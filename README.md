# AgroConnect - Agricultural Waste Trading Platform

AgroConnect is a Django-based web application that connects farmers and companies for agricultural waste trading. Farmers can list their crop residues (rice, corn, wheat, etc.) and companies can browse and purchase these waste products.

## 🌾 Features

### Authentication System
- **Farmer Registration & Login**: Farmers can register with farm details
- **Company Registration & Login**: Companies can register with business details
- **Role-based Access Control**: Different dashboards and permissions for farmers and companies
- **Django Admin Panel**: Admin can manage all users, products, and orders

### Farmer Features
- **Farmer Dashboard**: Overview of listings and orders
- **Add Waste Listings**: Create listings for crop waste (type, quantity, price, description)
- **Manage Listings**: View and manage own waste product listings
- **Order Management**: Accept or reject company orders
- **Order History**: View all past and current orders

### Company Features
- **Company Dashboard**: Overview of orders and quick actions
- **Browse Waste Products**: View all available agricultural waste
- **Advanced Filtering**: Filter by crop type (rice, corn, wheat, sugarcane, cotton)
- **Place Orders**: Order desired quantities of waste products
- **Order Tracking**: View order status and history

### Admin Features
- **User Management**: Manage farmers and companies
- **Product Management**: Oversee all waste listings
- **Order Monitoring**: Track all orders and transactions
- **System Analytics**: Monitor platform usage

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Django 4.2.7
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: SQLite (default, easily configurable to PostgreSQL/MySQL)
- **Authentication**: Django's built-in authentication system
- **Styling**: Bootstrap 5 with custom CSS

## 📋 Database Models

### User Profile System
- **UserProfile**: Extended user model with role (farmer/company)
- **FarmerProfile**: Farm-specific information (farm size, etc.)
- **CompanyProfile**: Company-specific information (name, registration number)

### Core Business Models
- **WasteProduct**: Crop waste listings with type, quantity, price, status
- **Order**: Purchase orders linking companies to waste products

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning)

### Step 1: Clone or Download Project
```bash
# If using Git
git clone <repository-url>
cd AgroConnect

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv agroconnect_env

# Activate virtual environment
# On Windows:
agroconnect_env\Scripts\activate
# On macOS/Linux:
source agroconnect_env/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
```

### Step 5: Collect Static Files
```bash
python manage.py collectstatic
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## 📱 Usage Guide

### For Farmers
1. **Register**: Go to "Register as Farmer" and fill in your details
2. **Login**: Use your credentials to access the farmer dashboard
3. **Add Waste**: Click "Add New" to list your agricultural waste
4. **Manage Orders**: Accept or reject orders from companies
5. **Track History**: View all your listings and order history

### For Companies
1. **Register**: Go to "Register as Company" and provide business details
2. **Login**: Access the company dashboard
3. **Browse Products**: View available waste products with filtering options
4. **Place Orders**: Select products and specify quantities needed
5. **Monitor Orders**: Track order status and communicate with farmers

### For Administrators
1. **Access Admin Panel**: Go to `/admin/` and login with superuser credentials
2. **Manage Users**: Add, edit, or remove farmer and company accounts
3. **Monitor Products**: Oversee all waste product listings
4. **Track Orders**: Monitor all transactions and order statuses

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root for production:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Database Configuration
For production, update `settings.py` to use PostgreSQL or MySQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'agroconnect_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📁 Project Structure

```
AgroConnect/
├── agroconnect/           # Main project settings
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── core/                 # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View functions and classes
│   ├── forms.py          # Django forms
│   ├── urls.py           # App URL patterns
│   └── admin.py          # Admin configuration
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── core/             # Core app templates
│   └── registration/     # Authentication templates
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
├── media/                # User uploaded files
├── db.sqlite3           # SQLite database
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## 🔒 Security Features

- **CSRF Protection**: All forms include CSRF tokens
- **User Authentication**: Secure login/logout system
- **Role-based Access**: Users can only access appropriate features
- **Input Validation**: Form validation prevents invalid data
- **SQL Injection Protection**: Django ORM prevents SQL injection
- **XSS Protection**: Template auto-escaping prevents XSS attacks

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Bootstrap 5**: Modern, clean interface
- **Interactive Elements**: Dynamic price calculation, form validation
- **User-friendly Navigation**: Intuitive menu and dashboard layout
- **Status Indicators**: Clear visual feedback for order and product status

## 🚀 Deployment

### For Production Deployment:

1. **Set Environment Variables**:
   - `SECRET_KEY`: Generate a secure secret key
   - `DEBUG=False`
   - `ALLOWED_HOSTS`: Add your domain

2. **Database**: Configure PostgreSQL or MySQL

3. **Static Files**: Configure static file serving

4. **Web Server**: Use Gunicorn + Nginx or similar

5. **Security**: Enable HTTPS, set security headers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For support or questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Future Enhancements

- **Payment Integration**: Online payment processing
- **Real-time Chat**: Communication between farmers and companies
- **Mobile App**: Native mobile applications
- **Analytics Dashboard**: Advanced reporting and analytics
- **Geolocation**: Location-based product search
- **Rating System**: User ratings and reviews
- **Notification System**: Email/SMS notifications for orders

---

**AgroConnect** - Bridging the gap between agricultural waste and industrial needs. 🌾✨