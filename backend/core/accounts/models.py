from django.db import models

# Create your models here.
"""
User authentication models
Custom user model with role-based access control
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with email and password
        """
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with admin privileges
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email as username
    Supports both admin and regular user roles
    """
    
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('user', 'Regular User'),
    )
    
    email = models.EmailField(
        max_length=255,
        unique=True,
        validators=[EmailValidator()],
        db_index=True,
        verbose_name='Email Address'
    )
    
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Full Name'
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Phone Number'
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        db_index=True,
        verbose_name='User Role'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Status'
    )
    
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Staff Status'
    )
    
    is_admin = models.BooleanField(
        default=False,
        verbose_name='Admin Status'
    )
    
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date Joined'
    )
    
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Last Login'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """
        Return full name or email if name not set
        """
        return self.full_name if self.full_name else self.email
    
    def get_short_name(self):
        """
        Return email as short name
        """
        return self.email
    
    @property
    def is_administrator(self):
        """
        Check if user has admin role
        """
        return self.role == 'admin' or self.is_admin
    
    def has_perm(self, perm, obj=None):
        """
        Check if user has specific permission
        """
        return self.is_active and (self.is_superuser or self.is_admin)
    
    def has_module_perms(self, app_label):
        """
        Check if user has permissions to view app
        """
        return self.is_active and (self.is_staff or self.is_admin)


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='User'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Address'
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='City'
    )
    
    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='State'
    )
    
    pincode = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='PIN Code'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.email}'s Profile"