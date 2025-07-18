/**
 * API Client for BookDine Restaurant Booking System
 * Handles all API communications with proper error handling and authentication
 */

class BookDineAPI {
    constructor() {
        this.baseURL = '/api';
        this.csrfToken = this.getCSRFToken();
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrfToken
        };
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
               document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                let errorData = {};
                try {
                    errorData = await response.json();
                } catch (parseError) {
                    errorData = { message: response.statusText };
                }
                
                // Handle different error types
                const errorMessage = errorData.message || errorData.detail || response.statusText;
                const apiError = new APIError(response.status, errorMessage, errorData);
                
                // Log error for debugging
                console.error('API Error:', {
                    status: response.status,
                    endpoint,
                    error: errorData
                });
                
                throw apiError;
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            return await response.text();
        } catch (error) {
            if (error instanceof APIError) throw error;
            
            // Network or other errors
            console.error('Network Error:', error);
            throw new APIError(0, 'Network error - please check your connection', { 
                originalError: error.message 
            });
        }
    }

    // Restaurant endpoints
    async getRestaurants(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/restaurants/${queryString ? '?' + queryString : ''}`);
    }

    async getRestaurant(id) {
        return this.request(`/restaurants/${id}/`);
    }

    async getFeaturedRestaurants() {
        return this.request('/restaurants/featured/');
    }

    async getRestaurantAvailability(restaurantId, date) {
        return this.request(`/restaurants/${restaurantId}/availability/?date=${date}`);
    }

    async getCuisines() {
        return this.request('/restaurants/cuisines/');
    }

    // Reservation endpoints
    async createReservation(reservationData) {
        return this.request('/reservations/', {
            method: 'POST',
            body: JSON.stringify(reservationData)
        });
    }

    async getReservations() {
        return this.request('/reservations/');
    }

    async getUpcomingReservations() {
        return this.request('/reservations/upcoming/');
    }

    async getReservationHistory() {
        return this.request('/reservations/history/');
    }

    async cancelReservation(reservationId) {
        return this.request(`/reservations/${reservationId}/cancel/`, {
            method: 'POST'
        });
    }

    // Review endpoints
    async createReview(reviewData) {
        return this.request('/reviews/', {
            method: 'POST',
            body: JSON.stringify(reviewData)
        });
    }

    async getReviews() {
        return this.request('/reviews/');
    }

    // Utility endpoints
    async checkAvailability(availabilityData) {
        return this.request('/check-availability/', {
            method: 'POST',
            body: JSON.stringify(availabilityData)
        });
    }

    async getDashboardStats() {
        return this.request('/dashboard/');
    }

    async getHealthCheck() {
        return this.request('/health/');
    }
}

class APIError extends Error {
    constructor(status, message, data = {}) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
    
    // Helper method to display user-friendly error messages
    getUserMessage() {
        switch (this.status) {
            case 400:
                return this.data.errors ? 'Please check your input and try again.' : this.message;
            case 401:
                return 'Please log in to continue.';
            case 403:
                return 'You do not have permission to perform this action.';
            case 404:
                return 'The requested resource was not found.';
            case 429:
                return 'Too many requests. Please wait a moment and try again.';
            case 500:
                return 'Server error. Please try again later.';
            default:
                return this.message || 'An unexpected error occurred.';
        }
    }
    
    // Helper to show error in UI
    showToUser(containerId = 'error-container') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    ${this.getUserMessage()}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    }
}

// Global API client instance
window.bookdineAPI = new BookDineAPI();
