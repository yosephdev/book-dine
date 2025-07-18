// BookDine App Enhancements
class AppEnhancements {
    constructor() {
        this.initializeAnimations();
        this.initializeInteractions();
        this.initializePerformanceOptimizations();
    }

    initializeAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.card, .hero-content, section h2, section p').forEach(el => {
            observer.observe(el);
        });

        // Stagger animations for cards
        document.querySelectorAll('.card').forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
        });
    }

    initializeInteractions() {
        // Enhanced button interactions
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
            });

            btn.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });

        // Card hover effects
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px) scale(1.02)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });

        // Smooth scroll for navigation links
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

        // Form enhancements
        document.querySelectorAll('.form-control, .form-select').forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });

            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
            });
        });
    }

    initializePerformanceOptimizations() {
        // Lazy loading for images
        document.querySelectorAll('img.lazy').forEach(img => {
            img.addEventListener('load', function() {
                this.classList.add('loaded');
            });
        });
        document.querySelectorAll('img.lazy').forEach(img => {
            img.src = img.dataset.src;
        });

        // Preload critical assets
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = '/static/css/custom.css';
        link.as = 'style';
        document.head.appendChild(link);
    }
}

// Initialize when DOM is loaded