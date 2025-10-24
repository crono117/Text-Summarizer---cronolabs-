#!/usr/bin/env python
"""
Test script to verify SummaSaaS application is working correctly
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from billing.models import Plan, Subscription
from django.urls import reverse


def test_plans_exist():
    """Test that all plans exist in database"""
    print("\n=== Testing Plans ===")

    expected_plans = ['FREE', 'STARTER', 'PRO', 'ENTERPRISE']
    plans = Plan.objects.all()

    print(f"Total plans in database: {plans.count()}")

    for plan_name in expected_plans:
        try:
            plan = Plan.objects.get(name=plan_name)
            print(f"  PASS: {plan.get_name_display()} - ${plan.monthly_price}/month")
            print(f"        - Character limit: {plan.character_limit:,}")
            print(f"        - Rate limit: {plan.api_rate_limit_per_hour}/hour")
        except Plan.DoesNotExist:
            print(f"  FAIL: Plan {plan_name} does not exist!")
            return False

    return True


def test_url_accessibility():
    """Test that URLs are accessible"""
    print("\n=== Testing URL Accessibility ===")

    from django.conf import settings

    # Temporarily add testserver to ALLOWED_HOSTS
    original_allowed_hosts = settings.ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = ['*']

    client = Client()

    urls_to_test = [
        ('/', 'Home Page', 200),
        ('/billing/pricing/', 'Pricing Page', 200),
        ('/accounts/login/', 'Login Page', 200),
        ('/accounts/signup/', 'Signup Page', 200),
        ('/dashboard/', 'Dashboard (should redirect)', 302),  # Should redirect to login
    ]

    all_passed = True

    for url, description, expected_status in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code == expected_status:
                print(f"  PASS: {description} ({url}) - Status {response.status_code}")
            else:
                print(f"  FAIL: {description} ({url}) - Expected {expected_status}, got {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  ERROR: {description} ({url}) - {str(e)}")
            all_passed = False

    # Restore original ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = original_allowed_hosts

    return all_passed


def test_authentication_redirect():
    """Test that protected pages redirect to login"""
    print("\n=== Testing Authentication ===")

    from django.conf import settings

    # Temporarily add testserver to ALLOWED_HOSTS
    original_allowed_hosts = settings.ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = ['*']

    client = Client()

    # Test unauthenticated access to dashboard
    response = client.get('/dashboard/')
    if response.status_code == 302 and '/accounts/login/' in response.url:
        print(f"  PASS: Dashboard redirects to login for unauthenticated users")
    else:
        print(f"  FAIL: Dashboard should redirect to login, got {response.status_code}")
        settings.ALLOWED_HOSTS = original_allowed_hosts
        return False

    # Test authenticated access
    user = User.objects.get(username='testuser')
    client.force_login(user)

    response = client.get('/dashboard/')
    if response.status_code == 200:
        print(f"  PASS: Dashboard accessible for authenticated users")
    else:
        print(f"  FAIL: Dashboard should be accessible for authenticated users, got {response.status_code}")
        settings.ALLOWED_HOSTS = original_allowed_hosts
        return False

    # Restore original ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = original_allowed_hosts

    return True


def test_test_user():
    """Test that test user exists and has subscription"""
    print("\n=== Testing Test User ===")

    try:
        user = User.objects.get(username='testuser')
        print(f"  PASS: Test user exists - {user.username} ({user.email})")

        subscription = Subscription.objects.filter(user=user, status='active').first()
        if subscription:
            print(f"  PASS: User has active subscription - {subscription.plan.get_name_display()}")
        else:
            print(f"  FAIL: User does not have an active subscription")
            return False

        return True
    except User.DoesNotExist:
        print(f"  FAIL: Test user does not exist!")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("SummaSaaS Application Test Suite")
    print("=" * 60)

    tests = [
        ("Plans Exist", test_plans_exist),
        ("URL Accessibility", test_url_accessibility),
        ("Authentication", test_authentication_redirect),
        ("Test User", test_test_user),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  ERROR in {test_name}: {str(e)}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {test_name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\nAll tests passed! Application is ready.")
        return 0
    else:
        print("\nSome tests failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
