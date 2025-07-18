import stripe
import logging
from django.conf import settings
from django.db import transaction
from decimal import Decimal
from .models import Reservation, Payment

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

class PaymentProcessor:
    """Handle payment processing with Stripe"""
    
    def __init__(self):
        self.stripe = stripe
    
    def create_payment_intent(self, reservation, amount):
        """Create a Stripe payment intent"""
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'reservation_id': reservation.id,
                    'restaurant_name': reservation.restaurant.name,
                    'customer_email': reservation.user.email,
                },
                receipt_email=reservation.user.email,
                description=f'Reservation at {reservation.restaurant.name}',
            )
            
            # Create payment record
            payment = Payment.objects.create(
                reservation=reservation,
                amount=amount,
                currency='USD',
                stripe_payment_intent_id=intent.id,
                status='pending'
            )
            
            logger.info(f"Payment intent created: {intent.id} for reservation {reservation.id}")
            return intent, payment
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            raise PaymentError(f"Payment processing error: {str(e)}")
    
    def confirm_payment(self, payment_intent_id):
        """Confirm payment and update reservation status"""
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(
                    stripe_payment_intent_id=payment_intent_id
                )
                
                if intent.status == 'succeeded':
                    payment.status = 'completed'
                    payment.stripe_charge_id = intent.charges.data[0].id
                    payment.save()
                    
                    # Update reservation status
                    reservation = payment.reservation
                    reservation.status = 'confirmed'
                    reservation.payment_status = 'paid'
                    reservation.save()
                    
                    logger.info(f"Payment confirmed for reservation {reservation.id}")
                    return True
                    
                elif intent.status == 'payment_failed':
                    payment.status = 'failed'
                    payment.save()
                    logger.warning(f"Payment failed for reservation {payment.reservation.id}")
                    return False
                    
        except (Payment.DoesNotExist, stripe.error.StripeError) as e:
            logger.error(f"Error confirming payment: {str(e)}")
            raise PaymentError(f"Payment confirmation error: {str(e)}")
    
    def process_refund(self, payment, amount=None):
        """Process refund for a payment"""
        try:
            if not payment.stripe_charge_id:
                raise PaymentError("No charge ID found for refund")
            
            refund_amount = amount or payment.amount
            
            refund = self.stripe.Refund.create(
                charge=payment.stripe_charge_id,
                amount=int(refund_amount * 100),
                metadata={
                    'reservation_id': payment.reservation.id,
                    'reason': 'Customer cancellation',
                }
            )
            
            payment.refund_amount = refund_amount
            payment.stripe_refund_id = refund.id
            payment.status = 'refunded'
            payment.save()
            
            logger.info(f"Refund processed: {refund.id} for payment {payment.id}")
            return refund
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error processing refund: {str(e)}")
            raise PaymentError(f"Refund processing error: {str(e)}")

class PaymentError(Exception):
    """Custom payment processing exception"""
    pass

def calculate_reservation_cost(reservation):
    """Calculate the cost for a reservation"""
    base_cost = Decimal('25.00')  # Base reservation fee
    
    # Add per-person fee
    per_person_fee = Decimal('5.00')
    total_cost = base_cost + (per_person_fee * reservation.number_of_guests)
    
    # Apply restaurant-specific pricing if available
    if hasattr(reservation.restaurant, 'reservation_fee'):
        total_cost = reservation.restaurant.reservation_fee
    
    # Apply time-based pricing (peak hours)
    if reservation.time.hour >= 18:  # After 6 PM
        total_cost *= Decimal('1.2')  # 20% surcharge
    
    return total_cost.quantize(Decimal('0.01'))