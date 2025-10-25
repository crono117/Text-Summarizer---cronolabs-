"""
Comprehensive Model Tests for SummaSaaS Platform
Tests all models, fields, relationships, methods, signals, and validations
"""

import os
import django
import hashlib
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from accounts.models import User, CustomerAccount, AccountMembership
from billing.models import Plan, Subscription
from security.models import AccountSecurityState, UserSession


class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.total = 0

    def test(self, name, fn):
        """Run a test and record result"""
        self.total += 1
        try:
            fn()
            self.passed.append(name)
            print(f"✅ {name}")
            return True
        except AssertionError as e:
            self.failed.append((name, str(e)))
            print(f"❌ {name}: {e}")
            return False
        except Exception as e:
            self.failed.append((name, f"ERROR: {e}"))
            print(f"❌ {name}: ERROR - {e}")
            return False

    def report(self):
        """Print final report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"\nTotal Tests: {self.total}")
        print(f"Passed: {len(self.passed)} ✅")
        print(f"Failed: {len(self.failed)} ❌")
        print(f"Pass Rate: {len(self.passed)/self.total*100:.1f}%")

        if self.failed:
            print("\n" + "-"*80)
            print("FAILED TESTS:")
            print("-"*80)
            for name, error in self.failed:
                print(f"\n❌ {name}")
                print(f"   {error}")

        print("\n" + "="*80)
        if self.failed:
            print("STATUS: FAIL ❌")
        else:
            print("STATUS: PASS ✅")
        print("="*80 + "\n")


results = TestResults()

# Cleanup function
def cleanup_test_data():
    """Delete all test data - accounts first due to PROTECT constraint"""
    # Delete accounts first (this will cascade to subscriptions, memberships, etc)
    CustomerAccount.objects.filter(name__startswith='Test ').delete()
    # Now safe to delete users
    User.objects.filter(username__startswith='test_').delete()
    # Delete test plans
    Plan.objects.filter(code__startswith='TEST_').delete()


print("Starting Comprehensive Model Tests...\n")

# Cleanup any leftover test data from previous runs
print("Cleaning up any leftover test data from previous runs...")
cleanup_test_data()
print("Cleanup complete.\n")

# =============================================================================
# CATEGORY 1: MODEL FIELD TESTS
# =============================================================================
print("\n" + "="*80)
print("CATEGORY 1: MODEL FIELD TESTS")
print("="*80 + "\n")

def test_user_fields():
    """Test all User model fields exist with correct types"""
    user = User.objects.create_user(username='test_user_fields', password='test123')

    # Check field existence
    assert hasattr(user, 'is_staff_support'), "Missing is_staff_support field"
    assert hasattr(user, 'is_superadmin'), "Missing is_superadmin field"
    assert hasattr(user, 'current_plan'), "Missing current_plan field"
    assert hasattr(user, 'monthly_char_used'), "Missing monthly_char_used field"
    assert hasattr(user, 'monthly_requests_used'), "Missing monthly_requests_used field"

    # Check field types
    assert isinstance(user.is_staff_support, bool), "is_staff_support should be bool"
    assert isinstance(user.is_superadmin, bool), "is_superadmin should be bool"
    assert isinstance(user.current_plan, str), "current_plan should be CharField (str)"
    assert isinstance(user.monthly_char_used, int), "monthly_char_used should be BigIntegerField (int)"
    assert isinstance(user.monthly_requests_used, int), "monthly_requests_used should be BigIntegerField (int)"

    # Check defaults
    assert user.is_staff_support == False, "is_staff_support default should be False"
    assert user.is_superadmin == False, "is_superadmin default should be False"
    assert user.current_plan == 'FREE', "current_plan default should be 'FREE'"
    assert user.monthly_char_used == 0, "monthly_char_used default should be 0"
    assert user.monthly_requests_used == 0, "monthly_requests_used default should be 0"

    # Check choices
    field = User._meta.get_field('current_plan')
    choice_values = [c[0] for c in field.choices]
    assert 'FREE' in choice_values, "current_plan should have FREE choice"
    assert 'PLUS' in choice_values, "current_plan should have PLUS choice"
    assert 'PRO' in choice_values, "current_plan should have PRO choice"
    assert 'ENTERPRISE' in choice_values, "current_plan should have ENTERPRISE choice"

    user.delete()

results.test("User model - all fields exist with correct types", test_user_fields)


def test_plan_fields():
    """Test all Plan model fields"""
    plan = Plan.objects.create(
        code='TEST_FREE',
        display_name='Test Free Plan',
        monthly_price_usd=0,
        char_limit=10000,
        req_per_hour=10,
        max_seats=1,
        max_concurrent_sessions=2,
        allow_team_members=False,
        priority_support=False,
        sla=False
    )

    # Check required fields exist
    assert hasattr(plan, 'code'), "Missing code field"
    assert hasattr(plan, 'display_name'), "Missing display_name field"
    assert hasattr(plan, 'monthly_price_usd'), "Missing monthly_price_usd field"
    assert hasattr(plan, 'stripe_price_id'), "Missing stripe_price_id field"
    assert hasattr(plan, 'char_limit'), "Missing char_limit field (not character_limit!)"
    assert hasattr(plan, 'req_per_hour'), "Missing req_per_hour field"
    assert hasattr(plan, 'max_seats'), "Missing max_seats field"
    assert hasattr(plan, 'max_concurrent_sessions'), "Missing max_concurrent_sessions field"
    assert hasattr(plan, 'allow_team_members'), "Missing allow_team_members field"
    assert hasattr(plan, 'priority_support'), "Missing priority_support field"
    assert hasattr(plan, 'sla'), "Missing sla field"

    # Check field types
    assert isinstance(plan.char_limit, int), "char_limit should be BigIntegerField (int)"
    assert isinstance(plan.req_per_hour, int), "req_per_hour should be IntegerField (int)"

    plan.delete()

results.test("Plan model - all fields exist with correct types", test_plan_fields)


def test_customer_account_fields():
    """Test CustomerAccount fields"""
    user = User.objects.create_user(username='test_account_owner', password='test123')
    account = CustomerAccount.objects.create(
        name='Test Account',
        owner=user,
        is_active=True
    )

    # Check required fields
    assert hasattr(account, 'name'), "Missing name field"
    assert hasattr(account, 'owner'), "Missing owner field"
    assert hasattr(account, 'stripe_customer_id'), "Missing stripe_customer_id field"
    assert hasattr(account, 'is_active'), "Missing is_active field"

    # Check field types
    assert isinstance(account.is_active, bool), "is_active should be bool"
    assert account.is_active == True, "is_active default should be True"

    account.delete()
    user.delete()

results.test("CustomerAccount model - all fields exist", test_customer_account_fields)


def test_subscription_fields():
    """Test Subscription fields"""
    user = User.objects.create_user(username='test_sub_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Sub Account', owner=user)
    plan = Plan.objects.create(
        code='TEST_PLUS',
        display_name='Test Plus',
        monthly_price_usd=9.99,
        char_limit=100000,
        req_per_hour=100,
        max_seats=1,
        max_concurrent_sessions=2,
        allow_team_members=False
    )

    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    # Check fields
    assert hasattr(sub, 'account'), "Missing account field"
    assert hasattr(sub, 'plan'), "Missing plan field"
    assert hasattr(sub, 'stripe_subscription_id'), "Missing stripe_subscription_id field"
    assert hasattr(sub, 'current_period_start'), "Missing current_period_start field"
    assert hasattr(sub, 'current_period_end'), "Missing current_period_end field"
    assert hasattr(sub, 'is_trial'), "Missing is_trial field (should be BooleanField!)"
    assert hasattr(sub, 'is_canceled'), "Missing is_canceled field (should be BooleanField!)"

    # Check field types (should be BooleanField, not CharField!)
    assert isinstance(sub.is_trial, bool), "is_trial should be BooleanField, not CharField"
    assert isinstance(sub.is_canceled, bool), "is_canceled should be BooleanField, not CharField"

    # Check defaults
    assert sub.is_trial == False, "is_trial default should be False"
    assert sub.is_canceled == False, "is_canceled default should be False"

    sub.delete()
    plan.delete()
    account.delete()
    user.delete()

results.test("Subscription model - all fields exist with correct types", test_subscription_fields)


def test_account_membership_fields():
    """Test AccountMembership fields"""
    user1 = User.objects.create_user(username='test_member1', password='test123')
    user2 = User.objects.create_user(username='test_member2', password='test123')
    account = CustomerAccount.objects.create(name='Test Membership Account', owner=user1)

    membership = AccountMembership.objects.create(
        account=account,
        user=user2,
        role='MEMBER'
    )

    # Check fields
    assert hasattr(membership, 'account'), "Missing account field"
    assert hasattr(membership, 'user'), "Missing user field"
    assert hasattr(membership, 'role'), "Missing role field"

    # Check role choices
    assert membership.role == 'MEMBER', "Role should be MEMBER"
    field = AccountMembership._meta.get_field('role')
    role_values = [c[0] for c in field.choices]
    assert 'OWNER' in role_values, "Should have OWNER role"
    assert 'ADMIN' in role_values, "Should have ADMIN role"
    assert 'MEMBER' in role_values, "Should have MEMBER role"
    assert 'READONLY' in role_values, "Should have READONLY role"

    membership.delete()
    account.delete()
    user2.delete()
    user1.delete()

results.test("AccountMembership model - all fields exist", test_account_membership_fields)


def test_account_security_state_fields():
    """Test AccountSecurityState fields"""
    user = User.objects.create_user(username='test_security_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Security Account', owner=user)

    security = AccountSecurityState.objects.create(
        account=account,
        concurrent_session_cap=2
    )

    # Check fields
    assert hasattr(security, 'account'), "Missing account field"
    assert hasattr(security, 'concurrent_session_cap'), "Missing concurrent_session_cap field"
    assert hasattr(security, 'is_temp_locked'), "Missing is_temp_locked field"
    assert hasattr(security, 'last_flag_reason'), "Missing last_flag_reason field"
    assert hasattr(security, 'warning_count'), "Missing warning_count field"

    # Check defaults
    assert security.concurrent_session_cap == 2, "concurrent_session_cap default should be 2"
    assert security.is_temp_locked == False, "is_temp_locked default should be False"
    assert security.warning_count == 0, "warning_count default should be 0"

    security.delete()
    account.delete()
    user.delete()

results.test("AccountSecurityState model - all fields exist", test_account_security_state_fields)


def test_user_session_fields():
    """Test UserSession fields"""
    user = User.objects.create_user(username='test_session_user', password='test123')

    session = UserSession.objects.create(
        user=user,
        session_key='test_session_key_12345'
    )

    # Check fields
    assert hasattr(session, 'user'), "Missing user field"
    assert hasattr(session, 'session_key'), "Missing session_key field"
    assert hasattr(session, 'ip_hash'), "Missing ip_hash field (should be ip_hash, NOT ip_address!)"
    assert hasattr(session, 'user_agent'), "Missing user_agent field"
    assert hasattr(session, 'created_at'), "Missing created_at field"
    assert hasattr(session, 'last_seen_at'), "Missing last_seen_at field"
    assert hasattr(session, 'is_flagged_suspicious'), "Missing is_flagged_suspicious field"

    # Ensure ip_address field does NOT exist (GDPR compliance)
    assert not hasattr(session, 'ip_address'), "Should NOT have ip_address field (use ip_hash instead!)"

    # Check defaults
    assert session.is_flagged_suspicious == False, "is_flagged_suspicious default should be False"

    session.delete()
    user.delete()

results.test("UserSession model - all fields exist (ip_hash not ip_address)", test_user_session_fields)


# =============================================================================
# CATEGORY 2: RELATIONSHIP TESTS
# =============================================================================
print("\n" + "="*80)
print("CATEGORY 2: RELATIONSHIP TESTS")
print("="*80 + "\n")


def test_user_to_customer_account_relationship():
    """Test User → CustomerAccount relationship"""
    user = User.objects.create_user(username='test_rel_user', password='test123')
    account1 = CustomerAccount.objects.create(name='Test Account 1', owner=user)
    account2 = CustomerAccount.objects.create(name='Test Account 2', owner=user)

    # Test forward relationship
    assert account1.owner == user, "Account owner should be user"

    # Test reverse relationship (related_name='owned_accounts')
    owned = user.owned_accounts.all()
    assert owned.count() == 2, "User should own 2 accounts"
    assert account1 in owned, "Account1 should be in owned_accounts"
    assert account2 in owned, "Account2 should be in owned_accounts"

    # Test PROTECT constraint - should not be able to delete user
    try:
        user.delete()
        assert False, "Should not be able to delete user with PROTECT constraint"
    except Exception:
        pass  # Expected

    account1.delete()
    account2.delete()
    user.delete()

results.test("User → CustomerAccount relationship (PROTECT, related_name='owned_accounts')", test_user_to_customer_account_relationship)


def test_subscription_to_account_ontoone():
    """Test Subscription → CustomerAccount OneToOneField"""
    user = User.objects.create_user(username='test_sub_rel_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Sub Rel Account', owner=user)
    plan = Plan.objects.create(
        code='TEST_PRO',
        display_name='Test Pro',
        monthly_price_usd=29.99,
        char_limit=1000000,
        req_per_hour=1000,
        max_seats=5,
        allow_team_members=True
    )

    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    # Test forward relationship
    assert sub.account == account, "Subscription account should match"

    # Test reverse relationship (related_name='subscription' - SINGULAR!)
    assert hasattr(account, 'subscription'), "Account should have 'subscription' (singular)"
    assert account.subscription == sub, "Account.subscription should return subscription"

    # Test OneToOne constraint - can't create second subscription
    try:
        Subscription.objects.create(
            account=account,
            plan=plan,
            current_period_start=now,
            current_period_end=now + timedelta(days=30)
        )
        assert False, "Should not allow 2 subscriptions for same account (OneToOne constraint)"
    except IntegrityError:
        pass  # Expected

    sub.delete()
    plan.delete()
    account.delete()
    user.delete()

results.test("Subscription → Account OneToOne (related_name='subscription')", test_subscription_to_account_ontoone)


def test_subscription_to_plan_relationship():
    """Test Subscription → Plan ForeignKey"""
    user = User.objects.create_user(username='test_plan_rel_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Plan Rel Account', owner=user)
    plan = Plan.objects.create(
        code='TEST_ENT',
        display_name='Test Enterprise',
        monthly_price_usd=99.99,
        char_limit=10000000,
        req_per_hour=10000,
        max_seats=20,
        allow_team_members=True
    )

    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    # Test forward relationship
    assert sub.plan == plan, "Subscription plan should match"

    # Test reverse relationship (related_name='subscriptions')
    assert plan.subscriptions.count() == 1, "Plan should have 1 subscription"
    assert sub in plan.subscriptions.all(), "Subscription should be in plan.subscriptions"

    # Test PROTECT constraint - can't delete plan with active subscriptions
    try:
        plan.delete()
        assert False, "Should not be able to delete plan with PROTECT constraint"
    except Exception:
        pass  # Expected

    sub.delete()
    plan.delete()
    account.delete()
    user.delete()

results.test("Subscription → Plan ForeignKey (PROTECT, related_name='subscriptions')", test_subscription_to_plan_relationship)


def test_account_membership_relationships():
    """Test AccountMembership relationships"""
    user1 = User.objects.create_user(username='test_mem_rel_user1', password='test123')
    user2 = User.objects.create_user(username='test_mem_rel_user2', password='test123')
    account = CustomerAccount.objects.create(name='Test Mem Rel Account', owner=user1)

    mem = AccountMembership.objects.create(
        account=account,
        user=user2,
        role='MEMBER'
    )

    # Test forward relationships
    assert mem.account == account, "Membership account should match"
    assert mem.user == user2, "Membership user should match"

    # Test reverse relationships
    assert account.memberships.count() == 1, "Account should have 1 membership"
    assert mem in account.memberships.all(), "Membership should be in account.memberships"

    assert user2.account_memberships.count() == 1, "User should have 1 account_membership"
    assert mem in user2.account_memberships.all(), "Membership should be in user.account_memberships"

    mem.delete()
    account.delete()
    user2.delete()
    user1.delete()

results.test("AccountMembership relationships (account/user ForeignKeys)", test_account_membership_relationships)


def test_user_session_relationship():
    """Test UserSession → User relationship"""
    user = User.objects.create_user(username='test_sess_rel_user', password='test123')

    sess1 = UserSession.objects.create(user=user, session_key='sess_key_1')
    sess2 = UserSession.objects.create(user=user, session_key='sess_key_2')

    # Test forward relationship
    assert sess1.user == user, "Session user should match"

    # Test reverse relationship (related_name='sessions')
    assert user.sessions.count() == 2, "User should have 2 sessions"
    assert sess1 in user.sessions.all(), "Session1 should be in user.sessions"
    assert sess2 in user.sessions.all(), "Session2 should be in user.sessions"

    sess1.delete()
    sess2.delete()
    user.delete()

results.test("UserSession → User relationship (CASCADE, related_name='sessions')", test_user_session_relationship)


def test_account_security_state_relationship():
    """Test AccountSecurityState → CustomerAccount OneToOne"""
    user = User.objects.create_user(username='test_sec_rel_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Sec Rel Account', owner=user)

    security = AccountSecurityState.objects.create(account=account)

    # Test forward relationship
    assert security.account == account, "Security account should match"

    # Test reverse relationship (related_name='security_state')
    assert hasattr(account, 'security_state'), "Account should have 'security_state'"
    assert account.security_state == security, "Account.security_state should match"

    # Test OneToOne constraint
    try:
        AccountSecurityState.objects.create(account=account)
        assert False, "Should not allow 2 security states for same account"
    except IntegrityError:
        pass  # Expected

    security.delete()
    account.delete()
    user.delete()

results.test("AccountSecurityState → Account OneToOne (related_name='security_state')", test_account_security_state_relationship)


# =============================================================================
# CATEGORY 3: METHOD TESTS
# =============================================================================
print("\n" + "="*80)
print("CATEGORY 3: METHOD TESTS")
print("="*80 + "\n")


def test_user_is_paying_customer_method():
    """Test User.is_paying_customer() method"""
    user_free = User.objects.create_user(username='test_free_user', password='test123', current_plan='FREE')
    user_plus = User.objects.create_user(username='test_plus_user', password='test123', current_plan='PLUS')
    user_pro = User.objects.create_user(username='test_pro_user', password='test123', current_plan='PRO')
    user_ent = User.objects.create_user(username='test_ent_user', password='test123', current_plan='ENTERPRISE')

    assert user_free.is_paying_customer() == False, "FREE user should not be paying customer"
    assert user_plus.is_paying_customer() == True, "PLUS user should be paying customer"
    assert user_pro.is_paying_customer() == True, "PRO user should be paying customer"
    assert user_ent.is_paying_customer() == True, "ENTERPRISE user should be paying customer"

    user_free.delete()
    user_plus.delete()
    user_pro.delete()
    user_ent.delete()

results.test("User.is_paying_customer() method works correctly", test_user_is_paying_customer_method)


def test_user_is_internal_method():
    """Test User.is_internal() method"""
    regular_user = User.objects.create_user(username='test_regular', password='test123')
    support_user = User.objects.create_user(username='test_support', password='test123', is_staff_support=True)
    admin_user = User.objects.create_user(username='test_admin', password='test123', is_superadmin=True)
    both_user = User.objects.create_user(username='test_both', password='test123', is_staff_support=True, is_superadmin=True)

    assert regular_user.is_internal() == False, "Regular user should not be internal"
    assert support_user.is_internal() == True, "Support staff should be internal"
    assert admin_user.is_internal() == True, "Superadmin should be internal"
    assert both_user.is_internal() == True, "User with both flags should be internal"

    regular_user.delete()
    support_user.delete()
    admin_user.delete()
    both_user.delete()

results.test("User.is_internal() method works correctly", test_user_is_internal_method)


def test_subscription_is_active_method():
    """Test Subscription.is_active() method"""
    user = User.objects.create_user(username='test_active_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Active Account', owner=user, is_active=True)
    plan = Plan.objects.create(
        code='TEST_ACTIVE',
        display_name='Test Active',
        monthly_price_usd=9.99,
        char_limit=100000,
        req_per_hour=100,
        max_seats=1
    )

    now = timezone.now()

    # Active subscription
    sub_active = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now - timedelta(days=15),
        current_period_end=now + timedelta(days=15),
        is_canceled=False
    )
    assert sub_active.is_active() == True, "Non-canceled, non-expired subscription should be active"

    # Update to canceled
    sub_active.is_canceled = True
    sub_active.save()
    assert sub_active.is_active() == False, "Canceled subscription should not be active"

    # Reset and test expired
    sub_active.is_canceled = False
    sub_active.current_period_end = now - timedelta(days=1)
    sub_active.save()
    assert sub_active.is_active() == False, "Expired subscription should not be active"

    # Reset and test inactive account
    sub_active.current_period_end = now + timedelta(days=15)
    sub_active.save()
    account.is_active = False
    account.save()
    sub_active.refresh_from_db()
    assert sub_active.is_active() == False, "Subscription with inactive account should not be active"

    sub_active.delete()
    plan.delete()
    account.delete()
    user.delete()

results.test("Subscription.is_active() method works correctly", test_subscription_is_active_method)


def test_user_session_hash_ip_method():
    """Test UserSession.hash_ip() static method"""
    # Test IP hashing
    ip1 = "192.168.1.1"
    ip2 = "10.0.0.1"

    hash1 = UserSession.hash_ip(ip1)
    hash2 = UserSession.hash_ip(ip2)

    # Should return SHA256 hash (64 character hex string)
    assert len(hash1) == 64, "IP hash should be 64 characters (SHA256)"
    assert len(hash2) == 64, "IP hash should be 64 characters (SHA256)"

    # Same IP should produce same hash
    assert UserSession.hash_ip(ip1) == hash1, "Same IP should produce same hash"

    # Different IPs should produce different hashes
    assert hash1 != hash2, "Different IPs should produce different hashes"

    # Verify it's actually SHA256
    expected_hash = hashlib.sha256(ip1.encode()).hexdigest()
    assert hash1 == expected_hash, "Should use SHA256 hash"

results.test("UserSession.hash_ip() method works correctly", test_user_session_hash_ip_method)


# =============================================================================
# CATEGORY 4: SIGNAL TESTS
# =============================================================================
print("\n" + "="*80)
print("CATEGORY 4: SIGNAL TESTS")
print("="*80 + "\n")


def test_subscription_signal_updates_user_plan():
    """Test that creating/updating Subscription updates User.current_plan"""
    user = User.objects.create_user(
        username='test_signal_user',
        password='test123',
        current_plan='FREE'
    )
    account = CustomerAccount.objects.create(name='Test Signal Account', owner=user)

    # Get or create PLUS plan
    plan_plus, _ = Plan.objects.get_or_create(
        code='PLUS',
        defaults={
            'display_name': 'Plus Plan',
            'monthly_price_usd': 9.99,
            'char_limit': 100000,
            'req_per_hour': 100,
            'max_seats': 1
        }
    )

    # Create subscription - should trigger signal
    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan_plus,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    # Refresh user from DB to see signal changes
    user.refresh_from_db()

    assert user.current_plan == 'PLUS', "Signal should update user.current_plan to PLUS"

    # Get or create PRO plan
    plan_pro, _ = Plan.objects.get_or_create(
        code='PRO',
        defaults={
            'display_name': 'Pro Plan',
            'monthly_price_usd': 29.99,
            'char_limit': 1000000,
            'req_per_hour': 1000,
            'max_seats': 5,
            'allow_team_members': True
        }
    )

    sub.plan = plan_pro
    sub.save()

    user.refresh_from_db()
    assert user.current_plan == 'PRO', "Signal should update user.current_plan to PRO"

    sub.delete()
    account.delete()
    user.delete()

results.test("Subscription signal updates User.current_plan (PLUS → PRO)", test_subscription_signal_updates_user_plan)


def test_subscription_signal_all_plan_codes():
    """Test signal with all 4 plan codes"""
    user = User.objects.create_user(
        username='test_all_plans_user',
        password='test123',
        current_plan='FREE'
    )
    account = CustomerAccount.objects.create(name='Test All Plans Account', owner=user)

    plans = {}
    for code, price, char_limit in [
        ('FREE', 0, 10000),
        ('PLUS', 9.99, 100000),
        ('PRO', 29.99, 1000000),
        ('ENTERPRISE', 99.99, 10000000)
    ]:
        plan, _ = Plan.objects.get_or_create(
            code=code,
            defaults={
                'display_name': f'{code} Plan',
                'monthly_price_usd': price,
                'char_limit': char_limit,
                'req_per_hour': 100,
                'max_seats': 1
            }
        )
        plans[code] = plan

    now = timezone.now()

    # Test each plan
    for code in ['FREE', 'PLUS', 'PRO', 'ENTERPRISE']:
        # Delete existing subscription if any
        Subscription.objects.filter(account=account).delete()

        # Create new subscription
        sub = Subscription.objects.create(
            account=account,
            plan=plans[code],
            current_period_start=now,
            current_period_end=now + timedelta(days=30)
        )

        user.refresh_from_db()
        assert user.current_plan == code, f"Signal should update user.current_plan to {code}"

    # Cleanup
    Subscription.objects.filter(account=account).delete()
    account.delete()
    user.delete()

results.test("Subscription signal works with all plan codes (FREE/PLUS/PRO/ENTERPRISE)", test_subscription_signal_all_plan_codes)


# =============================================================================
# CATEGORY 5: VALIDATION TESTS
# =============================================================================
print("\n" + "="*80)
print("CATEGORY 5: VALIDATION TESTS")
print("="*80 + "\n")


def test_account_membership_seat_limit_validation():
    """Test AccountMembership.clean() enforces seat limits"""
    user1 = User.objects.create_user(username='test_seat_owner', password='test123')
    user2 = User.objects.create_user(username='test_seat_member1', password='test123')
    user3 = User.objects.create_user(username='test_seat_member2', password='test123')

    account = CustomerAccount.objects.create(name='Test Seat Account', owner=user1)

    # Create plan with max_seats=1
    plan = Plan.objects.create(
        code='TEST_SEAT',
        display_name='Test Seat',
        monthly_price_usd=9.99,
        char_limit=100000,
        req_per_hour=100,
        max_seats=1  # Only 1 seat!
    )

    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    # First member should be OK
    mem1 = AccountMembership(account=account, user=user2, role='MEMBER')
    mem1.clean()  # Should not raise
    mem1.save()

    # Second member should fail (exceeds max_seats=1)
    mem2 = AccountMembership(account=account, user=user3, role='MEMBER')
    try:
        mem2.clean()
        assert False, "Should raise ValidationError when exceeding seat limit"
    except ValidationError as e:
        assert 'max seats' in str(e).lower(), "Error should mention max seats"

    mem1.delete()
    sub.delete()
    plan.delete()
    account.delete()
    user3.delete()
    user2.delete()
    user1.delete()

results.test("AccountMembership.clean() enforces seat limits", test_account_membership_seat_limit_validation)


def test_unique_constraints():
    """Test unique constraints"""
    # Plan.code should be unique
    plan1 = Plan.objects.create(
        code='TEST_UNIQUE',
        display_name='Test Unique 1',
        monthly_price_usd=9.99,
        char_limit=100000,
        req_per_hour=100,
        max_seats=1
    )

    try:
        plan2 = Plan.objects.create(
            code='TEST_UNIQUE',  # Duplicate!
            display_name='Test Unique 2',
            monthly_price_usd=19.99,
            char_limit=200000,
            req_per_hour=200,
            max_seats=2
        )
        assert False, "Should not allow duplicate Plan.code"
    except IntegrityError:
        pass  # Expected

    plan1.delete()

    # UserSession.session_key should be unique
    user = User.objects.create_user(username='test_unique_session', password='test123')
    sess1 = UserSession.objects.create(user=user, session_key='unique_key_123')

    try:
        sess2 = UserSession.objects.create(user=user, session_key='unique_key_123')
        assert False, "Should not allow duplicate session_key"
    except IntegrityError:
        pass  # Expected

    sess1.delete()
    user.delete()

results.test("Unique constraints work (Plan.code, UserSession.session_key)", test_unique_constraints)


def test_unique_together_account_membership():
    """Test unique_together constraint on AccountMembership"""
    user1 = User.objects.create_user(username='test_unique_mem1', password='test123')
    user2 = User.objects.create_user(username='test_unique_mem2', password='test123')
    account = CustomerAccount.objects.create(name='Test Unique Mem Account', owner=user1)

    mem1 = AccountMembership.objects.create(account=account, user=user2, role='MEMBER')

    # Try to create duplicate membership
    try:
        mem2 = AccountMembership.objects.create(account=account, user=user2, role='ADMIN')
        assert False, "Should not allow duplicate (account, user) combination"
    except IntegrityError:
        pass  # Expected

    mem1.delete()
    account.delete()
    user2.delete()
    user1.delete()

results.test("AccountMembership unique_together (account, user) constraint", test_unique_together_account_membership)


# =============================================================================
# CATEGORY 6: EDGE CASES & ERROR HANDLING
# =============================================================================
print("\n" + "="*80)
print("CATEGORY 6: EDGE CASES & ERROR HANDLING")
print("="*80 + "\n")


def test_delete_user_with_owned_account_fails():
    """Test that deleting User with owned accounts fails (PROTECT)"""
    user = User.objects.create_user(username='test_protect_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Protect Account', owner=user)

    try:
        user.delete()
        assert False, "Should not be able to delete user that owns accounts (PROTECT)"
    except Exception:
        pass  # Expected

    # Should work after deleting account
    account.delete()
    user.delete()  # Now should succeed

results.test("Cannot delete User that owns CustomerAccount (PROTECT)", test_delete_user_with_owned_account_fails)


def test_delete_plan_with_subscriptions_fails():
    """Test that deleting Plan with subscriptions fails (PROTECT)"""
    user = User.objects.create_user(username='test_plan_protect_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Plan Protect Account', owner=user)
    plan = Plan.objects.create(
        code='TEST_PROTECT',
        display_name='Test Protect',
        monthly_price_usd=9.99,
        char_limit=100000,
        req_per_hour=100,
        max_seats=1
    )

    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    try:
        plan.delete()
        assert False, "Should not be able to delete plan with subscriptions (PROTECT)"
    except Exception:
        pass  # Expected

    # Should work after deleting subscription
    sub.delete()
    plan.delete()  # Now should succeed
    account.delete()
    user.delete()

results.test("Cannot delete Plan with active Subscriptions (PROTECT)", test_delete_plan_with_subscriptions_fails)


def test_two_subscriptions_per_account_fails():
    """Test OneToOne constraint - can't have 2 subscriptions per account"""
    user = User.objects.create_user(username='test_two_sub_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Two Sub Account', owner=user)
    plan1 = Plan.objects.create(
        code='TEST_TWO_1',
        display_name='Test Two 1',
        monthly_price_usd=9.99,
        char_limit=100000,
        req_per_hour=100,
        max_seats=1
    )
    plan2 = Plan.objects.create(
        code='TEST_TWO_2',
        display_name='Test Two 2',
        monthly_price_usd=19.99,
        char_limit=200000,
        req_per_hour=200,
        max_seats=2
    )

    now = timezone.now()
    sub1 = Subscription.objects.create(
        account=account,
        plan=plan1,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    try:
        sub2 = Subscription.objects.create(
            account=account,
            plan=plan2,
            current_period_start=now,
            current_period_end=now + timedelta(days=30)
        )
        assert False, "Should not allow 2 subscriptions for same account (OneToOne)"
    except IntegrityError:
        pass  # Expected

    sub1.delete()
    plan2.delete()
    plan1.delete()
    account.delete()
    user.delete()

results.test("Cannot create 2 Subscriptions per Account (OneToOne constraint)", test_two_subscriptions_per_account_fails)


def test_canceled_subscription_not_active():
    """Test that canceled subscription is not active"""
    user = User.objects.create_user(username='test_cancel_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Cancel Account', owner=user)
    plan = Plan.objects.create(
        code='TEST_CANCEL',
        display_name='Test Cancel',
        monthly_price_usd=9.99,
        char_limit=100000,
        req_per_hour=100,
        max_seats=1
    )

    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        is_canceled=False
    )

    assert sub.is_active() == True, "Non-canceled subscription should be active"

    sub.is_canceled = True
    sub.save()

    assert sub.is_active() == False, "Canceled subscription should not be active"

    sub.delete()
    plan.delete()
    account.delete()
    user.delete()

results.test("Canceled subscription is not active", test_canceled_subscription_not_active)


def test_expired_subscription_not_active():
    """Test that expired subscription is not active"""
    user = User.objects.create_user(username='test_expire_user', password='test123')
    account = CustomerAccount.objects.create(name='Test Expire Account', owner=user)
    plan = Plan.objects.create(
        code='TEST_EXPIRE',
        display_name='Test Expire',
        monthly_price_usd=9.99,
        char_limit=100000,
        req_per_hour=100,
        max_seats=1
    )

    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now - timedelta(days=40),
        current_period_end=now - timedelta(days=10),  # Expired 10 days ago
        is_canceled=False
    )

    assert sub.is_active() == False, "Expired subscription should not be active"

    sub.delete()
    plan.delete()
    account.delete()
    user.delete()

results.test("Expired subscription is not active", test_expired_subscription_not_active)


# =============================================================================
# CATEGORY 7: MULTI-TENANT FLOW TESTS
# =============================================================================
print("\n" + "="*80)
print("CATEGORY 7: MULTI-TENANT FLOW TESTS")
print("="*80 + "\n")


def test_full_multi_tenant_workflow():
    """Test complete multi-tenant workflow"""
    # 1. Create user with FREE plan
    user = User.objects.create_user(
        username='test_workflow_user',
        password='test123',
        current_plan='FREE'
    )
    assert user.current_plan == 'FREE', "User should start with FREE plan"
    assert user.monthly_char_used == 0, "Usage should start at 0"

    # 2. Create CustomerAccount
    account = CustomerAccount.objects.create(
        name='Test Workflow Account',
        owner=user,
        is_active=True
    )

    # 3. Get or create PLUS plan and subscription
    plan, _ = Plan.objects.get_or_create(
        code='PLUS',
        defaults={
            'display_name': 'Plus Plan',
            'monthly_price_usd': 9.99,
            'char_limit': 100000,
            'req_per_hour': 100,
            'max_seats': 1
        }
    )

    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    # 4. Verify signal updated user.current_plan
    user.refresh_from_db()
    assert user.current_plan == 'PLUS', "Signal should update user to PLUS plan"
    assert user.is_paying_customer() == True, "User should be paying customer"

    # 5. Test usage tracking
    user.monthly_char_used = 50000
    user.monthly_requests_used = 50
    user.save()
    user.refresh_from_db()
    assert user.monthly_char_used == 50000, "Usage tracking should work"

    # 6. Create second user and add as member
    user2 = User.objects.create_user(username='test_workflow_member', password='test123')

    # With max_seats=1 and 0 existing members, first member should succeed
    mem = AccountMembership(account=account, user=user2, role='MEMBER')
    mem.clean()  # Should NOT raise (0 members < max_seats=1)
    mem.save()

    # Now try to add a THIRD user (should fail because we'd have 1 existing + 1 new = 2 > max_seats=1)
    user3 = User.objects.create_user(username='test_workflow_member3', password='test123')
    mem2 = AccountMembership(account=account, user=user3, role='MEMBER')
    try:
        mem2.clean()
        assert False, "Should fail seat limit validation (1 existing member, max_seats=1)"
    except ValidationError:
        pass  # Expected

    mem.delete()
    user3.delete()

    # Cleanup
    sub.delete()
    account.delete()
    user2.delete()
    user.delete()

results.test("Full multi-tenant workflow (user → account → subscription → signal)", test_full_multi_tenant_workflow)


def test_team_membership_workflow():
    """Test team membership workflow with PRO plan"""
    # Create owner
    owner = User.objects.create_user(username='test_team_owner', password='test123')
    account = CustomerAccount.objects.create(name='Test Team Account', owner=owner)

    # Get or create PRO plan (max_seats=5, allow_team_members=True)
    plan, _ = Plan.objects.get_or_create(
        code='PRO',
        defaults={
            'display_name': 'Pro Plan',
            'monthly_price_usd': 29.99,
            'char_limit': 1000000,
            'req_per_hour': 1000,
            'max_seats': 5,
            'allow_team_members': True
        }
    )

    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    # Create 5 members (should work)
    members = []
    for i in range(5):
        user = User.objects.create_user(username=f'test_team_member{i}', password='test123')
        mem = AccountMembership(account=account, user=user, role='MEMBER')
        mem.clean()  # Should not raise
        mem.save()
        members.append((user, mem))

    # 6th member should fail
    user6 = User.objects.create_user(username='test_team_member6', password='test123')
    mem6 = AccountMembership(account=account, user=user6, role='MEMBER')
    try:
        mem6.clean()
        assert False, "Should fail seat limit (max 5)"
    except ValidationError:
        pass  # Expected

    # Cleanup
    for user, mem in members:
        mem.delete()
        user.delete()
    user6.delete()
    sub.delete()
    account.delete()
    owner.delete()

results.test("Team membership workflow with seat limits", test_team_membership_workflow)


# =============================================================================
# CATEGORY 8: DATA INTEGRITY TESTS
# =============================================================================
print("\n" + "="*80)
print("CATEGORY 8: DATA INTEGRITY TESTS")
print("="*80 + "\n")


def test_plan_defaults():
    """Test Plan model defaults"""
    plan = Plan.objects.create(
        code='TEST_DEFAULTS',
        display_name='Test Defaults',
        monthly_price_usd=9.99,
        char_limit=100000,
        req_per_hour=100,
        max_seats=1
    )

    # Check defaults
    assert plan.max_concurrent_sessions == 2, "max_concurrent_sessions default should be 2"
    assert plan.allow_team_members == False, "allow_team_members default should be False"
    assert plan.priority_support == False, "priority_support default should be False"
    assert plan.sla == False, "sla default should be False"
    assert plan.stripe_price_id == '', "stripe_price_id default should be empty string"

    plan.delete()

results.test("Plan model defaults are correct", test_plan_defaults)


def test_subscription_defaults():
    """Test Subscription model defaults"""
    user = User.objects.create_user(username='test_sub_defaults', password='test123')
    account = CustomerAccount.objects.create(name='Test Sub Defaults', owner=user)
    plan = Plan.objects.create(
        code='TEST_SUB_DEF',
        display_name='Test',
        monthly_price_usd=9.99,
        char_limit=100000,
        req_per_hour=100,
        max_seats=1
    )

    now = timezone.now()
    sub = Subscription.objects.create(
        account=account,
        plan=plan,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    assert sub.is_trial == False, "is_trial default should be False"
    assert sub.is_canceled == False, "is_canceled default should be False"
    assert sub.stripe_subscription_id == '', "stripe_subscription_id default should be empty"

    sub.delete()
    plan.delete()
    account.delete()
    user.delete()

results.test("Subscription model defaults are correct", test_subscription_defaults)


# =============================================================================
# CATEGORY 9: GDPR COMPLIANCE TESTS
# =============================================================================
print("\n" + "="*80)
print("CATEGORY 9: GDPR COMPLIANCE TESTS")
print("="*80 + "\n")


def test_user_session_stores_hash_not_ip():
    """Test UserSession stores ip_hash, not raw IP"""
    user = User.objects.create_user(username='test_gdpr_user', password='test123')

    ip_address = "192.168.1.100"
    ip_hash = UserSession.hash_ip(ip_address)

    session = UserSession.objects.create(
        user=user,
        session_key='gdpr_test_key',
        ip_hash=ip_hash
    )

    # Verify ip_hash is stored
    assert session.ip_hash == ip_hash, "Should store ip_hash"
    assert len(session.ip_hash) == 64, "ip_hash should be 64 chars (SHA256)"

    # Verify raw IP is NOT stored
    assert not hasattr(session, 'ip_address'), "Should NOT have ip_address field"
    assert ip_address not in str(session.ip_hash), "Raw IP should not be in hash"

    session.delete()
    user.delete()

results.test("UserSession stores ip_hash (SHA256), not raw IP (GDPR)", test_user_session_stores_hash_not_ip)


def test_ip_hash_is_one_way():
    """Test that IP hash cannot be reversed"""
    ip1 = "203.0.113.45"
    hash1 = UserSession.hash_ip(ip1)

    # Hash should be deterministic
    assert UserSession.hash_ip(ip1) == hash1, "Same IP should give same hash"

    # But hash should not contain the IP
    assert ip1 not in hash1, "Hash should not contain original IP"
    assert '203' not in hash1, "Hash should not contain IP segments"

    # Different IPs should give different hashes
    ip2 = "203.0.113.46"
    hash2 = UserSession.hash_ip(ip2)
    assert hash1 != hash2, "Different IPs should give different hashes"

results.test("IP hashing is one-way (cannot reverse to get original IP)", test_ip_hash_is_one_way)


# =============================================================================
# CATEGORY 10: ADMIN INTEGRATION TESTS
# =============================================================================
print("\n" + "="*80)
print("CATEGORY 10: ADMIN INTEGRATION TESTS")
print("="*80 + "\n")


def test_models_registered_in_admin():
    """Test that all models are registered in Django admin"""
    from django.contrib import admin

    # Check User
    assert User in admin.site._registry, "User should be registered in admin"

    # Check CustomerAccount
    assert CustomerAccount in admin.site._registry, "CustomerAccount should be registered in admin"

    # Check AccountMembership
    assert AccountMembership in admin.site._registry, "AccountMembership should be registered in admin"

    # Check Plan
    assert Plan in admin.site._registry, "Plan should be registered in admin"

    # Check Subscription
    assert Subscription in admin.site._registry, "Subscription should be registered in admin"

results.test("All models registered in Django admin", test_models_registered_in_admin)


def test_admin_list_display_fields():
    """Test that admin has proper list_display fields"""
    from django.contrib import admin

    # User admin
    user_admin = admin.site._registry[User]
    assert hasattr(user_admin, 'list_display'), "User admin should have list_display"
    list_display = user_admin.list_display
    assert 'current_plan' in list_display or 'email' in list_display, "User admin should show relevant fields"

    # Plan admin
    plan_admin = admin.site._registry[Plan]
    assert hasattr(plan_admin, 'list_display'), "Plan admin should have list_display"

results.test("Admin interfaces have list_display configured", test_admin_list_display_fields)


# =============================================================================
# FINAL REPORT
# =============================================================================
print("\n\nCleaning up test data...")
cleanup_test_data()

print("\n\nGenerating final report...")
results.report()
