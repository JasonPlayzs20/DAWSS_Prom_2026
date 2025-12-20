# 🚀 Prom Management System - Complete Setup Guide

## 📁 Final Project Structure

```
DAWSS_fastAPI/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── dependencies/
│   │   │   ├── __init__.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── seating.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── student.py
│   │   │   ├── admin.py
│   │   │   ├── payment.py
│   │   │   └── pages.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── addUser.py        
│   │       ├── removeUser.py    
│   │       └── modCredentials.py
│   ├── static/                   
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── main.js
│   │       ├── auth.js
│   │       └── student.js
│   └── templates/
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       └── student_dashboard.html
├── init_db.py
├── run.py
├── requirements.txt
└── README.md
```

## 📋 Step-by-Step Setup

### 1. Create Missing Directories

```bash
# Create static directories
mkdir -p app/static/css
mkdir -p app/static/js

# Create templates directory
mkdir app/templates
```

### 2. Create All __init__.py Files

```bash
# macOS/Linux
touch app/__init__.py
touch app/core/__init__.py
touch app/core/models/__init__.py
touch app/core/routers/__init__.py
touch app/core/schemas/__init__.py
touch app/core/utils/__init__.py
touch app/core/dependencies/__init__.py

# Windows PowerShell
New-Item -ItemType File -Path app/__init__.py -Force
New-Item -ItemType File -Path app/core/__init__.py -Force
New-Item -ItemType File -Path app/core/models/__init__.py -Force
New-Item -ItemType File -Path app/core/routers/__init__.py -Force
New-Item -ItemType File -Path app/core/schemas/__init__.py -Force
New-Item -ItemType File -Path app/core/utils/__init__.py -Force
New-Item -ItemType File -Path app/core/dependencies/__init__.py -Force
```

### 3. Install Dependencies

```bash
# Make sure you're in your virtual environment
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python init_db.py
```

This creates:
- ✅ Admin account: `admin@prom.com` / `admin123`
- ✅ Student account: `student@school.com` / `student123`
- ✅ 10 tables with 8 seats each (80 total seats)

### 5. Start the Server

```bash
python run.py
```

## 🔗 Available URLs

### Frontend Pages
- **Home**: http://localhost:8000/
- **Login**: http://localhost:8000/login
- **Register**: http://localhost:8000/register
- **Student Dashboard**: http://localhost:8000/student/dashboard
- **Admin Dashboard**: http://localhost:8000/admin/dashboard

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints
- **Auth**: http://localhost:8000/api/auth/*
- **Student**: http://localhost:8000/api/student/*
- **Admin**: http://localhost:8000/api/admin/*
- **Payment**: http://localhost:8000/api/payment/*

## 🛠️ Using Utility Scripts

### Add a User

```bash
# Interactive mode
python -m app.core.utils.addUser

# Or programmatically in Python
from app.core.utils.addUser import add_user

add_user(
    email="newstudent@school.com",
    password="password123",
    full_name="Jane Smith",
    role="student",
    student_id="STU002"
)
```

### Remove a User

```bash
# Interactive mode
python -m app.core.utils.removeUser

# Or programmatically
from app.core.utils.removeUser import remove_user

remove_user("student@school.com", by_email=True)
```

### Modify User Credentials

```bash
# Interactive mode
python -m app.core.utils.modCredentials

# Or programmatically
from app.core.utils.modCredentials import modify_user, reset_password

# Reset password
reset_password("student@school.com", "newpassword123")

# Toggle active status
from app.core.utils.modCredentials import toggle_active_status
toggle_active_status("student@school.com")
```

## 🎯 Testing the System

### 1. Test Registration
1. Go to http://localhost:8000/register
2. Fill in the form with your details
3. Click "Create Account"
4. You'll be redirected to login

### 2. Test Student Login
1. Go to http://localhost:8000/login
2. Login with: `student@school.com` / `student123`
3. You'll be redirected to student dashboard
4. You should see your booking status (no booking yet)

### 3. Test Admin Login
1. Logout (if logged in)
2. Login with: `admin@prom.com` / `admin123`
3. You'll be redirected to admin dashboard
4. Use API docs at `/docs` to test admin endpoints

### 4. Test API Endpoints
1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Login to get a token
4. Try various endpoints

## 🎨 Customization

### Change Ticket Price
Edit `app/core/routers/student.py`:
```python
ticket_price = 50.00  # Change this value
```

### Change Event Details
Edit `app/templates/index.html` and `student_dashboard.html`:
```html
<div><strong>Date:</strong> June 15, 2025</div>  <!-- Edit here -->
<div><strong>Time:</strong> 7:00 PM - 12:00 AM</div>
<div><strong>Venue:</strong> Grand Ballroom</div>
```

### Customize Colors
Edit `app/static/css/style.css`:
```css
:root {
    --primary-color: #6366f1;  /* Change colors here */
    --secondary-color: #8b5cf6;
    /* ... */
}
```

## 🔐 Security for Production

Before deploying to production:

1. **Change Secret Key** in `app/core/utils/auth.py`:
```python
SECRET_KEY = "your-very-secure-secret-key-here"
```

2. **Use PostgreSQL** instead of SQLite in `app/core/dependencies/database.py`:
```python
DATABASE_URL = "postgresql://user:password@localhost/prom_db"
```

3. **Update CORS origins** in `app/main.py`:
```python
allow_origins=["https://yourdomain.com"]  # Specific domain
```

4. **Enable HTTPS** using a reverse proxy (nginx/Apache)

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use run.py which auto-kills processes
python run.py

# Or manually specify different port
python run.py 8001
```

### Import Errors
Make sure all `__init__.py` files exist in every directory.

### Database Not Found
Run `python init_db.py` to create the database.

### Static Files Not Loading
Make sure the `static` and `templates` directories exist under `app/`.

## 📝 Next Steps

1. ✅ **Create remaining pages**: Seating chart, booking management, admin pages
2. ✅ **Add WebSocket**: Real-time seat updates
3. ✅ **Payment Integration**: Connect Stripe/PayPal
4. ✅ **Email Notifications**: Send booking confirmations
5. ✅ **Testing**: Add unit and integration tests
6. ✅ **Deployment**: Deploy to cloud (AWS, Heroku, DigitalOcean)

## 🎉 You're All Set!

Your prom management system is now running. Students can register, view seats, and book tickets, while admins have full control over the system.

**Need help?** Check the API documentation at http://localhost:8000/docs