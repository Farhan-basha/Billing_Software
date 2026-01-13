from django.shortcuts import render

# Create your views here.
"""
Authentication views for login, register, and user management
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from .models import User
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """
        Create new user and return tokens
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user login
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        """
        Authenticate user and return tokens
        """
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Login user
        login(request, user)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    API endpoint for user logout
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Logout user by blacklisting refresh token
        """
        try:
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response({
                    'success': False,
                    'message': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Invalid token or token already blacklisted'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to get and update user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Return current authenticated user
        """
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get current user profile
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """
        Update user profile
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    API endpoint to change user password
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request):
        """
        Change user password
        """
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Set new password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """
    API endpoint to list all users (admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter users based on role
        """
        queryset = super().get_queryset()
        
        # Only admins can see all users
        if not self.request.user.is_administrator:
            return queryset.filter(id=self.request.user.id)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Return list of users
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)