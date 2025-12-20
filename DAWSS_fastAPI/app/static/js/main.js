// Main JavaScript file for general functionality

// Check if user is logged in and update nav
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');

    // If on home page and logged in, update nav links
    if (token && user && window.location.pathname === '/') {
        const navLinks = document.querySelector('.nav-links');
        if (navLinks) {
            const dashboardLink = user.role === 'admin'
                ? '/admin/dashboard'
                : '/student/dashboard';

            navLinks.innerHTML = `
                <a href="${dashboardLink}" class="btn btn-primary">Go to Dashboard</a>
                <button onclick="logout()" class="btn btn-outline">Logout</button>
            `;
        }
    }
});

// Logout function (global)
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});