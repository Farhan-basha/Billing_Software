# DEVELOPMENT_GUIDE.md

# Backend Development Guide

This guide provides comprehensive information for developers working on the Billing Software backend.

## Project Architecture

### Separation of Concerns

The project is organized into Django apps, each responsible for a specific domain:

- **common/** - Shared utilities, base models, exceptions, permissions
- **accounts/** - User authentication and management
- **customers/** - Customer data management
- **invoices/** - Invoice generation and management
- **settings_app/** - Company configuration

### Request Flow

```
Request
  ↓
URLs (urls.py) → Views/ViewSets
  ↓
Serializers (Input Validation)
  ↓
Models (Database)
  ↓
Signals (Data Consistency)
  ↓
Response
```

## Code Standards

### Model Design

All models should follow these principles:

1. **Inherit from appropriate base class**
   ```python
   from common.models import TimeStampedModel
   
   class MyModel(TimeStampedModel):
       # Your fields
   ```

2. **Add descriptive docstrings**
   ```python
   class Invoice(TimeStampedModel):
       """
       Comprehensive invoice model with billing details.
       
       Attributes:
           invoice_number: Unique invoice identifier
           customer: Foreign key to Customer
           status: Current invoice status (draft, sent, paid, cancelled)
       """
   ```

3. **Use proper field definitions**
   ```python
   field_name = models.CharField(
       max_length=100,
       verbose_name='Display Name',
       help_text='Description for admin',
       db_index=True,  # For frequently queried fields
   )
   ```

4. **Override __str__ method**
   ```python
   def __str__(self):
       return f"Invoice {self.invoice_number}"
   ```

### View Design

Use class-based views with proper inheritance:

```python
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

class MyListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for MyModel list and create operations.
    
    Methods:
        GET: List all MyModel instances (paginated)
        POST: Create a new MyModel instance
    """
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['field1', 'field2']
    search_fields = ['searchable_field']
```

### Serializer Design

Create specialized serializers for different operations:

```python
class MyModelListSerializer(serializers.ModelSerializer):
    """Serializer for list view (minimal fields)"""
    class Meta:
        model = MyModel
        fields = ['id', 'name', 'created_at']

class MyModelDetailSerializer(serializers.ModelSerializer):
    """Serializer for detail view (all fields)"""
    class Meta:
        model = MyModel
        fields = '__all__'

class MyModelCreateSerializer(serializers.ModelSerializer):
    """Serializer for create operation (write fields)"""
    class Meta:
        model = MyModel
        fields = ['name', 'description']
    
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Name too short")
        return value
```

### Error Handling

Use custom exceptions from `common.exceptions`:

```python
from common.exceptions import ValidationException, ResourceNotFoundException

try:
    # Your code
except ValueError as e:
    raise ValidationException(f"Invalid value: {str(e)}")
except MyModel.DoesNotExist:
    raise ResourceNotFoundException("MyModel not found")
```

## Working with Signals

Signals maintain data consistency between related models:

### Adding a Signal

```python
# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=MyModel)
def update_related_model(sender, instance, created, **kwargs):
    """
    Update related model when MyModel is saved.
    
    Args:
        sender: The model class
        instance: The saved instance
        created: Boolean indicating if instance was created
    """
    if created:
        # Handle creation
        pass
    else:
        # Handle update
        pass
```

### Registering Signal

In `myapp/apps.py`:

```python
class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    
    def ready(self):
        import myapp.signals  # noqa
```

## Testing

### Unit Tests

```python
# tests.py or tests/test_models.py
from django.test import TestCase
from myapp.models import MyModel

class MyModelTestCase(TestCase):
    def setUp(self):
        self.model = MyModel.objects.create(name="Test")
    
    def test_model_creation(self):
        self.assertEqual(self.model.name, "Test")
    
    def test_model_str(self):
        self.assertEqual(str(self.model), "Test")
```

### API Tests

```python
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class MyModelAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_endpoint(self):
        response = self.client.get('/api/mymodel/')
        self.assertEqual(response.status_code, 200)
```

## Common Patterns

### Custom Manager

```python
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class MyModel(models.Model):
    is_active = models.BooleanField(default=True)
    objects = models.Manager()  # All objects
    published = PublishedManager()  # Only active
```

### Signal for Automatic Calculation

```python
@receiver(post_save, sender=InvoiceItem)
def calculate_invoice_total(sender, instance, **kwargs):
    invoice = instance.invoice
    total = invoice.items.aggregate(
        Sum('total_price')
    )['total_price__sum'] or 0
    invoice.total = total
    invoice.save()
```

### Pagination in Views

```python
from common.pagination import StandardPagination

class MyListView(generics.ListAPIView):
    pagination_class = StandardPagination
```

## Database Optimization

### Query Optimization

```python
# Bad: N+1 queries
invoices = Invoice.objects.all()
for invoice in invoices:
    print(invoice.customer.name)  # Additional query per invoice

# Good: Select related
invoices = Invoice.objects.select_related('customer')
for invoice in invoices:
    print(invoice.customer.name)  # No additional queries

# For reverse relationships
customers = Customer.objects.prefetch_related('invoices')
for customer in customers:
    print(customer.invoices.all())  # No additional queries
```

### Indexing

```python
class MyModel(models.Model):
    # Add index for frequently queried fields
    name = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Composite index for common filters
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
```

## Troubleshooting

### Migration Issues

```bash
# Show migration status
python manage.py showmigrations

# Roll back to specific migration
python manage.py migrate myapp 0002

# Create empty migration for data changes
python manage.py makemigrations myapp --empty --name fix_data
```

### Import Errors

```bash
# Check for circular imports
# Ensure apps are in INSTALLED_APPS
python manage.py check
```

### Debugging

```python
# Use Django shell
python manage.py shell

# Or with iPython (install: pip install django-extensions)
python manage.py shell_plus

# Print debug info
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Debug info: {variable}")
```

## Performance Tips

1. **Use select_related for ForeignKey**
2. **Use prefetch_related for ManyToMany and reverse ForeignKey**
3. **Add db_index=True to frequently filtered fields**
4. **Use only() and defer() to limit fields in queries**
5. **Use count() and exists() efficiently**
6. **Avoid N+1 query problems**
7. **Use pagination for large result sets**

## Security Tips

1. **Always validate input**
2. **Use DRF permission classes**
3. **Sanitize file uploads**
4. **Use environment variables for secrets**
5. **Implement rate limiting**
6. **Log security events**
7. **Validate CORS origins**

## Git Workflow

### Branch Naming

```
feature/feature-name      # New feature
bugfix/bug-name           # Bug fix
refactor/refactor-name    # Code refactoring
docs/doc-name             # Documentation
```

### Commit Message

```
Type: Brief description

Detailed explanation if needed

Fixes: #issue_number
```

## Documentation

### API Documentation

Keep docstrings updated:

```python
def get(self, request, *args, **kwargs):
    """
    Retrieve object details.
    
    Args:
        request: HTTP request object
        args: Variable length argument list
        kwargs: Arbitrary keyword arguments
    
    Returns:
        Response: JSON response with object data
        
    Raises:
        Http404: If object not found
    """
```

## Resources

- Django Documentation: https://docs.djangoproject.com/
- DRF Documentation: https://www.django-rest-framework.org/
- Celery: https://docs.celeryproject.io/
- PostgreSQL: https://www.postgresql.org/docs/

