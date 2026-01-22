# QUICK_START.md

# Quick Start Guide - Billing Software Backend

Get the backend running in 5 minutes!

## Prerequisites
- Python 3.8+
- pip
- Git

## Quick Setup

### 1. Clone and Navigate
```bash
cd backend
```

### 2. Virtual Environment
```bash
# Create
python -m venv venv

# Activate
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (default settings work for development)
```

### 5. Database Setup
```bash
# Apply migrations
cd core
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Enter email, password, and details when prompted
```

### 6. Run Server
```bash
python manage.py runserver
```

Server is running at: **http://localhost:8000/**

## Common Commands

### Django Shell
```bash
python manage.py shell
```

### Admin Panel
```
http://localhost:8000/admin/
Login with superuser credentials created above
```

### Create Test Data
```bash
# In Django shell
from accounts.models import User
from customers.models import Customer
from invoices.models import Invoice

# Create customer
customer = Customer.objects.create(
    customer_name="John Doe",
    phone_number="1234567890",
    email="john@example.com"
)

# Create invoice
invoice = Invoice.objects.create(
    invoice_number="INV-001",
    customer=customer,
    customer_name="John Doe",
    customer_phone="1234567890",
    status="draft"
)
```

## API Testing

### Using cURL

#### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "full_name": "User Name"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
# Copy access token from response
```

#### Get Company Settings (Public)
```bash
curl http://localhost:8000/api/settings/company/public/
```

#### Get Company Settings (Admin)
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/settings/company/
```

#### Create Customer
```bash
curl -X POST http://localhost:8000/api/customers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Acme Corp",
    "phone_number": "1234567890",
    "email": "contact@acme.com",
    "address": "123 Business St",
    "city": "New York",
    "state": "NY",
    "pincode": "10001"
  }'
```

### Using Python Requests
```python
import requests

BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(f"{BASE_URL}/auth/login/", json={
    "email": "user@example.com",
    "password": "password123"
})
token = response.json()['data']['tokens']['access']

# Get customers
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/customers/", headers=headers)
customers = response.json()['data']
print(customers)
```

## File Locations

| File | Purpose |
|------|---------|
| `core/settings.py` | Django settings (use .env for config) |
| `core/urls.py` | Main URL routing |
| `accounts/` | User authentication |
| `customers/` | Customer management |
| `invoices/` | Invoice management |
| `settings_app/` | Company configuration |
| `common/` | Shared utilities |
| `.env` | Environment variables (local) |
| `logs/django.log` | Application logs |

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001  # Use different port
```

### Migration Errors
```bash
# Check status
python manage.py showmigrations

# Rollback and retry
python manage.py migrate zero
python manage.py migrate
```

### Import Errors
```bash
# Verify installation
python manage.py check

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Database Issues
```bash
# Reset database (development only!)
rm db.sqlite3
python manage.py migrate
```

## Next Steps

1. **Read Full Documentation**
   - [README.md](README.md) - Complete backend docs
   - [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Developer guide
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

2. **Create More Data**
   - Use admin panel at `/admin/`
   - Use API endpoints
   - Write test scripts

3. **Explore Features**
   - Test invoice creation
   - Try customer filtering
   - Check settings API

4. **Integration**
   - Connect frontend at `http://localhost:3000`
   - Test API endpoints
   - Verify CORS configuration

## Default Test Credentials

If using fixtures:
- **Email**: admin@example.com
- **Password**: admin123

## Useful Links

- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [JWT Docs](https://github.com/jpadilla/pyjwt)
- [PostgreSQL](https://www.postgresql.org/)

## Support

For issues:
1. Check `logs/django.log`
2. Run `python manage.py check`
3. Review error messages
4. Check [README.md](README.md) troubleshooting section

---

**That's it!** Your backend is ready. Happy coding! 🚀

