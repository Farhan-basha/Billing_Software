"""
Authentication serializers for user registration and login
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data
    """
    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'address', 'city', 'state', 'pincode']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user model with profile data
    """
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone_number', 
            'role', 'is_active', 'date_joined', 'profile'
        ]
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 
            'full_name', 'phone_number', 'role'
        ]
    
    def validate(self, attrs):
        """
        Validate password confirmation
        """
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password': 'Passwords do not match'
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create new user with hashed password
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    role = serializers.ChoiceField(
        choices=['admin', 'user'],
        required=False,
        help_text='Login as admin or regular user'
    )
    
    def validate(self, attrs):
        """
        Validate user credentials
        """
        email = attrs.get('email')
        password = attrs.get('password')
        role_filter = attrs.get('role')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError({
                    'detail': 'Invalid email or password'
                })
            
            if not user.is_active:
                raise serializers.ValidationError({
                    'detail': 'User account is disabled'
                })
            
            # Check role if specified
            if role_filter and user.role != role_filter:
                raise serializers.ValidationError({
                    'detail': f'Invalid credentials for {role_filter} login'
                })
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError({
                'detail': 'Email and password are required'
            })


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        min_length=8
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        Validate password change
        """
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError({
                'new_password': 'Passwords do not match'
            })
        return attrs
    
    def validate_old_password(self, value):
        """
        Validate old password is correct
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value