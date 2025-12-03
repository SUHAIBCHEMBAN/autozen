"""
Management command to initialize the landing page with sample data
"""

from django.core.management.base import BaseCommand
from landing.utils import initialize_landing_page
from landing.models import HeroBanner, CategorySection, Testimonial


class Command(BaseCommand):
    help = 'Initialize the landing page with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing landing page with sample data...')

        # Initialize landing page
        config = initialize_landing_page()
        self.stdout.write(f"Created/updated landing page configuration: {config.site_title}")

        # Create sample testimonials if none exist
        if not Testimonial.objects.exists():
            testimonials_data = [
                {
                    'name': 'John Smith',
                    'role': 'Car Enthusiast',
                    'company': 'Auto Club',
                    'content': 'The quality of parts from AutoZen is exceptional. My Toyota runs smoother than ever!',
                    'rating': 5,
                    'order': 1
                },
                {
                    'name': 'Sarah Johnson',
                    'role': 'Fleet Manager',
                    'company': 'City Transport',
                    'content': 'We\'ve been ordering from AutoZen for over a year now. Reliable service and great prices.',
                    'rating': 4,
                    'order': 2
                },
                {
                    'name': 'Mike Williams',
                    'role': 'Mechanic',
                    'company': 'Precision Auto Repair',
                    'content': 'As a mechanic, I recommend AutoZen to all my customers. Their parts are always in stock.',
                    'rating': 5,
                    'order': 3
                }
            ]
            
            for testimonial_data in testimonials_data:
                testimonial = Testimonial.objects.create(**testimonial_data)
                self.stdout.write(f"Created testimonial: {testimonial.name}")

        self.stdout.write(
            self.style.SUCCESS('Landing page initialized successfully')
        )