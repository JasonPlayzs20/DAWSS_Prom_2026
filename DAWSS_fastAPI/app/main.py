from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.dependencies.database import engine, Base
from app.core.routers import auth, student, admin, payment, pages

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Prom Management System",
    description="API for managing prom ticketing, seating, and administration",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include page router first to serve HTML pages
app.include_router(pages.router)

# Include API routers
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(admin.router)
app.include_router(payment.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}