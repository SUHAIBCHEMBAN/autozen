"""
Management command to initialize the payment system with default configurations
"""

from django.core.management.base import BaseCommand
from payment.utils import initialize_payment_system


class Command(BaseCommand):
    help = 'Initialize the payment system with default configurations'

    def handle(self, *args, **options):
        self.stdout.write('Initializing payment system...')
        
        # Initialize payment system
        dummy_config = initialize_payment_system()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized payment system. '
                f'Dummy configuration: {dummy_config.gateway} (Active: {dummy_config.is_active})'
            )
        )
        
        self.stdout.write(
            'You can now configure real payment gateways through the admin interface.'
        )