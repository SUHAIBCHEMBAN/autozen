from django.core.management.base import BaseCommand
from pages.models import Page
import json

class Command(BaseCommand):
    help = 'Update pages with structured JSON content'

    def handle(self, *args, **options):
        # Update About page content
        try:
            about_page = Page.objects.get(page_type='about')
            about_content = {
                "subtitle": "We're building the most reliable destination for aftermarket vehicle parts and accessories in India.",
                "badge": "About",
                "story": "AutoZen was started by enthusiasts who wanted better access to dependable parts, transparent pricing, and fast delivery. Today we partner with vetted suppliers and certified installers to keep your vehicle running and looking its best.",
                "mission": "From daily commuters to weekend builds, we obsess over compatibility, safety, and service so you can shop confidently and get back on the road faster.",
                "coverage": "Interior, exterior, lighting, electronics, care & styling, and core auto parts—all under one roof.",
                "promise": "Authentic parts, responsive support, and delivery timelines you can rely on.",
                "highlight": "Trusted",
                "highlights": [
                    {"label": "15+ Warehouses", "body": "Fast delivery across major cities with optimized routes."},
                    {"label": "3,500+ SKUs", "body": "Curated accessories and parts from trusted OEM/ODM partners."},
                    {"label": "24/7 Support", "body": "Friendly experts for fitment, installation, and post-purchase help."}
                ],
                "values": [
                    "Quality-first sourcing with transparent specs and warranties.",
                    "Fitment assurance tailored to your vehicle model and variant.",
                    "Hassle-free returns and proactive order tracking updates."
                ]
            }
            about_page.content = json.dumps(about_content)
            about_page.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {about_page.title} page with structured content')
            )
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('About page not found')
            )

        # Update Terms page content
        try:
            terms_page = Page.objects.get(page_type='terms')
            terms_content = {
                "subtitle": "Our mutual commitments for a reliable, transparent shopping experience.",
                "badge": "Terms",
                "highlight": "Fitment ready",
                "note": "Terms may change as we launch new services. We'll post revisions here with effective dates. Continued use implies acceptance.",
                "commitments": [
                    "Authentic products with clear specifications, warranties, and return eligibility.",
                    "Transparent pricing inclusive of taxes; shipping shown before checkout.",
                    "Service levels for dispatch, tracking, and resolution timelines."
                ],
                "responsibilities": [
                    "Provide accurate vehicle details for fitment assurance.",
                    "Use products as intended; follow installation and safety guidance.",
                    "Respect intellectual property and avoid misuse of the platform."
                ],
                "limitations": [
                    "Liability limited to the order value; indirect or consequential losses are excluded.",
                    "Warranty coverage depends on brand terms; misuse or improper installs are excluded.",
                    "Platform availability may vary during maintenance and upgrades."
                ]
            }
            terms_page.content = json.dumps(terms_content)
            terms_page.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {terms_page.title} page with structured content')
            )
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Terms page not found')
            )

        # Update Privacy page content
        try:
            privacy_page = Page.objects.get(page_type='privacy')
            privacy_content = {
                "subtitle": "Your trust matters. We keep your data lean, encrypted in transit, and shared only when essential to serve you.",
                "badge": "Privacy",
                "highlight": "Operational use only",
                "noteTitle": "Need changes?",
                "note": "Reach us at support@autozen.com for data access, correction, or deletion requests. We respond within 72 hours.",
                "privacyPoints": [
                    "We collect only what's needed to process orders, personalize recommendations, and improve the experience.",
                    "Payment details are processed via PCI-compliant gateways; we never store raw card data.",
                    "You can access, update, or delete your data anytime by contacting support."
                ],
                "dataUsage": [
                    "Order fulfillment: addresses, contact numbers, and preferences.",
                    "Personalization: recent searches, vehicle selections, and wishlist items.",
                    "Security: fraud prevention, device/IP checks, and audit logs."
                ],
                "commitments": [
                    "Cookies limited to session continuity and analytics; opt-out options available.",
                    "Data sharing only with logistics, payments, and vetted partners needed to deliver your order.",
                    "Breach response with clear notifications and remediation steps."
                ],
                "controls": [
                    "Download or delete your profile data on request.",
                    "Manage marketing preferences from your account.",
                    "Unsubscribe links in every campaign email."
                ]
            }
            privacy_page.content = json.dumps(privacy_content)
            privacy_page.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {privacy_page.title} page with structured content')
            )
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Privacy page not found')
            )

        # Update Refund page content
        try:
            refund_page = Page.objects.get(page_type='refund')
            refund_content = {
                "subtitle": "Straightforward returns with safety-first installation guidance.",
                "badge": "Returns",
                "stepsHighlight": "7-day window",
                "safetyHighlight": "Read before install",
                "noteTitle": "Need help?",
                "note": "If a part arrives damaged or doesn't fit, contact support within 48 hours for priority handling. Keep packaging until fitment is confirmed.",
                "returnSteps": [
                    "Initiate a request from your account within 7 days of delivery.",
                    "Share clear photos and order ID for quality checks.",
                    "Pack unused items with original tags, manuals, and accessories.",
                    "Pickup arranged or drop-off guided based on your pincode."
                ],
                "refundRules": [
                    "Refunds processed to the original payment method after inspection.",
                    "COD orders refunded via bank transfer or wallet credit.",
                    "Electricals and bulbs are returnable only if unopened or DOA.",
                    "Custom/painted parts are final sale unless damaged on arrival."
                ],
                "safetyTips": [
                    "Disconnect battery when installing electrical parts.",
                    "Use torque specs for critical fasteners; avoid over-tightening.",
                    "Test fit before painting or removing protective films.",
                    "Seek professional installation for airbags, sensors, and wiring."
                ]
            }
            refund_page.content = json.dumps(refund_content)
            refund_page.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {refund_page.title} page with structured content')
            )
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Refund page not found')
            )

        # Update FAQ page content
        try:
            faq_page = Page.objects.get(page_type='faq')
            faq_content = "Quick answers to the most common questions from AutoZen shoppers."
            faq_page.content = faq_content
            faq_page.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {faq_page.title} page with plain text content')
            )
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('FAQ page not found')
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully updated all pages with structured content')
        )