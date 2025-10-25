"""
Management command to seed billing plans with multi-tenant pricing tiers

Usage:
    python manage.py seed_plans
"""

from django.core.management.base import BaseCommand
from billing.models import Plan


class Command(BaseCommand):
    help = 'Seed billing plans with FREE, PLUS, PRO, and ENTERPRISE tiers'

    def handle(self, *args, **options):
        self.stdout.write('Seeding billing plans...')

        plans_data = [
            {
                'code': 'FREE',
                'display_name': 'Free',
                'monthly_price_usd': 0.00,
                'char_limit': 10_000,
                'req_per_hour': 10,
                'max_seats': 1,
                'max_concurrent_sessions': 2,
                'allow_team_members': False,
                'priority_support': False,
                'sla': False,
            },
            {
                'code': 'PLUS',
                'display_name': 'Plus',
                'monthly_price_usd': 9.99,
                'char_limit': 100_000,
                'req_per_hour': 100,
                'max_seats': 1,
                'max_concurrent_sessions': 2,
                'allow_team_members': False,
                'priority_support': False,
                'sla': False,
            },
            {
                'code': 'PRO',
                'display_name': 'Pro',
                'monthly_price_usd': 29.99,
                'char_limit': 1_000_000,
                'req_per_hour': 1000,
                'max_seats': 5,
                'max_concurrent_sessions': 8,
                'allow_team_members': True,
                'priority_support': True,
                'sla': False,
            },
            {
                'code': 'ENTERPRISE',
                'display_name': 'Enterprise',
                'monthly_price_usd': 99.99,
                'char_limit': 10_000_000,
                'req_per_hour': 10000,
                'max_seats': 20,
                'max_concurrent_sessions': 40,
                'allow_team_members': True,
                'priority_support': True,
                'sla': True,
            }
        ]

        created_count = 0
        updated_count = 0

        for plan_data in plans_data:
            plan, created = Plan.objects.update_or_create(
                code=plan_data['code'],
                defaults=plan_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created plan: {plan.display_name} (${plan.monthly_price_usd}/month)')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated plan: {plan.display_name} (${plan.monthly_price_usd}/month)')
                )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Done! Created {created_count} plans, updated {updated_count} plans.'
            )
        )
        self.stdout.write('')

        # Display summary table
        self.stdout.write(self.style.SUCCESS('Plan Summary:'))
        self.stdout.write('─' * 100)
        self.stdout.write(
            f"{'Plan':<12} {'Price':<10} {'Chars/Mo':<15} {'Rate/Hr':<10} {'Seats':<7} {'Sessions':<10}"
        )
        self.stdout.write('─' * 100)

        for plan in Plan.objects.all():
            self.stdout.write(
                f"{plan.display_name:<12} "
                f"${plan.monthly_price_usd:<9} "
                f"{plan.char_limit:>13,}  "
                f"{plan.req_per_hour:>8}  "
                f"{plan.max_seats:>5}  "
                f"{plan.max_concurrent_sessions:>8}"
            )

        self.stdout.write('─' * 100)
