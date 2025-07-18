// Enhanced BookDine Frontend Application
class BookingSystem {
    constructor() {
        this.api = window.bookdineAPI;
        this.currentUser = null;
        this.selectedRestaurant = null;
        this.availableTimeSlots = [];
        this.currentFilters = {};
        this.retryAttempts = 3;
        this.retryDelay = 1000;
        
        this.initializeEventListeners();
        this.initializeDatePicker();
        this.initializeFormValidation();
        this.initializeErrorHandling();
        this.loadInitialData();
    }

    initializeErrorHandling() {
        // Global error handler for unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showToast('An unexpected error occurred. Please try again.', 'error');
            event.preventDefault();
        });

        // Global error handler for JavaScript errors
        window.addEventListener('error', (event) => {
            console.error('JavaScript error:', event.error);
            this.showToast('Something went wrong. Please refresh the page.', 'error');
        });
    }

    async withRetry(operation, maxRetries = this.retryAttempts) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                console.warn(`Attempt ${attempt} failed:`, error);
                
                if (attempt === maxRetries) {
                    throw error;
                }
                
                // Exponential backoff
                const delay = this.retryDelay * Math.pow(2, attempt - 1);
                await this.sleep(delay);
            }
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async loadInitialData() {
        const loadingTasks = [];
        
        try {
            // Load featured restaurants on home page
            if (document.querySelector('.featured-restaurants')) {
                loadingTasks.push(this.safeLoadFeaturedRestaurants());
            }

            // Load restaurant list if on restaurants page
            if (document.querySelector('.restaurant-list')) {
                loadingTasks.push(this.safeLoadRestaurants());
            }

            // Load user reservations if on reservations page
            if (document.querySelector('.user-reservations')) {
                loadingTasks.push(this.safeLoadUserReservations());
            }

            // Load dashboard stats if on dashboard
            if (document.querySelector('.dashboard-stats')) {
                loadingTasks.push(this.safeLoadDashboardStats());
            }

            // Execute all loading tasks with error isolation
            await Promise.allSettled(loadingTasks);

        } catch (error) {
            console.error('Critical error during initial data load:', error);
            this.showCriticalError();
        }
    }

    async safeLoadFeaturedRestaurants() {
        try {
            const restaurants = await this.withRetry(() => this.api.getFeaturedRestaurants());
            this.renderFeaturedRestaurants(restaurants);
        } catch (error) {
            console.error('Error loading featured restaurants:', error);
            this.renderFeaturedRestaurantsError();
        }
    }

    async safeLoadRestaurants(filters = {}) {
        const container = document.querySelector('.restaurant-list');
        if (!container) return;

        try {
            this.showLoadingState(container);
            const data = await this.withRetry(() => this.api.getRestaurants(filters));
            this.renderRestaurantList(data.results || data);
            
            if (data.count !== undefined) {
                this.updatePagination(data);
            }
        } catch (error) {
            console.error('Error loading restaurants:', error);
            this.renderRestaurantListError(container, error);
        }
    }

    getPlaceholderImage() {
        return 'data:image/svg+xml;base64,' + btoa(`
            <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
                <rect width="100%" height="100%" fill="#f8f9fa"/>
                <rect x="50%" y="50%" width="80" height="80" rx="8" fill="#dee2e6" transform="translate(-40, -40)"/>
                <circle cx="50%" cy="40%" r="12" fill="#6c757d"/>
                <rect x="50%" y="55%" width="40" height="4" rx="2" fill="#6c757d" transform="translate(-20, 0)"/>
                <rect x="50%" y="65%" width="60" height="3" rx="1.5" fill="#adb5bd" transform="translate(-30, 0)"/>
                <text x="50%" y="85%" text-anchor="middle" fill="#6c757d" font-family="Arial, sans-serif" font-size="12">Restaurant Image</text>
            </svg>
        `);
    }

    renderFeaturedRestaurants(restaurants) {
        const container = document.querySelector('.featured-restaurants');
        if (!container) return;

        container.innerHTML = restaurants.map(restaurant => `
            <div class="col-md-4 mb-4">
                <div class="card restaurant-card h-100">
                    <img src="${restaurant.image || this.getPlaceholderImage()}" 
                         class="card-img-top" alt="${restaurant.name}" style="height: 200px; object-fit: cover;"
                         onerror="this.src='${this.getPlaceholderImage()}'">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${restaurant.name}</h5>
                        <p class="card-text text-muted">${restaurant.cuisine} • ${restaurant.location}</p>
                        <p class="card-text flex-grow-1">${restaurant.description}</p>
                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <div class="rating">
                                ${this.renderStars(restaurant.average_rating || restaurant.rating)}
                                <span class="ms-1">(${restaurant.total_reviews || 0})</span>
                            </div>
                            <div class="btn-group">
                                <a href="/restaurants/${restaurant.id}/" class="btn btn-outline-primary btn-sm">View</a>
                                <button class="btn btn-primary btn-sm" onclick="bookingSystem.quickBook('${restaurant.id}')">
                                    Book Now
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderRestaurantList(restaurants) {
        const container = document.querySelector('.restaurant-list');
        if (!container) return;

        if (restaurants.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <h4>No restaurants found</h4>
                    <p class="text-muted">Try adjusting your search criteria</p>
                </div>
            `;
            return;
        }

        container.innerHTML = restaurants.map(restaurant => `
            <div class="col-lg-6 mb-4">
                <div class="card restaurant-card h-100">
                    <div class="row g-0">
                        <div class="col-md-4">
                            <img src="${restaurant.image || this.getPlaceholderImage()}" 
                                 class="img-fluid rounded-start h-100" alt="${restaurant.name}" 
                                 style="object-fit: cover;"
                                 onerror="this.src='${this.getPlaceholderImage()}'">
                        </div>
                        <div class="col-md-8">
                            <div class="card-body d-flex flex-column h-100">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <h5 class="card-title mb-0">${restaurant.name}</h5>
                                    <span class="badge bg-${restaurant.is_open_now ? 'success' : 'secondary'}">
                                        ${restaurant.is_open_now ? 'Open' : 'Closed'}
                                    </span>
                                </div>
                                <p class="card-text text-muted small">${restaurant.cuisine} • ${restaurant.location}</p>
                                <p class="card-text flex-grow-1">${restaurant.description}</p>
                                <div class="d-flex justify-content-between align-items-center mt-auto">
                                    <div class="rating">
                                        ${this.renderStars(restaurant.average_rating || restaurant.rating)}
                                        <span class="ms-1 small">(${restaurant.total_reviews || 0})</span>
                                    </div>
                                    <div class="btn-group">
                                        <a href="/restaurants/${restaurant.id}/" class="btn btn-outline-primary btn-sm">
                                            Details
                                        </a>
                                        <button class="btn btn-primary btn-sm" 
                                                onclick="bookingSystem.quickBook('${restaurant.id}')"
                                                ${!restaurant.is_open_now ? 'disabled' : ''}>
                                            Book Table
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async safeLoadUserReservations() {
        try {
            const [upcoming, history] = await Promise.allSettled([
                this.withRetry(() => this.api.getUpcomingReservations()),
                this.withRetry(() => this.api.getReservationHistory())
            ]);

            if (upcoming.status === 'fulfilled') {
                this.renderUpcomingReservations(upcoming.value);
            } else {
                this.renderUpcomingReservationsError();
            }

            if (history.status === 'fulfilled') {
                this.renderReservationHistory(history.value.results || history.value);
            } else {
                this.renderReservationHistoryError();
            }
        } catch (error) {
            console.error('Error loading reservations:', error);
            this.showToast('Error loading reservations. Please refresh the page.', 'error');
        }
    }

    renderUpcomingReservations(reservations) {
        const container = document.querySelector('.upcoming-reservations');
        if (!container) return;

        if (reservations.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <h5>No upcoming reservations</h5>
                    <p class="text-muted">Ready to book your next dining experience?</p>
                    <a href="/book-table/" class="btn btn-primary">Book a Table</a>
                </div>
            `;
            return;
        }

        container.innerHTML = reservations.map(reservation => `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <img src="${reservation.restaurant.image || this.getPlaceholderImage()}" 
                                 class="img-fluid rounded" alt="${reservation.restaurant.name}"
                                 onerror="this.src='${this.getPlaceholderImage()}'">
                        </div>
                        <div class="col-md-6">
                            <h5 class="card-title">${reservation.restaurant.name}</h5>
                            <p class="card-text">
                                <i class="fas fa-calendar me-2"></i>${this.formatDate(reservation.date)}<br>
                                <i class="fas fa-clock me-2"></i>${this.formatTime(reservation.time)}<br>
                                <i class="fas fa-users me-2"></i>${reservation.number_of_guests} guests
                            </p>
                            <span class="badge bg-${this.getStatusColor(reservation.status)}">
                                ${reservation.status.charAt(0).toUpperCase() + reservation.status.slice(1)}
                            </span>
                        </div>
                        <div class="col-md-3 text-end">
                            ${reservation.can_cancel ? `
                                <button class="btn btn-outline-danger btn-sm" 
                                        onclick="bookingSystem.cancelReservation('${reservation.id}')">
                                    Cancel
                                </button>
                            ` : ''}
                            <a href="/restaurants/${reservation.restaurant.id}/" class="btn btn-outline-primary btn-sm">
                                View Restaurant
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderReservationHistory(reservations) {
        const container = document.querySelector('.reservation-history');
        if (!container) return;

        if (reservations.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <h5>No reservation history</h5>
                    <p class="text-muted">Your past reservations will appear here</p>
                </div>
            `;
            return;
        }

        container.innerHTML = reservations.map(reservation => `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <img src="${reservation.restaurant.image || this.getPlaceholderImage()}" 
                                 class="img-fluid rounded" alt="${reservation.restaurant.name}"
                                 onerror="this.src='${this.getPlaceholderImage()}'">
                        </div>
                        <div class="col-md-6">
                            <h5 class="card-title">${reservation.restaurant.name}</h5>
                            <p class="card-text">
                                <i class="fas fa-calendar me-2"></i>${this.formatDate(reservation.date)}<br>
                                <i class="fas fa-clock me-2"></i>${this.formatTime(reservation.time)}<br>
                                <i class="fas fa-users me-2"></i>${reservation.number_of_guests} guests
                            </p>
                            <span class="badge bg-${this.getStatusColor(reservation.status)}">
                                ${reservation.status.charAt(0).toUpperCase() + reservation.status.slice(1)}
                            </span>
                        </div>
                        <div class="col-md-3 text-end">
                            <a href="/restaurants/${reservation.restaurant.id}/" class="btn btn-outline-primary btn-sm">
                                View Restaurant
                            </a>
                            ${reservation.status === 'completed' ? `
                                <a href="/restaurants/${reservation.restaurant.id}/review/" class="btn btn-success btn-sm">
                                    Leave Review
                                </a>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async safeLoadDashboardStats() {
        try {
            const stats = await this.withRetry(() => this.api.getDashboardStats());
            this.renderDashboardStats(stats);
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
            this.renderDashboardStatsError();
        }
    }

    renderDashboardStats(stats) {
        const container = document.querySelector('.dashboard-stats');
        if (!container) return;

        container.innerHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-primary">${stats.total_reservations || 0}</h3>
                            <p class="card-text">Total Reservations</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-success">${stats.upcoming_reservations || 0}</h3>
                            <p class="card-text">Upcoming</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-info">${stats.completed_reservations || 0}</h3>
                            <p class="card-text">Completed</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-warning">${stats.favorite_restaurants || 0}</h3>
                            <p class="card-text">Favorite Places</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async quickBook(restaurantId) {
        try {
            this.showLoadingToast('Loading restaurant details...');
            const restaurant = await this.withRetry(() => this.api.getRestaurant(restaurantId));
            this.selectedRestaurant = restaurant;
            this.showQuickBookModal(restaurant);
            this.hideLoadingToast();
        } catch (error) {
            this.hideLoadingToast();
            console.error('Error loading restaurant for quick book:', error);
            
            if (error.status === 404) {
                this.showToast('Restaurant not found. It may no longer be available.', 'error');
            } else if (error.status === 0) {
                this.showToast('Network error. Please check your connection and try again.', 'error');
            } else {
                this.showToast('Unable to load restaurant details. Please try again.', 'error');
            }
        }
    }

    showQuickBookModal(restaurant) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Book Table at ${restaurant.name}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="quick-book-form">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="book-date" class="form-label">Date</label>
                                    <input type="date" class="form-control" id="book-date" required
                                           min="${new Date().toISOString().split('T')[0]}">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="book-guests" class="form-label">Number of Guests</label>
                                    <select class="form-select" id="book-guests" required>
                                        <option value="">Select guests</option>
                                        ${Array.from({length: 10}, (_, i) => i + 1).map(num => 
                                            `<option value="${num}">${num} ${num === 1 ? 'guest' : 'guests'}</option>`
                                        ).join('')}
                                    </select>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Available Time Slots</label>
                                <div id="time-slots" class="d-flex flex-wrap gap-2">
                                    <p class="text-muted">Please select date and number of guests first</p>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="special-requests" class="form-label">Special Requests (Optional)</label>
                                <textarea class="form-control" id="special-requests" rows="3" 
                                          placeholder="Any special dietary requirements or requests..."></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirm-booking" disabled>
                            Confirm Booking
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Event listeners for the modal
        const dateInput = modal.querySelector('#book-date');
        const guestsInput = modal.querySelector('#book-guests');
        const confirmBtn = modal.querySelector('#confirm-booking');

        [dateInput, guestsInput].forEach(input => {
            input.addEventListener('change', () => this.updateTimeSlots(restaurant.id, modal));
        });

        confirmBtn.addEventListener('click', () => this.confirmQuickBooking(restaurant, modal, bsModal));

        // Clean up modal when closed
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    async updateTimeSlots(restaurantId, modal) {
        const dateInput = modal.querySelector('#book-date');
        const guestsInput = modal.querySelector('#book-guests');
        const timeSlotsContainer = modal.querySelector('#time-slots');
        const confirmBtn = modal.querySelector('#confirm-booking');

        if (!dateInput.value || !guestsInput.value) {
            timeSlotsContainer.innerHTML = '<p class="text-muted">Please select date and number of guests first</p>';
            confirmBtn.disabled = true;
            return;
        }

        try {
            timeSlotsContainer.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2"></div>
                    <span>Loading available times...</span>
                </div>
            `;
            
            const availability = await this.withRetry(() => 
                this.api.getRestaurantAvailability(restaurantId, dateInput.value)
            );
            
            const availableSlots = availability.time_slots.filter(slot => slot.is_available);
            
            if (availableSlots.length === 0) {
                timeSlotsContainer.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-calendar-times me-2"></i>
                        No available time slots for this date. Please try a different date.
                    </div>
                `;
                confirmBtn.disabled = true;
                return;
            }

            timeSlotsContainer.innerHTML = availableSlots.map(slot => `
                <button type="button" class="btn btn-outline-primary time-slot-btn me-2 mb-2" data-time="${slot.time}">
                    ${slot.time}
                </button>
            `).join('');

            // Add click handlers for time slots
            timeSlotsContainer.querySelectorAll('.time-slot-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    timeSlotsContainer.querySelectorAll('.time-slot-btn').forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    confirmBtn.disabled = false;
                });
            });

        } catch (error) {
            console.error('Error loading time slots:', error);
            
            let errorMessage = 'Error loading available times';
            if (error.status === 0) {
                errorMessage = 'Network error. Please check your connection.';
            } else if (error.status === 429) {
                errorMessage = 'Too many requests. Please wait a moment and try again.';
            }
            
            timeSlotsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    ${errorMessage}
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="bookingSystem.updateTimeSlots('${restaurantId}', this.closest('.modal'))">
                        <i class="fas fa-refresh me-1"></i>Retry
                    </button>
                </div>
            `;
            confirmBtn.disabled = true;
        }
    }

    async confirmQuickBooking(restaurant, modal, bsModal) {
        const confirmBtn = modal.querySelector('#confirm-booking');
        const originalText = confirmBtn.innerHTML;
        
        try {
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating reservation...';

            const reservationData = {
                restaurant: restaurant.id,
                date: modal.querySelector('#book-date').value,
                time: modal.querySelector('.time-slot-btn.active').dataset.time,
                number_of_guests: parseInt(modal.querySelector('#book-guests').value),
                special_requests: modal.querySelector('#special-requests')?.value || ''
            };

            const reservation = await this.withRetry(() => this.api.createReservation(reservationData));
            
            bsModal.hide();
            this.showToast('Reservation confirmed successfully!', 'success');
            
            // Redirect to reservations page or refresh current page
            if (window.location.pathname === '/reservations/') {
                this.safeLoadUserReservations();
            } else {
                setTimeout(() => {
                    window.location.href = '/reservations/';
                }, 2000);
            }

        } catch (error) {
            console.error('Error creating reservation:', error);
            
            let errorMessage = 'Error creating reservation';
            if (error.status === 400) {
                errorMessage = error.data?.detail || 'Please check your booking details and try again.';
            } else if (error.status === 409) {
                errorMessage = 'This time slot is no longer available. Please select a different time.';
            } else if (error.status === 0) {
                errorMessage = 'Network error. Please check your connection and try again.';
            }
            
            this.showToast(errorMessage, 'error');
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = originalText;
        }
    }

    async cancelReservation(reservationId) {
        if (!confirm('Are you sure you want to cancel this reservation?')) {
            return;
        }

        try {
            await this.api.cancelReservation(reservationId);
            this.showToast('Reservation cancelled successfully', 'success');
            this.loadUserReservations(); // Refresh the list
        } catch (error) {
            console.error('Error cancelling reservation:', error);
            this.showToast(error.data?.detail || 'Error cancelling reservation', 'error');
        }
    }

    // Utility methods
    renderStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

        return [
            ...Array(fullStars).fill('<i class="fas fa-star text-warning"></i>'),
            ...(hasHalfStar ? ['<i class="fas fa-star-half-alt text-warning"></i>'] : []),
            ...Array(emptyStars).fill('<i class="far fa-star text-warning"></i>')
        ].join('');
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    formatTime(timeString) {
        return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    getStatusColor(status) {
        const colors = {
            'pending': 'warning',
            'confirmed': 'success',
            'completed': 'info',
            'cancelled': 'danger'
        };
        return colors[status] || 'secondary';
    }

    showLoadingToast(message) {
        this.hideLoadingToast(); // Remove any existing loading toast
        
        const toastContainer = document.querySelector('#toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-info border-0 loading-toast';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <div class="spinner-border spinner-border-sm me-2"></div>
                    ${message}
                </div>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { autohide: false });
        bsToast.show();
    }

    hideLoadingToast() {
        const loadingToast = document.querySelector('.loading-toast');
        if (loadingToast) {
            const bsToast = bootstrap.Toast.getInstance(loadingToast);
            if (bsToast) {
                bsToast.hide();
            }
            setTimeout(() => {
                if (loadingToast.parentNode) {
                    loadingToast.parentNode.removeChild(loadingToast);
                }
            }, 300);
        }
    }

    showToast(message, type = 'info', duration = 5000) {
        const toastContainer = document.querySelector('#toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            if (toastContainer.contains(toast)) {
                toastContainer.removeChild(toast);
            }
        });
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    }

    // Initialize existing methods
    initializeEventListeners() {
        // Restaurant search with debouncing
        const searchInput = document.getElementById('restaurant-search');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        }

        // Filter handling
        document.querySelectorAll('.filter-option').forEach(filter => {
            filter.addEventListener('change', () => this.applyFilters());
        });

        // Smooth scrolling for navigation
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
    }

    async performSearch(query) {
        this.currentFilters = { ...this.currentFilters, search: query };
        await this.loadRestaurants(this.currentFilters);
    }

    async applyFilters() {
        const filters = {};
        
        // Collect filter values
        document.querySelectorAll('.filter-option:checked').forEach(filter => {
            const filterType = filter.dataset.filterType;
            const filterValue = filter.value;
            
            if (!filters[filterType]) {
                filters[filterType] = [];
            }
            filters[filterType].push(filterValue);
        });

        // Convert arrays to comma-separated strings for API
        Object.keys(filters).forEach(key => {
            if (Array.isArray(filters[key])) {
                filters[key] = filters[key].join(',');
            }
        });

        this.currentFilters = filters;
        await this.loadRestaurants(this.currentFilters);
    }

    initializeDatePicker() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            input.min = new Date().toISOString().split('T')[0];
        });
    }

    initializeFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }

    updatePagination(data) {
        const paginationNav = document.getElementById('pagination-nav');
        const pagination = document.getElementById('pagination');
        
        if (!paginationNav || !pagination) return;
        
        // Hide pagination if not needed
        if (!data.count || data.count <= (data.results?.length || 0)) {
            paginationNav.style.display = 'none';
            return;
        }
        
        paginationNav.style.display = 'block';
        
        const currentPage = data.current_page || 1;
        const totalPages = Math.ceil(data.count / (data.page_size || 10));
        let paginationHTML = '';
        
        // Previous button
        if (data.previous) {
            paginationHTML += `<li class="page-item">
                <a class="page-link" href="#" onclick="bookingSystem.loadRestaurants({...bookingSystem.currentFilters, page: ${currentPage - 1}}); return false;">Previous</a>
            </li>`;
        }
        
        // Page numbers (show max 5 pages around current)
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        if (startPage > 1) {
            paginationHTML += `<li class="page-item">
                <a class="page-link" href="#" onclick="bookingSystem.loadRestaurants({...bookingSystem.currentFilters, page: 1}); return false;">1</a>
            </li>`;
            if (startPage > 2) {
                paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            if (i === currentPage) {
                paginationHTML += `<li class="page-item active">
                    <span class="page-link">${i}</span>
                </li>`;
            } else {
                paginationHTML += `<li class="page-item">
                    <a class="page-link" href="#" onclick="bookingSystem.loadRestaurants({...bookingSystem.currentFilters, page: ${i}}); return false;">${i}</a>
                </li>`;
            }
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            paginationHTML += `<li class="page-item">
                <a class="page-link" href="#" onclick="bookingSystem.loadRestaurants({...bookingSystem.currentFilters, page: ${totalPages}}); return false;">${totalPages}</a>
            </li>`;
        }
        
        // Next button
        if (data.next) {
            paginationHTML += `<li class="page-item">
                <a class="page-link" href="#" onclick="bookingSystem.loadRestaurants({...bookingSystem.currentFilters, page: ${currentPage + 1}}); return false;">Next</a>
            </li>`;
        }
        
        pagination.innerHTML = paginationHTML;
    }

    // Error rendering methods
    renderFeaturedRestaurantsError() {
        const container = document.querySelector('.featured-restaurants');
        if (!container) return;

        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <h5>Unable to load featured restaurants</h5>
                    <p class="mb-3">We're having trouble loading our featured restaurants right now.</p>
                    <button class="btn btn-primary" onclick="bookingSystem.safeLoadFeaturedRestaurants()">
                        <i class="fas fa-refresh me-2"></i>Try Again
                    </button>
                </div>
            </div>
        `;
    }

    renderRestaurantListError(container, error) {
        const isNetworkError = error.status === 0;
        const errorMessage = isNetworkError ? 
            'Network connection issue. Please check your internet connection.' :
            'Unable to load restaurants at the moment.';

        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    <h4>Error Loading Restaurants</h4>
                    <p class="mb-3">${errorMessage}</p>
                    <div class="d-flex gap-2 justify-content-center">
                        <button class="btn btn-primary" onclick="bookingSystem.safeLoadRestaurants()">
                            <i class="fas fa-refresh me-2"></i>Retry
                        </button>
                        <button class="btn btn-outline-secondary" onclick="location.reload()">
                            <i class="fas fa-redo me-2"></i>Refresh Page
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderUpcomingReservationsError() {
        const container = document.querySelector('.upcoming-reservations');
        if (!container) return;

        container.innerHTML = `
            <div class="text-center py-4">
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <h5>Unable to load upcoming reservations</h5>
                    <p class="mb-3">Please try refreshing the page or contact support if the issue persists.</p>
                    <button class="btn btn-primary" onclick="bookingSystem.safeLoadUserReservations()">
                        <i class="fas fa-refresh me-2"></i>Try Again
                    </button>
                </div>
            </div>
        `;
    }

    renderReservationHistoryError() {
        const container = document.querySelector('.reservation-history');
        if (!container) return;

        container.innerHTML = `
            <div class="text-center py-4">
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <h5>Unable to load reservation history</h5>
                    <p class="mb-3">Your reservation history is temporarily unavailable.</p>
                    <button class="btn btn-primary" onclick="bookingSystem.safeLoadUserReservations()">
                        <i class="fas fa-refresh me-2"></i>Try Again
                    </button>
                </div>
            </div>
        `;
    }

    renderDashboardStatsError() {
        const container = document.querySelector('.dashboard-stats');
        if (!container) return;

        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    <h5>Dashboard statistics unavailable</h5>
                    <p class="mb-0">We're working to restore your dashboard statistics.</p>
                </div>
            </div>
        `;
    }

    showLoadingState(container) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-muted">Loading restaurants...</p>
            </div>
        `;
    }

    showCriticalError() {
        const body = document.body;
        const errorOverlay = document.createElement('div');
        errorOverlay.className = 'critical-error-overlay';
        errorOverlay.innerHTML = `
            <div class="critical-error-content">
                <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                <h3>Something went wrong</h3>
                <p>We're experiencing technical difficulties. Please refresh the page or try again later.</p>
                <div class="mt-4">
                    <button class="btn btn-primary me-2" onclick="location.reload()">
                        <i class="fas fa-refresh me-2"></i>Refresh Page
                    </button>
                    <button class="btn btn-outline-secondary" onclick="history.back()">
                        <i class="fas fa-arrow-left me-2"></i>Go Back
                    </button>
                </div>
            </div>
        `;
        body.appendChild(errorOverlay);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.bookingSystem = new BookingSystem();
});

// Progressive Web App functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    });
}
