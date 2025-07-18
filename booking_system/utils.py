from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Reservation
import logging

logger = logging.getLogger(__name__)

def send_reservation_confirmation(reservation):
    """Send reservation confirmation email"""
    try:
        subject = f'Reservation Confirmation - {reservation.restaurant.name}'
        
        context = {
            'reservation': reservation,
            'user': reservation.user,
            'restaurant': reservation.restaurant,
        }
        
        html_message = render_to_string('emails/reservation_confirmation.html', context)
        plain_message = render_to_string('emails/reservation_confirmation.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reservation.contact_email or reservation.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Confirmation email sent for reservation {reservation.id}")
        
    except Exception as e:
        logger.error(f"Failed to send confirmation email for reservation {reservation.id}: {str(e)}")
        raise

def send_cancellation_email(reservation):
    """Send reservation cancellation email"""
    try:
        subject = f'Reservation Cancelled - {reservation.restaurant.name}'
        
        context = {
            'reservation': reservation,
            'user': reservation.user,
            'restaurant': reservation.restaurant,
        }
        
        html_message = render_to_string('emails/reservation_cancellation.html', context)
        plain_message = render_to_string('emails/reservation_cancellation.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reservation.contact_email or reservation.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Cancellation email sent for reservation {reservation.id}")
        
    except Exception as e:
        logger.error(f"Failed to send cancellation email for reservation {reservation.id}: {str(e)}")
        raise

def send_reminder_emails():
    """Send reminder emails for upcoming reservations (to be run as a cron job)"""
    try:
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        
        upcoming_reservations = Reservation.objects.filter(
            date=tomorrow,
            status__in=['confirmed', 'pending']
        ).select_related('user', 'restaurant')
        
        for reservation in upcoming_reservations:
            try:
                subject = f'Reminder: Your reservation at {reservation.restaurant.name}'
                
                context = {
                    'reservation': reservation,
                    'user': reservation.user,
                    'restaurant': reservation.restaurant,
                }
                
                html_message = render_to_string('emails/reservation_reminder.html', context)
                plain_message = render_to_string('emails/reservation_reminder.txt', context)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reservation.contact_email or reservation.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                logger.info(f"Reminder email sent for reservation {reservation.id}")
                
            except Exception as e:
                logger.error(f"Failed to send reminder email for reservation {reservation.id}: {str(e)}")
                continue
        
        logger.info(f"Processed {upcoming_reservations.count()} reminder emails")
        
    except Exception as e:
        logger.error(f"Error in send_reminder_emails: {str(e)}")
        raise

def get_restaurant_analytics(restaurant, days=30):
    """Get analytics data for a restaurant"""
    try:
        from django.db.models import Count, Avg
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        reservations = Reservation.objects.filter(
            restaurant=restaurant,
            date__range=[start_date, end_date]
        )
        
        analytics = {
            'total_reservations': reservations.count(),
            'confirmed_reservations': reservations.filter(status='confirmed').count(),
            'cancelled_reservations': reservations.filter(status='cancelled').count(),
            'completed_reservations': reservations.filter(status='completed').count(),
            'no_shows': reservations.filter(status='no_show').count(),
            'average_party_size': reservations.aggregate(
                avg_guests=Avg('number_of_guests')
            )['avg_guests'] or 0,
            'busiest_days': reservations.values('date').annotate(
                count=Count('id')
            ).order_by('-count')[:5],
            'popular_times': reservations.values('time').annotate(
                count=Count('id')
            ).order_by('-count')[:5],
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting analytics for restaurant {restaurant.id}: {str(e)}")
        return {}