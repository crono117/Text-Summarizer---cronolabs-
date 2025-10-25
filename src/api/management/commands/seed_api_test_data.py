from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from api.models import APIKey
from billing.models import Plan, Subscription
from accounts.models import User, CustomerAccount


class Command(BaseCommand):
    help = 'Seeds test data for WordPress integration API testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate all test data (deletes existing test users)',
        )

    def handle(self, *args, **options):
        """Create test users, API keys, subscriptions, and usage quotas"""

        force = options.get('force', False)

        # Test user data
        test_users_data = [
            {
                'email': 'test_free@summasaas.com',
                'username': 'test_free',
                'password': 'testpass123',
                'plan': 'FREE',
                'chars_used': 5000,
            },
            {
                'email': 'test_plus@summasaas.com',
                'username': 'test_plus',
                'password': 'testpass123',
                'plan': 'PLUS',
                'chars_used': 50000,
            },
            {
                'email': 'test_pro@summasaas.com',
                'username': 'test_pro',
                'password': 'testpass123',
                'plan': 'PRO',
                'chars_used': 100000,
            },
            {
                'email': 'test_enterprise@summasaas.com',
                'username': 'test_enterprise',
                'password': 'testpass123',
                'plan': 'ENTERPRISE',
                'chars_used': 500000,
            },
        ]

        # Check if test data already exists
        existing_users = User.objects.filter(
            email__in=[data['email'] for data in test_users_data]
        )

        if existing_users.exists() and not force:
            self.stdout.write(
                self.style.WARNING(
                    f"\nTest data already exists ({existing_users.count()} users found)."
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    "Use --force flag to recreate all test data.\n"
                )
            )
            # Display existing API keys
            self._display_existing_api_keys(existing_users)
            return

        # Delete existing test data if force flag is set
        if force and existing_users.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Deleting {existing_users.count()} existing test users..."
                )
            )
            existing_users.delete()

        # Ensure plans exist
        plans = {}
        for plan_code in ['FREE', 'PLUS', 'PRO', 'ENTERPRISE']:
            try:
                plans[plan_code] = Plan.objects.get(code=plan_code)
            except Plan.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"\nError: Plan '{plan_code}' does not exist. "
                        f"Run 'python manage.py seed_plans' first.\n"
                    )
                )
                return

        # Create test users
        created_users = []
        api_keys_info = []

        now = timezone.now()
        current_period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_period_end = (current_period_start + relativedelta(months=1)) - timedelta(seconds=1)
        reset_date = (now + relativedelta(months=1)).replace(day=1).date()

        self.stdout.write("\n" + "="*70)
        self.stdout.write("Creating Test Users and API Keys")
        self.stdout.write("="*70 + "\n")

        for user_data in test_users_data:
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
            )

            # Get plan
            plan = plans[user_data['plan']]

            # Set user's current plan and usage
            user.current_plan = plan.code
            user.monthly_char_used = user_data['chars_used']
            user.monthly_requests_used = 0
            user.save(update_fields=['current_plan', 'monthly_char_used', 'monthly_requests_used'])

            created_users.append(user)

            # Create CustomerAccount
            account = CustomerAccount.objects.create(
                name=f"{user_data['username']}'s Account",
                owner=user,
                is_active=True,
            )

            # Create subscription linked to the account
            subscription = Subscription.objects.create(
                account=account,
                plan=plan,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                is_trial=False,
                is_canceled=False,
            )

            # Create API key
            api_key = APIKey.objects.create(
                user=user,
                name="WordPress Test Key",
                is_active=True,
            )

            # Calculate usage percentage
            usage_percentage = (user_data['chars_used'] / plan.char_limit) * 100

            # Store API key info for display
            api_keys_info.append({
                'email': user_data['email'],
                'plan': user_data['plan'],
                'api_key': api_key.key,
                'chars_used': user_data['chars_used'],
                'char_limit': plan.char_limit,
                'usage_percentage': usage_percentage,
            })

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created user: {user_data['email']} ({user_data['plan']} plan)"
                )
            )

        # Display summary
        self.stdout.write("\n" + "="*70)
        self.stdout.write("Test Data Created Successfully")
        self.stdout.write("="*70 + "\n")

        self.stdout.write(f"\nTotal users created: {len(created_users)}")
        self.stdout.write(f"Subscription period: {current_period_start.date()} to {current_period_end.date()}")
        self.stdout.write(f"Quota reset date: {reset_date}\n")

        # Display API keys and credentials
        self.stdout.write("\n" + "="*70)
        self.stdout.write("API Keys for Testing")
        self.stdout.write("="*70 + "\n")

        for info in api_keys_info:
            self.stdout.write(
                self.style.SUCCESS(f"\n{info['plan']} Plan ({info['email']})")
            )
            self.stdout.write(f"  Password: testpass123")
            self.stdout.write(f"  API Key: {info['api_key']}")
            self.stdout.write(
                f"  Usage: {info['chars_used']:,} / {info['char_limit']:,} chars "
                f"({info['usage_percentage']:.1f}%)"
            )

        self.stdout.write("\n" + "="*70)
        self.stdout.write("WordPress Plugin Configuration")
        self.stdout.write("="*70 + "\n")
        self.stdout.write("\nUse any of the API keys above in your WordPress plugin:")
        self.stdout.write("  - API Endpoint: http://localhost:8000/api/v1/")
        self.stdout.write("  - Add API key to the 'X-API-Key' header")
        self.stdout.write("\nExample curl command:")
        self.stdout.write(f"""
  curl -X POST http://localhost:8000/api/v1/summarize/ \\
    -H "X-API-Key: {api_keys_info[0]['api_key']}" \\
    -H "Content-Type: application/json" \\
    -d '{{"text": "Your text to summarize here...", "method": "extractive"}}'
""")

        self.stdout.write("="*70 + "\n")

    def _display_existing_api_keys(self, users):
        """Display API keys for existing test users"""
        self.stdout.write("\n" + "="*70)
        self.stdout.write("Existing Test Users and API Keys")
        self.stdout.write("="*70 + "\n")

        for user in users:
            # Get user's subscription and plan using new architecture
            try:
                account = user.owned_accounts.first() or (
                    user.account_memberships.first().account
                    if user.account_memberships.exists()
                    else None
                )
                if account:
                    try:
                        plan = account.subscription.plan
                        plan_name = plan.code
                    except Subscription.DoesNotExist:
                        plan_name = user.current_plan or 'No Plan'
                else:
                    plan_name = user.current_plan or 'No Plan'
            except Exception:
                plan_name = 'No Plan'

            # Get API keys
            api_keys = user.api_keys.filter(is_active=True)

            if api_keys.exists():
                self.stdout.write(
                    self.style.SUCCESS(f"\n{user.email} ({plan_name} plan)")
                )
                for api_key in api_keys:
                    self.stdout.write(f"  API Key: {api_key.key}")
                    self.stdout.write(f"  Key Name: {api_key.name}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"\n{user.email} - No active API keys")
                )

        self.stdout.write("\n" + "="*70 + "\n")
