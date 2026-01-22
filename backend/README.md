# Billing Software - Backend API

A comprehensive Django REST Framework-based billing system for managing invoices, customers, and company settings.

## Project Structure

```
backend/
├── core/                          # Django project configuration
│   ├── settings.py               # Main settings file (uses environment variables)
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py                   # Production WSGI entry point
│   └── asgi.py                   # ASGI for async support
├── common/                        # Shared utilities and base classes
│   ├── models.py                 # Base models (TimeStampedModel, SoftDeleteModel)
│   ├── exceptions.py             # Custom exception classes
│   ├── permissions.py            # Custom permission classes
│   ├── pagination.py             # Custom pagination classes
│   └── handlers.py               # Exception handlers
├── accounts/                      # User authentication & management
│   ├── models.py                 # Custom User model with JWT
│   ├── views.py                  # Authentication views (login, register, logout)
│   ├── serializers.py            # User serializers
│   └── urls.py                   # Account endpoints
├── customers/                     # Customer management
│   ├── models.py                 # Customer model
│   ├── views.py                  # CRUD operations for customers
│   ├── serializers.py            # Customer serializers
│   ├── admin.py                  # Django admin configuration
│   └── urls.py                   # Customer endpoints
├── invoices/                      # Invoice & billing management
│   ├── models.py                 # Invoice and InvoiceItem models
│   ├── views.py                  # Invoice CRUD and reporting
│   ├── serializers.py            # Invoice serializers
│   ├── signals.py                # Data consistency signals
│   ├── admin.py                  # Django admin configuration
│   └── urls.py                   # Invoice endpoints
├── settings_app/                 # Company configuration
│   ├── models.py                 # CompanySettings singleton model
│   ├── views.py                  # Settings management views
│   ├── serializers.py            # Settings serializers
│   ├── admin.py                  # Django admin configuration
│   └── urls.py                   # Settings endpoints
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (local)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file
└── README.md                     # This file
```

## Features

### 🔐 Authentication
- Email-based user authentication
- JWT token-based API authentication
- Role-based access control (Admin/User)
- Custom User model with enhanced fields

### 👥 Customer Management
- Complete CRUD operations
- Customer search and filtering
- Phone number validation (regex)
- GST/Tax ID management
- Automatic invoice count and amount tracking

### 📄 Invoice Management
- Invoice generation with unique numbering
- Line items (InvoiceItem model)
- Automatic total calculations (subtotal, tax, grand total)
- Invoice status workflow (Draft → Sent → Paid → Cancelled)
- Historical data caching (customer name, phone)
- Invoice print/PDF generation support
- Dashboard with summary statistics

### ⚙️ Company Settings
- Singleton model for company configuration
- Tax rate management
- Invoice numbering configuration
- Company branding (logo, details)
- Payment terms and conditions
- Bank account details storage
- Admin-only modification

### 🔄 Data Consistency
- Signal handlers for automatic calculations
- Denormalized field synchronization
- Invoice total auto-calculation
- Customer statistics auto-update

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (recommended) or SQLite (development)
- pip

### Setup

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# Debug mode (False in production)
DEBUG=True

# Secret key for Django
SECRET_KEY=your-secret-key-here

# Allowed hosts
ALLOWED_HOSTS=localhost,127.0.0.1

# Database configuration
DB_ENGINE=django.db.backends.postgresql  # or sqlite3
DB_NAME=billing_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# CORS settings
CORS_ALLOWED_ORIGINS=http://localhost:3000

# API settings
API_PAGINATION_SIZE=20
API_THROTTLE_RATE=100/hour

# JWT token lifetimes
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=5
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/django.log
```

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication
All endpoints (except auth and public settings) require JWT token in header:
```
Authorization: Bearer <access_token>
```

### Endpoints

#### 🔑 Authentication (`/api/auth/`)
- `POST /register` - Register new user
- `POST /login` - Login user
- `POST /logout` - Logout user
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `POST /change-password` - Change password
- `POST /token/refresh` - Refresh JWT token

#### 👥 Customers (`/api/customers/`)
- `GET /` - List customers (paginated)
- `POST /` - Create customer
- `GET /{id}/` - Retrieve customer
- `PUT /{id}/` - Update customer
- `PATCH /{id}/` - Partial update
- `DELETE /{id}/` - Delete customer
- `GET /search/` - Search customers
- `GET /{id}/stats/` - Get customer statistics

#### 📄 Invoices (`/api/invoices/`)
- `GET /` - List invoices (paginated, filterable)
- `POST /` - Create invoice with items
- `GET /{id}/` - Retrieve invoice
- `PUT /{id}/` - Update invoice
- `PATCH /{id}/` - Partial update
- `DELETE /{id}/` - Delete invoice
- `GET /{id}/print/` - Get printable format
- `POST /{id}/status/` - Update invoice status
- `GET /dashboard/` - Get dashboard statistics
- `POST /items/{item_id}/` - Update invoice item

#### ⚙️ Settings (`/api/settings/`)
- `GET /company/` - Get company settings (authenticated)
- `PUT /company/` - Update settings (admin only)
- `PATCH /company/` - Partial update (admin only)
- `GET /company/public/` - Get public settings (no auth required)

## API Response Format

All API responses follow a standardized format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "count": 10,
  "summary": { ... }  // Optional
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": "error_code",
    "status_code": 400,
    "details": { ... }  // Optional
  }
}
```

### Paginated Response
```json
{
  "success": true,
  "pagination": {
    "count": 100,
    "next": "http://...",
    "previous": "http://...",
    "current_page": 1,
    "total_pages": 5,
    "page_size": 20
  },
  "data": [ ... ]
}
```

## Database Models

### User
- Custom user model with email as username
- Roles: admin, user
- Profile extended data (address, city, etc.)

### Customer
- Customer information and contact details
- GST/Tax identification
- Address components (city, state, pincode)
- Denormalized totals (invoices count, total amount)

### Invoice
- Invoice header information
- References customer
- Cached customer name/phone for historical accuracy
- Status tracking
- Tax and discount calculations
- Automatic grand total calculation

### InvoiceItem
- Line items in an invoice
- Item name, unit, quantity, rate
- Automatic total calculation
- Decimal precision for monetary values

### CompanySettings
- Singleton model (max 1 record)
- Company branding and contact info
- Invoice configuration
- Tax rate defaults
- Bank and payment details

## Testing

Run tests with:
```bash
pytest
# With coverage
pytest --cov=.
```

## Logging

Logs are written to:
- Console (development)
- File: `logs/django.log` (production)

Log level controlled via `LOG_LEVEL` environment variable.

## Security

### Implemented
✅ Environment variable configuration  
✅ SECRET_KEY protection  
✅ CORS configuration  
✅ JWT authentication  
✅ Permission classes  
✅ Secure password hashing  

### Recommended
- Use HTTPS in production
- Implement rate limiting
- Add CSRF protection for frontend
- Use strong SECRET_KEY
- Configure secure database

## Performance

### Features
- Database query optimization (select_related, prefetch_related)
- Pagination for large result sets
- Indexing on frequently queried fields
- Signal handlers for automatic calculations

### Recommendations
- Add Redis caching for frequently accessed data
- Implement Celery for async tasks
- Use database read replicas
- Monitor with Prometheus/Grafana

## Deployment

### Using Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 core.wsgi
```

### Docker
```bash
docker build -t billing-api .
docker run -p 8000:8000 billing-api
```

## Development Guidelines

### Code Style
- Follow PEP 8
- Use Black for formatting
- Use flake8 for linting

### Naming Conventions
- Models: PascalCase
- Fields: snake_case
- Views: DescriptiveNameView
- Serializers: ModelNameSerializer

### Adding New Features
1. Create models with proper fields
2. Create serializers for API
3. Implement views/viewsets
4. Add URL patterns
5. Create tests
6. Update documentation

## Troubleshooting

### Database Errors
```bash
# Reset migrations (development only)
python manage.py migrate zero

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

### Import Errors
Ensure `common` app is in `INSTALLED_APPS` in settings.py

### Permission Denied
Check user role and permissions. Ensure JWT token is valid.

## Support

For issues or questions:
1. Check existing documentation
2. Review error logs in `logs/django.log`
3. Check Django admin panel
4. Run `python manage.py check` for system checks

## License

[Add your license here]

## Changelog

### Version 1.0 (January 2026)
- Initial release
- Core features implemented
- API documentation
- Security hardening
