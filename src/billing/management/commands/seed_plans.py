from django.core.management.base import BaseCommand
from billing.models import Plan


class Command(BaseCommand):
    help = 'Seeds the database with subscription plans for SummaSaaS'

    def handle(self, *args, **options):
        """Create or update subscription plans"""

        plans_data = [
            {
                'name': 'FREE',
                'monthly_price': 0.00,
                'character_limit': 10000,
                'api_rate_limit_per_hour': 10,
                'features': {
                    'basic_summarization': True,
                    'save_summaries': False,
                    'api_access': False,
                    'priority_support': False,
                    'custom_models': False,
                }
            },
            {
                'name': 'STARTER',
                'monthly_price': 9.99,
                'character_limit': 100000,
                'api_rate_limit_per_hour': 100,
                'features': {
                    'basic_summarization': True,
                    'save_summaries': True,
                    'api_access': True,
                    'priority_support': False,
                    'custom_models': False,
                }
            },
            {
                'name': 'PRO',
                'monthly_price': 29.99,
                'character_limit': 1000000,
                'api_rate_limit_per_hour': 1000,
                'features': {
                    'basic_summarization': True,
                    'save_summaries': True,
                    'api_access': True,
                    'priority_support': True,
                    'custom_models': False,
                    'batch_processing': True,
                }
            },
            {
                'name': 'ENTERPRISE',
                'monthly_price': 99.99,
                'character_limit': 10000000,
                'api_rate_limit_per_hour': 0,  # 0 means unlimited
                'features': {
                    'basic_summarization': True,
                    'save_summaries': True,
                    'api_access': True,
                    'priority_support': True,
                    'custom_models': True,
                    'batch_processing': True,
                    'dedicated_support': True,
                    'sla_guarantee': True,
                }
            },
        ]

        created_count = 0
        updated_count = 0

        for plan_data in plans_data:
            plan, created = Plan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'monthly_price': plan_data['monthly_price'],
                    'character_limit': plan_data['character_limit'],
                    'api_rate_limit_per_hour': plan_data['api_rate_limit_per_hour'],
                    'features': plan_data['features'],
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created plan: {plan.get_name_display()}")
                )
            else:
                # Update existing plan
                plan.monthly_price = plan_data['monthly_price']
                plan.character_limit = plan_data['character_limit']
                plan.api_rate_limit_per_hour = plan_data['api_rate_limit_per_hour']
                plan.features = plan_data['features']
                plan.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Updated plan: {plan.get_name_display()}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSummary: {created_count} plans created, {updated_count} plans updated"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"Total plans in database: {Plan.objects.count()}")
        )
