"""
Router for serving HTML pages
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(tags=["Pages"])

# Setup templates directory
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Landing page"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page for both students and admins"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Student registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/student/dashboard", response_class=HTMLResponse)
async def student_dashboard_page(request: Request):
    """Student dashboard page"""
    return templates.TemplateResponse("student_dashboard.html", {"request": request})

@router.get("/student/seating", response_class=HTMLResponse)
async def student_seating_page(request: Request):
    """Interactive seating chart for students"""
    return templates.TemplateResponse("student_seating.html", {"request": request})

@router.get("/student/booking", response_class=HTMLResponse)
async def student_booking_page(request: Request):
    """Student booking details and payment page"""
    return templates.TemplateResponse("student_booking.html", {"request": request})

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    """Admin dashboard page"""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@router.get("/admin/seating", response_class=HTMLResponse)
async def admin_seating_page(request: Request):
    """Admin seating management page"""
    return templates.TemplateResponse("admin_seating.html", {"request": request})

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(request: Request):
    """Admin user management page"""
    return templates.TemplateResponse("admin_users.html", {"request": request})

@router.get("/admin/bookings", response_class=HTMLResponse)
async def admin_bookings_page(request: Request):
    """Admin bookings overview page"""
    return templates.TemplateResponse("admin_bookings.html", {"request": request})