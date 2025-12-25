# AgroConnect - Agricultural Waste Trading Platform

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Installation & Setup](#installation--setup)
5. [Project Structure](#project-structure)
6. [Database Models](#database-models)
7. [User Roles & Permissions](#user-roles--permissions)
8. [API Endpoints](#api-endpoints)
9. [Usage Guide](#usage-guide)
10. [Security Features](#security-features)
11. [Deployment](#deployment)
12. [Contributing](#contributing)

## Project Overview

AgroConnect is a web-based platform that connects farmers with companies for agricultural waste trading. The platform enables farmers to sell their crop residues and companies to purchase quality agricultural waste for their business needs, promoting sustainable farming practices and reducing waste burning.

### Key Objectives
- **Environmental Impact**: Reduce agricultural waste burning
- **Economic Benefit**: Provide additional income to farmers
- **Supply Chain**: Connect waste producers with consumers
- **Sustainability**: Promote circular economy in agriculture

## Features

### Core Features
- **User Registration & Authentication**
  - Separate registration for farmers and companies
  - Role-based access control
  - Profile management with photo upload

- **Waste Product Management**
  - Farmers can list agricultural waste products
  - Photo upload for products
  - Quantity and pricing management
  - Location-based listings

- **Order Management System**
  - Companies can browse and order waste products
  - Multi-stage order approval process
  - Order tracking and status updates

- **Price Bargaining System**
  - Farmers can negotiate prices with admin
  - Counter-offer functionality
  - Transparent pricing mechanism

- **Admin Dashboard**
  - Comprehensive order management
  - Price monitoring and control
  - User and product oversight

### Advanced Features
- **Concurrent Session Management**
- **Real-time Market Prices**
- **Responsive Design**
- **Search and Filter Functionality**
- **Order Status Tracking**

## Technology Stack

### Backend
- **Framework**: Django 4.2+
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: Django Auth System
- **File Storage**: Django File Handling

### Frontend
- **Template Engine**: Django Templates
- **CSS Framework**: Bootstrap 5
- **Icons**: FontAwesome
- **JavaScript**: Vanilla JS for interactions

### Additional Libraries
- **django-crispy-forms**: Form styling
- **crispy-bootstrap5**: Bootstrap 5 integration
- **python-decouple**: Environment configuration
- **Pillow**: Image processing

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/pavanbbca2023-del/AgroConnect.git
   cd AgroConnect
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env file with your settings
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access Application**
   - Main Site: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Project Structure

```
AgroConnect/
├── agroconnect/           # Main project directory
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── core/                 # Main application
│   ├── migrations/       # Database migrations
│   ├── templatetags/     # Custom template tags
│   ├── __init__.py
│   ├── admin.py         # Admin interface configuration
│   ├── apps.py          # App configuration
│   ├── auth_views.py    # Authentication views
│   ├── forms.py         # Django forms
│   ├── middleware.py    # Custom middleware
│   ├── models.py        # Database models
│   ├── urls.py          # App URL patterns
│   └── views.py         # View functions
├── templates/           # HTML templates
│   ├── core/           # App-specific templates
│   ├── registration/   # Auth templates
│   └── base.html       # Base template
├── static/             # Static files
│   ├── css/           # Stylesheets
│   └── js/            # JavaScript files
├── media/             # User uploaded files
├── logs/              # Application logs
├── .env               # Environment variables
├── .gitignore         # Git ignore rules
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
└── README.md          # Project README
```

## Database Models

### User Profile System
```python
# UserProfile - Base profile for all users
- user: OneToOneField(User)
- role: CharField (farmer/company)
- phone: CharField
- address: TextField
- profile_photo: ImageField
- created_at: DateTimeField

# FarmerProfile - Extended profile for farmers
- user_profile: OneToOneField(UserProfile)
- farm_size: DecimalField

# CompanyProfile - Extended profile for companies
- user_profile: OneToOneField(UserProfile)
- company_name: CharField
- registration_number: CharField (unique)
```

### Product & Order System
```python
# WasteProduct - Agricultural waste listings
- farmer: ForeignKey(FarmerProfile)
- crop_name: CharField (choices)
- quantity: DecimalField
- admin_price_per_ton: DecimalField
- farmer_price_per_ton: DecimalField (optional)
- location: CharField
- description: TextField
- photo: ImageField
- status: CharField (available/sold/reserved)
- created_at: DateTimeField

# Order - Purchase orders from companies
- company: ForeignKey(CompanyProfile)
- waste_product: ForeignKey(WasteProduct)
- quantity_ordered: DecimalField
- company_price_per_ton: DecimalField
- total_price: DecimalField
- status: CharField (multiple stages)
- notes: TextField
- admin_notes: TextField
- created_at: DateTimeField

# PriceBargain - Price negotiation system
- waste_product: ForeignKey(WasteProduct)
- farmer_proposed_price: DecimalField
- admin_counter_price: DecimalField (optional)
- farmer_message: TextField
- admin_message: TextField
- status: CharField (pending/accepted/rejected)
- created_at: DateTimeField
```

## User Roles & Permissions

### Farmer Role
**Permissions:**
- Create and manage waste product listings
- View and respond to orders
- Negotiate prices through bargaining system
- Update profile information
- View market prices

**Dashboard Features:**
- Waste product management
- Order notifications and responses
- Bargain request tracking
- Market price monitoring

### Company Role
**Permissions:**
- Browse available waste products
- Place orders for waste products
- View order history and status
- Update profile information
- Filter and search products

**Dashboard Features:**
- Product browsing interface
- Order management system
- Company statistics
- Order tracking

### Admin Role
**Permissions:**
- Full system access
- User management
- Order approval workflow
- Price management
- Bargain request handling
- System monitoring

**Dashboard Features:**
- Comprehensive order management
- User oversight
- Price control system
- Bargain negotiation interface
- System statistics

## API Endpoints

### Authentication URLs
```
/                          # Home page
/login/                    # User login
/logout/                   # User logout
/register/farmer/          # Farmer registration
/register/company/         # Company registration
```

### Dashboard URLs
```
/dashboard/                # Role-based dashboard redirect
/admin-dashboard/          # Admin dashboard
```

### Product Management URLs
```
/waste/                    # Browse waste products
/waste/<id>/               # Product detail view
/waste/add/                # Add new waste product (farmers)
```

### Order Management URLs
```
/order/<waste_id>/         # Place order
/order/<order_id>/<status>/ # Update order status
/admin-orders/             # Admin order management
/admin-order/<id>/approve/ # Admin order approval
/order-summary/            # Order statistics
```

### Profile Management URLs
```
/profile/                  # View profile
/profile/edit/             # Edit profile
```

### Bargaining System URLs
```
/bargain/create/<waste_id>/ # Create bargain request
/bargains/                 # Admin bargain management
/bargain/<id>/respond/     # Admin bargain response
```

### Price Management URLs
```
/price-management/view/    # View all prices (admin)
```

### Session Management APIs
```
/api/sessions/             # Get active sessions
/api/sessions/terminate/   # Terminate session
```

## Usage Guide

### For Farmers

1. **Registration**
   - Visit `/register/farmer/`
   - Fill in personal details and farm information
   - Upload profile photo (optional)

2. **Adding Waste Products**
   - Navigate to dashboard
   - Click "Add Waste Product"
   - Fill in crop details, quantity, location
   - Upload product photo
   - Set optional pricing

3. **Managing Orders**
   - View incoming orders in dashboard
   - Accept or reject orders from companies
   - Track order status through completion

4. **Price Negotiation**
   - Create bargain requests for better prices
   - Negotiate with admin through messaging system

### For Companies

1. **Registration**
   - Visit `/register/company/`
   - Provide company details and registration number
   - Complete profile setup

2. **Browsing Products**
   - Use `/waste/` to browse available products
   - Filter by crop type and location
   - View detailed product information

3. **Placing Orders**
   - Select desired waste product
   - Specify quantity and offer price
   - Add notes for special requirements
   - Submit order for admin review

4. **Order Tracking**
   - Monitor order status in dashboard
   - Receive notifications on status changes

### For Administrators

1. **Order Management**
   - Review incoming orders
   - Send orders to farmers for approval
   - Provide final approval after farmer acceptance
   - Add administrative notes

2. **Price Management**
   - Monitor market prices
   - View all product pricing
   - Handle price bargain requests

3. **User Oversight**
   - Manage user accounts
   - Monitor system activity
   - Handle disputes and issues

## Security Features

### Authentication & Authorization
- Django's built-in authentication system
- Role-based access control
- Session management with security headers
- CSRF protection on all forms

### Data Validation
- Server-side form validation
- Input sanitization
- File upload restrictions
- Phone number and email validation

### Session Security
- Concurrent session management
- Session timeout configuration
- Secure session cookies
- Session activity tracking

### Production Security
- Environment-based configuration
- Secure headers (HSTS, XSS protection)
- SSL/HTTPS enforcement
- Database security best practices

## Deployment

### Environment Setup
1. **Production Settings**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

2. **Database Configuration**
   - Use PostgreSQL for production
   - Configure connection pooling
   - Set up regular backups

3. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

### Deployment Options

#### Option 1: Traditional Server (Ubuntu/CentOS)
1. Install Python, PostgreSQL, Nginx
2. Set up virtual environment
3. Configure Gunicorn/uWSGI
4. Set up Nginx reverse proxy
5. Configure SSL certificates

#### Option 2: Cloud Platforms
- **Heroku**: Easy deployment with buildpacks
- **AWS**: EC2 + RDS + S3 for scalability
- **DigitalOcean**: App Platform or Droplets
- **Railway**: Simple deployment platform

#### Option 3: Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "agroconnect.wsgi:application"]
```

## Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Make changes and test thoroughly
4. Commit changes (`git commit -am 'Add new feature'`)
5. Push to branch (`git push origin feature/new-feature`)
6. Create Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for complex functions
- Write unit tests for new features
- Update documentation for changes

### Testing
```bash
# Run tests
python manage.py test

# Check code coverage
coverage run manage.py test
coverage report
```

## Support & Maintenance

### Logging
- Application logs stored in `logs/agroconnect.log`
- Error tracking and monitoring
- Performance metrics collection

### Backup Strategy
- Regular database backups
- Media file backups
- Configuration backups
- Automated backup scheduling

### Monitoring
- Server resource monitoring
- Application performance tracking
- User activity analytics
- Error rate monitoring

---

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For support or questions, please contact:
- **Developer**: Pavan
- **Email**: [Your Email]
- **GitHub**: https://github.com/pavanbbca2023-del/AgroConnect

---

*Last Updated: December 2024*