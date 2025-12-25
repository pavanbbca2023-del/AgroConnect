# AgroConnect API Documentation

## Overview
This document provides detailed technical information about AgroConnect's internal APIs and endpoints for developers working on the platform.

## Authentication
All authenticated endpoints require a valid Django session. The platform uses Django's built-in authentication system.

## Response Formats
All API responses are in JSON format with the following structure:

```json
{
    "success": boolean,
    "message": string,
    "data": object,
    "error": string (if applicable)
}
```

## Session Management APIs

### Get Active Sessions
**Endpoint:** `GET /api/sessions/`
**Authentication:** Required
**Description:** Retrieve all active sessions for the current user

**Response:**
```json
{
    "success": true,
    "sessions": [
        {
            "session_id": "abc12345",
            "login_time": "2024-12-24T10:30:00Z",
            "is_current": true
        }
    ],
    "total_sessions": 1
}
```

### Terminate Session
**Endpoint:** `POST /api/sessions/terminate/`
**Authentication:** Required
**Description:** Terminate a specific user session

**Request Body:**
```json
{
    "session_key": "session_key_to_terminate"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Session terminated successfully"
}
```

## View-Based Endpoints

### Home Page
**Endpoint:** `GET /`
**Authentication:** Not required
**Description:** Landing page with platform overview

### User Registration

#### Farmer Registration
**Endpoint:** `GET/POST /register/farmer/`
**Authentication:** Not required
**Description:** Register a new farmer account

**POST Data:**
```json
{
    "username": "farmer1",
    "email": "farmer@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password1": "securepassword",
    "password2": "securepassword",
    "phone": "+1234567890",
    "address": "Farm Address",
    "farm_size": "10.5"
}
```

#### Company Registration
**Endpoint:** `GET/POST /register/company/`
**Authentication:** Not required
**Description:** Register a new company account

**POST Data:**
```json
{
    "username": "company1",
    "email": "company@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "password1": "securepassword",
    "password2": "securepassword",
    "phone": "+0987654321",
    "address": "Company Address",
    "company_name": "ABC Company Ltd",
    "registration_number": "REG123456"
}
```

### Authentication

#### Login
**Endpoint:** `POST /login/`
**Authentication:** Not required
**Description:** User login with concurrent session support

**POST Data:**
```json
{
    "username": "user123",
    "password": "userpassword"
}
```

#### Logout
**Endpoint:** `POST /logout/`
**Authentication:** Required
**Description:** User logout

### Dashboard Access

#### Role-Based Dashboard
**Endpoint:** `GET /dashboard/`
**Authentication:** Required
**Description:** Redirects to appropriate dashboard based on user role
- Farmers → Farmer Dashboard
- Companies → Company Dashboard  
- Admins → Admin Dashboard

### Waste Product Management

#### Browse Waste Products
**Endpoint:** `GET /waste/`
**Authentication:** Required (Company role)
**Description:** Browse available waste products with filtering

**Query Parameters:**
- `crop_type`: Filter by crop type (rice, wheat, sugarcane, cotton, other)

#### Waste Product Detail
**Endpoint:** `GET /waste/<int:pk>/`
**Authentication:** Required
**Description:** View detailed information about a specific waste product

#### Add Waste Product
**Endpoint:** `GET/POST /waste/add/`
**Authentication:** Required (Farmer role)
**Description:** Create a new waste product listing

**POST Data (multipart/form-data):**
```json
{
    "crop_name": "rice",
    "quantity": "25.5",
    "farmer_price_per_ton": "5000.00",
    "location": "Punjab, India",
    "description": "High quality rice residue",
    "photo": "file_upload"
}
```

### Order Management

#### Place Order
**Endpoint:** `GET/POST /order/<int:waste_id>/`
**Authentication:** Required (Company role)
**Description:** Place an order for a waste product

**POST Data:**
```json
{
    "quantity_ordered": "10.0",
    "company_price_per_ton": "4500.00",
    "notes": "Urgent delivery required"
}
```

#### Update Order Status
**Endpoint:** `POST /order/<int:order_id>/<str:status>/`
**Authentication:** Required (Farmer role)
**Description:** Update order status (accept/reject)

**Valid Status Values:**
- `accepted`: Accept the order
- `rejected`: Reject the order

### Profile Management

#### View Profile
**Endpoint:** `GET /profile/`
**Authentication:** Required
**Description:** View user profile information

#### Edit Profile
**Endpoint:** `GET/POST /profile/edit/`
**Authentication:** Required
**Description:** Update user profile information

### Price Bargaining

#### Create Bargain Request
**Endpoint:** `GET/POST /bargain/create/<int:waste_id>/`
**Authentication:** Required (Farmer role)
**Description:** Create a price bargain request

**POST Data:**
```json
{
    "proposed_price": "5500.00",
    "message": "Requesting higher price due to quality"
}
```

### Admin Endpoints

#### Admin Orders
**Endpoint:** `GET /admin-orders/`
**Authentication:** Required (Admin role)
**Description:** View all orders for admin management

**Query Parameters:**
- `status`: Filter by order status

#### Admin Order Approval
**Endpoint:** `GET/POST /admin-order/<int:order_id>/approve/`
**Authentication:** Required (Admin role)
**Description:** Approve or manage specific order

**POST Data:**
```json
{
    "action": "send_to_farmer|final_approve|reject",
    "admin_notes": "Order approved for processing"
}
```

#### Admin Bargains
**Endpoint:** `GET /bargains/`
**Authentication:** Required (Admin role)
**Description:** View all price bargain requests

#### Respond to Bargain
**Endpoint:** `GET/POST /bargain/<int:bargain_id>/respond/`
**Authentication:** Required (Admin role)
**Description:** Respond to farmer bargain request

**POST Data:**
```json
{
    "action": "accept|reject|counter",
    "admin_message": "Price approved",
    "counter_price": "5200.00"
}
```

#### View Prices
**Endpoint:** `GET /price-management/view/`
**Authentication:** Required (Admin role)
**Description:** View all waste product prices

**Query Parameters:**
- `crop`: Filter by crop type
- `status`: Filter by product status

#### Order Summary
**Endpoint:** `GET /order-summary/`
**Authentication:** Required (Admin role)
**Description:** View order statistics and summary

## Error Handling

### Common HTTP Status Codes
- `200`: Success
- `302`: Redirect (successful form submission)
- `400`: Bad Request (form validation errors)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Internal Server Error

### Error Response Format
```json
{
    "success": false,
    "error": "Error description",
    "details": {
        "field_name": ["Field-specific error messages"]
    }
}
```

## Middleware

### ConcurrentSessionMiddleware
Handles concurrent user sessions and session tracking.

### SessionSecurityMiddleware
Adds security headers and session metadata.

## Form Validation

### UserRegistrationForm
**Validation Rules:**
- Email must be unique
- Phone: 10-15 digits, optional + prefix
- Registration number: 6-20 alphanumeric uppercase (companies)

### WasteProductForm
**Validation Rules:**
- Quantity: Minimum 0.01 tons
- Price: Minimum ₹0.01 per ton
- Photo: Image files only

### OrderForm
**Validation Rules:**
- Quantity cannot exceed available stock
- Price: Minimum ₹0.01 per ton

## Database Relationships

### User Hierarchy
```
User (Django Auth)
└── UserProfile (role: farmer/company)
    ├── FarmerProfile (if farmer)
    └── CompanyProfile (if company)
```

### Product-Order Flow
```
FarmerProfile
└── WasteProduct
    ├── Order (from CompanyProfile)
    └── PriceBargain (negotiation)
```

## Security Considerations

### CSRF Protection
All POST requests require CSRF tokens. Forms automatically include CSRF tokens when using Django templates.

### Permission Checks
- Role-based access control on all views
- Object-level permissions for orders and products
- Admin-only access for management functions

### Input Validation
- Server-side validation on all forms
- File upload restrictions (images only)
- SQL injection prevention through ORM

## Rate Limiting
Currently not implemented. Consider adding for production:
- Login attempts: 5 per minute
- Order creation: 10 per hour
- API calls: 100 per minute

## Caching Strategy
- Session data cached for 1 hour
- Market prices cached for performance
- Static files cached with versioning

## Logging
All significant actions are logged:
- User registration and login
- Order creation and status changes
- Admin actions
- Error conditions

Log files location: `logs/agroconnect.log`

## Testing Endpoints

### Test Data Creation
For development and testing, you can create test users:

```python
# Create test farmer
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from core.models import UserProfile, FarmerProfile
>>> user = User.objects.create_user('testfarmer', 'farmer@test.com', 'password')
>>> profile = UserProfile.objects.create(user=user, role='farmer', phone='1234567890', address='Test Address')
>>> FarmerProfile.objects.create(user_profile=profile, farm_size=10.0)
```

### API Testing Tools
- **Postman**: For API endpoint testing
- **Django Test Client**: For unit testing
- **Browser DevTools**: For frontend debugging

---

*This API documentation is for internal development use. For public API documentation, refer to the main project documentation.*