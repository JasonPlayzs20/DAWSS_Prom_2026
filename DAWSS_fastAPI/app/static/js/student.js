// API Base URL
const API_BASE = '';

// Get auth token
function getToken() {
    return localStorage.getItem('token');
}

// Get user info
function getUser() {
    return JSON.parse(localStorage.getItem('user') || 'null');
}

// Check authentication
function requireAuth() {
    const token = getToken();
    const user = getUser();

    if (!token || !user) {
        window.location.href = '/login';
        return false;
    }

    // If admin trying to access student pages, redirect
    if (user.role === 'admin' && window.location.pathname.startsWith('/student')) {
        window.location.href = '/admin/dashboard';
        return false;
    }

    return true;
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Display user name in navigation
function displayUserName() {
    const user = getUser();
    const userNameElement = document.getElementById('user-name');
    if (userNameElement && user) {
        userNameElement.textContent = `Hello, ${user.full_name}`;
    }
}

// Load booking status
async function loadBookingStatus() {
    const token = getToken();
    const bookingContent = document.getElementById('booking-content');

    try {
        const response = await fetch(`${API_BASE}/api/student/my-booking`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const booking = await response.json();
            displayBooking(booking);

            // Show manage booking card, hide view seats card
            document.getElementById('manage-booking-card').style.display = 'block';
            document.getElementById('view-seats-card').style.display = 'none';
        } else if (response.status === 404) {
            // No booking found
            bookingContent.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🎫</div>
                    <h3>No Booking Yet</h3>
                    <p style="color: var(--text-secondary); margin: 1rem 0;">
                        You haven't reserved your seat yet.
                    </p>
                    <a href="/student/seating" class="btn btn-primary">
                        Browse Available Seats
                    </a>
                </div>
            `;
        } else {
            throw new Error('Failed to load booking');
        }
    } catch (error) {
        bookingContent.innerHTML = `
            <div class="error-message">
                Failed to load booking information. Please try again later.
            </div>
        `;
    }
}

// Display booking information
function displayBooking(booking) {
    const bookingContent = document.getElementById('booking-content');

    const statusBadge = booking.payment_status === 'completed'
        ? '<span style="background: var(--success-color); padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">✓ Paid</span>'
        : '<span style="background: var(--warning-color); padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">⏳ Pending Payment</span>';

    bookingContent.innerHTML = `
        <div style="display: grid; gap: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>Your Reservation</h3>
                ${statusBadge}
            </div>

            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 8px;">
                <div style="display: grid; gap: 1rem;">
                    <div>
                        <strong>Table Number:</strong>
                        <span style="font-size: 1.5rem; color: var(--primary-color); margin-left: 1rem;">
                            ${booking.seat.table_number}
                        </span>
                    </div>
                    <div>
                        <strong>Seat Number:</strong>
                        <span style="font-size: 1.5rem; color: var(--primary-color); margin-left: 1rem;">
                            ${booking.seat.seat_number}
                        </span>
                    </div>
                    <div>
                        <strong>Amount:</strong>
                        <span style="margin-left: 1rem;">$${booking.payment_amount.toFixed(2)}</span>
                    </div>
                    ${booking.payment_date ? `
                        <div>
                            <strong>Payment Date:</strong>
                            <span style="margin-left: 1rem;">${new Date(booking.payment_date).toLocaleDateString()}</span>
                        </div>
                    ` : ''}
                </div>
            </div>

            ${booking.payment_status === 'pending' ? `
                <a href="/student/booking" class="btn btn-primary btn-block">
                    Complete Payment
                </a>
            ` : `
                <div style="text-align: center; color: var(--success-color); font-weight: bold;">
                    ✓ Your ticket is confirmed! See you at prom!
                </div>
            `}
        </div>
    `;
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;

    displayUserName();

    // Load booking status on dashboard
    if (window.location.pathname === '/student/dashboard') {
        loadBookingStatus();
    }
});