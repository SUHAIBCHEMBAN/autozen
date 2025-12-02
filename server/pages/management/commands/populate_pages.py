from django.core.management.base import BaseCommand
from pages.models import Page, FAQ

class Command(BaseCommand):
    help = 'Populate database with initial pages and FAQs'

    def handle(self, *args, **options):
        # Create sample pages
        pages_data = [
            {
                'title': 'About Us',
                'content': 'Welcome to our company. We are dedicated to providing the best service...',
                'page_type': 'about',
                'is_active': True
            },
            {
                'title': 'Terms and Conditions',
                'content': 'These terms and conditions outline the rules and regulations for the use of our website...',
                'page_type': 'terms',
                'is_active': True
            },
            {
                'title': 'Return, Refund and Safety Tips',
                'content': 'Our return and refund policy provides guidelines on how to return items...',
                'page_type': 'refund',
                'is_active': True
            },
            {
                'title': 'Privacy Policy',
                'content': 'This Privacy Policy describes how we collect, use, and protect your personal information...',
                'page_type': 'privacy',
                'is_active': True
            },
            {
                'title': 'Frequently Asked Questions',
                'content': 'Find answers to common questions about our services...',
                'page_type': 'faq',
                'is_active': True
            }
        ]

        for page_data in pages_data:
            page, created = Page.objects.get_or_create(
                page_type=page_data['page_type'],
                defaults=page_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {page.title} page')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'{page.title} page already exists')
                )

        # Create sample FAQs
        faqs_data = [
            {
                'question': 'How do I create an account?',
                'answer': 'To create an account, click on the "Sign Up" button and fill in your details.',
                'order': 1,
                'is_active': True
            },
            {
                'question': 'What payment methods do you accept?',
                'answer': 'We accept all major credit cards including Visa, MasterCard, and American Express.',
                'order': 2,
                'is_active': True
            },
            {
                'question': 'How long does delivery take?',
                'answer': 'Delivery typically takes 3-5 business days depending on your location.',
                'order': 3,
                'is_active': True
            },
            {
                'question': 'Can I return my purchase?',
                'answer': 'Yes, you can return unused items within 30 days of purchase.',
                'order': 4,
                'is_active': True
            }
        ]

        for faq_data in faqs_data:
            faq, created = FAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created FAQ: {faq.question}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'FAQ "{faq.question}" already exists')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated pages and FAQs')
        )