from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
import json

from .models import Restaurant, Reservation, Review, Table

class AnalyticsEngine:
    """Advanced analytics for restaurant performance and booking patterns"""
    
    def __init__(self, restaurant=None):
        self.restaurant = restaurant
    
    def get_booking_trends(self, days=30):
        """Get booking trends over specified period"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        queryset = Reservation.objects.filter(
            date__range=[start_date, end_date]
        )
        
        if self.restaurant:
            queryset = queryset.filter(restaurant=self.restaurant)
        
        # Daily booking counts
        daily_bookings = queryset.values('date').annotate(
            count=Count('id'),
            confirmed=Count('id', filter=Q(status='confirmed')),
            cancelled=Count('id', filter=Q(status='cancelled')),
            revenue=Sum('payment__amount', filter=Q(payment__status='completed'))
        ).order_by('date')
        
        # Weekly patterns
        weekly_patterns = queryset.extra(
            select={'weekday': 'EXTRACT(dow FROM date)'}
        ).values('weekday').annotate(
            count=Count('id'),
            avg_guests=Avg('number_of_guests')
        ).order_by('weekday')
        
        # Hourly patterns
        hourly_patterns = queryset.extra(
            select={'hour': 'EXTRACT(hour FROM time)'}
        ).values('hour').annotate(
            count=Count('id'),
            avg_guests=Avg('number_of_guests')
        ).order_by('hour')
        
        return {
            'daily_bookings': list(daily_bookings),
            'weekly_patterns': list(weekly_patterns),
            'hourly_patterns': list(hourly_patterns),
            'total_bookings': queryset.count(),
            'total_revenue': queryset.aggregate(
                revenue=Sum('payment__amount', filter=Q(payment__status='completed'))
            )['revenue'] or 0
        }
    
    def get_customer_insights(self):
        """Get customer behavior insights"""
        queryset = Reservation.objects.all()
        if self.restaurant:
            queryset = queryset.filter(restaurant=self.restaurant)
        
        # Customer segmentation
        customer_stats = queryset.values('user').annotate(
            total_bookings=Count('id'),
            avg_party_size=Avg('number_of_guests'),
            total_spent=Sum('payment__amount', filter=Q(payment__status='completed')),
            last_booking=Max('date')
        )
        
        # Segment customers
        segments = {
            'vip': customer_stats.filter(total_bookings__gte=10, total_spent__gte=500),
            'regular': customer_stats.filter(total_bookings__gte=3, total_bookings__lt=10),
            'occasional': customer_stats.filter(total_bookings__lt=3),
        }
        
        # Repeat customer rate
        repeat_customers = customer_stats.filter(total_bookings__gt=1).count()
        total_customers = customer_stats.count()
        repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        return {
            'segments': {k: list(v) for k, v in segments.items()},
            'repeat_customer_rate': repeat_rate,
            'avg_party_size': queryset.aggregate(avg=Avg('number_of_guests'))['avg'] or 0,
            'customer_lifetime_value': customer_stats.aggregate(
                avg_clv=Avg('total_spent')
            )['avg_clv'] or 0
        }
    
    def get_table_utilization(self, days=30):
        """Analyze table utilization rates"""
        if not self.restaurant:
            return {}
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        tables = self.restaurant.tables.all()
        utilization_data = []
        
        for table in tables:
            reservations = Reservation.objects.filter(
                table=table,
                date__range=[start_date, end_date],
                status__in=['confirmed', 'completed']
            )
            
            total_slots = days * 14  # Assuming 14 time slots per day (9 AM - 11 PM)
            booked_slots = reservations.count()
            utilization_rate = (booked_slots / total_slots * 100) if total_slots > 0 else 0
            
            utilization_data.append({
                'table_number': table.table_number,
                'capacity': table.capacity,
                'utilization_rate': utilization_rate,
                'total_bookings': booked_slots,
                'revenue': reservations.aggregate(
                    revenue=Sum('payment__amount', filter=Q(payment__status='completed'))
                )['revenue'] or 0
            })
        
        return {
            'table_utilization': utilization_data,
            'avg_utilization': sum(t['utilization_rate'] for t in utilization_data) / len(utilization_data) if utilization_data else 0
        }
    
    def get_revenue_analytics(self, days=30):
        """Get detailed revenue analytics"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        queryset = Reservation.objects.filter(
            date__range=[start_date, end_date],
            payment__status='completed'
        )
        
        if self.restaurant:
            queryset = queryset.filter(restaurant=self.restaurant)
        
        # Revenue by time period
        daily_revenue = queryset.values('date').annotate(
            revenue=Sum('payment__amount')
        ).order_by('date')
        
        # Revenue by table size
        revenue_by_party_size = queryset.values('number_of_guests').annotate(
            revenue=Sum('payment__amount'),
            count=Count('id')
        ).order_by('number_of_guests')
        
        # Peak revenue hours
        revenue_by_hour = queryset.extra(
            select={'hour': 'EXTRACT(hour FROM time)'}
        ).values('hour').annotate(
            revenue=Sum('payment__amount'),
            count=Count('id')
        ).order_by('hour')
        
        total_revenue = queryset.aggregate(
            total=Sum('payment__amount')
        )['total'] or 0
        
        return {
            'daily_revenue': list(daily_revenue),
            'revenue_by_party_size': list(revenue_by_party_size),
            'revenue_by_hour': list(revenue_by_hour),
            'total_revenue': total_revenue,
            'avg_revenue_per_booking': total_revenue / queryset.count() if queryset.count() > 0 else 0
        }
    
    def get_predictive_insights(self):
        """Generate predictive insights for future bookings"""
        # Get historical data for the last 90 days
        historical_data = self.get_booking_trends(days=90)
        
        # Simple trend analysis
        daily_bookings = historical_data['daily_bookings']
        if len(daily_bookings) >= 7:
            recent_avg = sum(day['count'] for day in daily_bookings[-7:]) / 7
            previous_avg = sum(day['count'] for day in daily_bookings[-14:-7]) / 7
            trend = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
        else:
            trend = 0
        
        # Seasonal patterns
        seasonal_data = self.analyze_seasonal_patterns()
        
        # Capacity recommendations
        capacity_insights = self.get_capacity_recommendations()
        
        # Revenue forecasting
        revenue_forecast = self.forecast_revenue()
        
        return {
            'booking_trend': {
                'direction': 'increasing' if trend > 5 else 'decreasing' if trend < -5 else 'stable',
                'percentage': abs(trend),
                'recommendation': self.get_trend_recommendation(trend)
            },
            'seasonal_patterns': seasonal_data,
            'capacity_insights': capacity_insights,
            'revenue_forecast': revenue_forecast,
            'peak_times': self.identify_peak_times(),
            'optimization_suggestions': self.get_optimization_suggestions()
        }
    
    def analyze_seasonal_patterns(self):
        """Analyze seasonal booking patterns"""
        queryset = Reservation.objects.all()
        if self.restaurant:
            queryset = queryset.filter(restaurant=self.restaurant)
        
        # Monthly patterns
        monthly_data = queryset.extra(
            select={'month': 'EXTRACT(month FROM date)'}
        ).values('month').annotate(
            count=Count('id'),
            avg_guests=Avg('number_of_guests'),
            revenue=Sum('payment__amount', filter=Q(payment__status='completed'))
        ).order_by('month')
        
        return {
            'monthly_patterns': list(monthly_data),
            'peak_months': sorted(monthly_data, key=lambda x: x['count'], reverse=True)[:3],
            'low_months': sorted(monthly_data, key=lambda x: x['count'])[:3]
        }
    
    def get_capacity_recommendations(self):
        """Provide capacity optimization recommendations"""
        utilization_data = self.get_table_utilization()
        
        recommendations = []
        
        if utilization_data:
            avg_utilization = utilization_data['avg_utilization']
            
            if avg_utilization > 85:
                recommendations.append({
                    'type': 'capacity_increase',
                    'message': 'Consider adding more tables or extending hours',
                    'priority': 'high'
                })
            elif avg_utilization < 40:
                recommendations.append({
                    'type': 'capacity_optimization',
                    'message': 'Consider reducing table count or improving marketing',
                    'priority': 'medium'
                })
            
            # Table-specific recommendations
            for table_data in utilization_data['table_utilization']:
                if table_data['utilization_rate'] < 20:
                    recommendations.append({
                        'type': 'table_optimization',
                        'message': f"Table {table_data['table_number']} has low utilization",
                        'priority': 'low'
                    })
        
        return recommendations
    
    def forecast_revenue(self, days_ahead=30):
        """Simple revenue forecasting based on historical trends"""
        historical_revenue = self.get_revenue_analytics(days=90)
        
        if not historical_revenue['daily_revenue']:
            return {'forecast': 0, 'confidence': 'low'}
        
        # Calculate average daily revenue
        daily_revenues = [day['revenue'] for day in historical_revenue['daily_revenue']]
        avg_daily_revenue = sum(daily_revenues) / len(daily_revenues)
        
        # Simple linear trend
        if len(daily_revenues) >= 30:
            recent_avg = sum(daily_revenues[-15:]) / 15
            older_avg = sum(daily_revenues[-30:-15]) / 15
            growth_rate = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        else:
            growth_rate = 0
        
        # Forecast
        forecasted_daily = avg_daily_revenue * (1 + growth_rate)
        forecasted_total = forecasted_daily * days_ahead
        
        confidence = 'high' if len(daily_revenues) >= 60 else 'medium' if len(daily_revenues) >= 30 else 'low'
        
        return {
            'forecast': forecasted_total,
            'daily_average': forecasted_daily,
            'growth_rate': growth_rate * 100,
            'confidence': confidence
        }
    
    def identify_peak_times(self):
        """Identify peak booking times and patterns"""
        queryset = Reservation.objects.all()
        if self.restaurant:
            queryset = queryset.filter(restaurant=self.restaurant)
        
        # Peak hours
        hourly_data = queryset.extra(
            select={'hour': 'EXTRACT(hour FROM time)'}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Peak days of week
        weekly_data = queryset.extra(
            select={'weekday': 'EXTRACT(dow FROM date)'}
        ).values('weekday').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'peak_hours': list(hourly_data[:3]),
            'peak_days': list(weekly_data[:3]),
            'recommendations': self.get_peak_time_recommendations(hourly_data, weekly_data)
        }
    
    def get_optimization_suggestions(self):
        """Generate optimization suggestions based on analytics"""
        suggestions = []
        
        # Analyze no-show rates
        no_show_rate = self.calculate_no_show_rate()
        if no_show_rate > 15:
            suggestions.append({
                'category': 'operations',
                'suggestion': 'Implement confirmation reminders to reduce no-shows',
                'impact': 'high',
                'no_show_rate': no_show_rate
            })
        
        # Analyze cancellation patterns
        cancellation_data = self.analyze_cancellation_patterns()
        if cancellation_data['rate'] > 20:
            suggestions.append({
                'category': 'policy',
                'suggestion': 'Review cancellation policy and implement deposits',
                'impact': 'medium',
                'cancellation_rate': cancellation_data['rate']
            })
        
        # Revenue optimization
        revenue_data = self.get_revenue_analytics()
        if revenue_data['avg_revenue_per_booking'] < 50:
            suggestions.append({
                'category': 'revenue',
                'suggestion': 'Consider implementing minimum spend requirements',
                'impact': 'high',
                'current_avg': revenue_data['avg_revenue_per_booking']
            })
        
        return suggestions
    
    def calculate_no_show_rate(self):
        """Calculate no-show rate for reservations"""
        queryset = Reservation.objects.filter(
            date__lt=timezone.now().date()
        )
        if self.restaurant:
            queryset = queryset.filter(restaurant=self.restaurant)
        
        total_reservations = queryset.count()
        no_shows = queryset.filter(status='no_show').count()
        
        return (no_shows / total_reservations * 100) if total_reservations > 0 else 0
    
    def analyze_cancellation_patterns(self):
        """Analyze cancellation patterns and timing"""
        queryset = Reservation.objects.filter(status='cancelled')
        if self.restaurant:
            queryset = queryset.filter(restaurant=self.restaurant)
        
        total_reservations = Reservation.objects.all()
        if self.restaurant:
            total_reservations = total_reservations.filter(restaurant=self.restaurant)
        
        cancellation_rate = (queryset.count() / total_reservations.count() * 100) if total_reservations.count() > 0 else 0
        
        # Analyze timing of cancellations
        cancellation_timing = queryset.extra(
            select={
                'hours_before': 'EXTRACT(EPOCH FROM (date + time - created_at)) / 3600'
            }
        ).values('hours_before').annotate(
            count=Count('id')
        )
        
        return {
            'rate': cancellation_rate,
            'timing_patterns': list(cancellation_timing),
            'total_cancelled': queryset.count()
        }

class RealtimeAnalytics:
    """Real-time analytics for live dashboard"""
    
    def __init__(self, restaurant=None):
        self.restaurant = restaurant
    
    def get_live_stats(self):
        """Get real-time statistics"""
        today = timezone.now().date()
        
        queryset = Reservation.objects.filter(date=today)
        if self.restaurant:
            queryset = queryset.filter(restaurant=self.restaurant)
        
        return {
            'today_bookings': queryset.count(),
            'confirmed_today': queryset.filter(status='confirmed').count(),
            'pending_today': queryset.filter(status='pending').count(),
            'cancelled_today': queryset.filter(status='cancelled').count(),
            'revenue_today': queryset.filter(
                payment__status='completed'
            ).aggregate(
                total=Sum('payment__amount')
            )['total'] or 0,
            'avg_party_size_today': queryset.aggregate(
                avg=Avg('number_of_guests')
            )['avg'] or 0,
            'next_reservation': queryset.filter(
                time__gt=timezone.now().time(),
                status='confirmed'
            ).order_by('time').first()
        }
    
    def get_availability_heatmap(self, date=None):
        """Generate availability heatmap for a specific date"""
        if not date:
            date = timezone.now().date()
        
        if not self.restaurant:
            return {}
        
        # Get all time slots (9 AM to 11 PM, 30-minute intervals)
        time_slots = []
        for hour in range(9, 23):
            for minute in [0, 30]:
                time_slots.append(f"{hour:02d}:{minute:02d}")
        
        # Get reservations for the date
        reservations = Reservation.objects.filter(
            restaurant=self.restaurant,
            date=date,
            status__in=['confirmed', 'pending']
        )
        
        # Calculate availability for each time slot
        heatmap_data = []
        total_tables = self.restaurant.tables.count()
        
        for time_slot in time_slots:
            hour, minute = map(int, time_slot.split(':'))
            slot_time = timezone.datetime.strptime(time_slot, '%H:%M').time()
            
            booked_tables = reservations.filter(time=slot_time).count()
            available_tables = total_tables - booked_tables
            availability_percentage = (available_tables / total_tables * 100) if total_tables > 0 else 0
            
            heatmap_data.append({
                'time': time_slot,
                'available_tables': available_tables,
                'booked_tables': booked_tables,
                'availability_percentage': availability_percentage
            })
        
        return {
            'date': date.isoformat(),
            'heatmap': heatmap_data,
            'total_tables': total_tables
        }
