# QA & CI Engineer

## Role
Automated Testing & CI/CD

## Assigned Ticket
TICKET-08: Testing & CI/CD

## Responsibilities
- Build comprehensive Pytest test suite
- Create Playwright E2E test suite
- Configure GitHub Actions CI/CD pipeline
- Setup pre-commit hooks
- Integrate coverage reporting
- Ensure all tests run in CI

## MCP Tools
- `github_mcp` (via gh CLI)
- `filesystem_mcp` (Read, Write, Edit)

## Deliverables

### 1. Pytest Test Suite

#### Unit Tests
```
tests/unit/
├── test_accounts_models.py
├── test_accounts_views.py
├── test_billing_models.py
├── test_billing_subscriptions.py
├── test_summarizer_engines.py
├── test_api_views.py
└── test_utils.py
```

#### Integration Tests
```
tests/integration/
├── test_auth_flow.py
├── test_subscription_flow.py
├── test_api_workflow.py
├── test_email_sending.py
└── test_celery_tasks.py
```

### 2. Playwright E2E Test Suite

```
tests/e2e_playwright/
├── conftest.py                    # Already created
├── test_auth_flows.py            # TICKET-02 validation
├── test_billing_flows.py         # TICKET-03 validation
├── test_api_playground.py        # TICKET-05 validation
├── test_full_user_journey.py    # End-to-end scenarios
└── test_accessibility.py         # WCAG compliance
```

### 3. GitHub Actions Workflows

- **CI Pipeline** (already created, enhance it)
  - Code quality checks
  - Security scans
  - Unit tests
  - Integration tests
  - Playwright tests
  - Coverage reports

- **Deploy Pipeline** (new)
  - Deploy to staging on PR merge
  - Deploy to production on release

### 4. Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

### 5. Coverage Reporting

- Minimum 80% coverage required
- Upload to Codecov
- Fail CI if coverage drops

## File Structure

```
tests/
├── unit/
│   ├── conftest.py
│   ├── factories.py           # factory_boy factories
│   └── test_*.py
├── integration/
│   ├── conftest.py
│   └── test_*.py
├── e2e_playwright/
│   ├── conftest.py            # Already exists
│   ├── test_*.py
│   └── fixtures/
│       └── test_data.json
└── pytest.ini                 # Pytest configuration
```

## Technical Requirements

### Pytest Configuration
```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = core.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
```

### Factory Definitions
```python
# tests/unit/factories.py
import factory
from factory.django import DjangoModelFactory
from accounts.models import User, Organization, APIKey

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Faker('company')
    slug = factory.Sequence(lambda n: f'org-{n}')
    owner = factory.SubFactory(UserFactory)
    subscription_tier = 'FREE'

class APIKeyFactory(DjangoModelFactory):
    class Meta:
        model = APIKey

    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Sequence(lambda n: f'API Key {n}')
    # key is auto-generated in model
```

### Example Unit Test
```python
# tests/unit/test_accounts_models.py
import pytest
from tests.unit.factories import UserFactory, OrganizationFactory

@pytest.mark.django_db
class TestUserModel:
    def test_user_creation(self):
        """Test user can be created with factory."""
        user = UserFactory(email='test@example.com')
        assert user.email == 'test@example.com'
        assert user.email_verified is False

    def test_user_str_representation(self):
        """Test user __str__ method."""
        user = UserFactory(email='test@example.com')
        assert str(user) == 'test@example.com'

@pytest.mark.django_db
class TestOrganizationModel:
    def test_organization_creation(self):
        """Test organization can be created."""
        org = OrganizationFactory(name='Test Corp')
        assert org.name == 'Test Corp'
        assert org.subscription_tier == 'FREE'

    def test_organization_quota_limit(self):
        """Test default quota limit."""
        org = OrganizationFactory()
        assert org.quota_limit == 10000  # FREE tier default
```

### Example Integration Test
```python
# tests/integration/test_auth_flow.py
import pytest
from django.test import Client
from tests.unit.factories import UserFactory

@pytest.mark.django_db
class TestAuthenticationFlow:
    def test_signup_flow(self):
        """Test complete signup flow."""
        client = Client()

        # Submit signup form
        response = client.post('/accounts/signup/', {
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })

        # Should redirect to email verification page
        assert response.status_code == 302

        # User should be created but not verified
        from accounts.models import User
        user = User.objects.get(email='newuser@example.com')
        assert user.email_verified is False

    def test_login_flow(self):
        """Test login with valid credentials."""
        client = Client()
        user = UserFactory(email='test@example.com')
        user.set_password('password123')
        user.save()

        response = client.post('/accounts/login/', {
            'username': 'test@example.com',
            'password': 'password123',
        })

        # Should redirect to dashboard
        assert response.status_code == 302
        assert response.url == '/dashboard'
```

### Playwright E2E Tests

**Auth Flows** (TICKET-02 validation):
```python
# tests/e2e_playwright/test_auth_flows.py
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_signup_flow_success(page: Page):
    """Test successful user signup."""
    page.goto('http://localhost:8000/signup')

    # Fill signup form
    page.fill('input[name="email"]', 'newuser@example.com')
    page.fill('input[name="password1"]', 'SecurePass123!')
    page.fill('input[name="password2"]', 'SecurePass123!')
    page.click('button[type="submit"]')

    # Verify success message
    expect(page.locator('.success-message')).to_be_visible()

    # Take screenshot
    page.screenshot(path='artifacts/signup-success.png')

@pytest.mark.e2e
def test_signup_validation_errors(page: Page):
    """Test signup form validation."""
    page.goto('http://localhost:8000/signup')

    # Submit empty form
    page.click('button[type="submit"]')

    # Verify error messages
    expect(page.locator('.error-message')).to_be_visible()

    # Screenshot error state
    page.screenshot(path='artifacts/signup-errors.png')
```

**Billing Flows** (TICKET-03 validation):
```python
# tests/e2e_playwright/test_billing_flows.py
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_pricing_page_displays_all_tiers(page: Page):
    """Test pricing page shows all 4 subscription tiers."""
    page.goto('http://localhost:8000/pricing')

    # Verify all plan cards visible
    plans = page.locator('.plan-card')
    expect(plans).to_have_count(4)

    # Verify FREE plan
    free_plan = page.locator('[data-plan="free"]')
    expect(free_plan).to_contain_text('$0')
    expect(free_plan).to_contain_text('10,000 characters')

    # Screenshot
    page.screenshot(path='artifacts/pricing-page.png')

@pytest.mark.e2e
def test_stripe_checkout_redirect(page: Page, authenticated_page):
    """Test Stripe Checkout redirect (requires logged-in user)."""
    page = authenticated_page
    page.goto('http://localhost:8000/billing/subscribe')

    # Click STARTER plan
    page.click('[data-plan="starter"]')

    # Wait for Stripe redirect
    page.wait_for_url('**/checkout.stripe.com/**', timeout=10000)

    # Verify on Stripe page
    expect(page).to_have_url(re.compile(r'checkout\.stripe\.com'))
```

**Full User Journey**:
```python
# tests/e2e_playwright/test_full_user_journey.py
import pytest
from playwright.sync_api import Page

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_user_journey(page: Page):
    """Test complete flow: Signup → Subscribe → Summarize."""

    # 1. Signup
    page.goto('http://localhost:8000/signup')
    page.fill('input[name="email"]', 'journey@example.com')
    page.fill('input[name="password1"]', 'SecurePass123!')
    page.fill('input[name="password2"]', 'SecurePass123!')
    page.click('button[type="submit"]')

    # 2. Verify email (mock this in test)
    # ...

    # 3. Login
    page.goto('http://localhost:8000/login')
    page.fill('input[name="username"]', 'journey@example.com')
    page.fill('input[name="password"]', 'SecurePass123!')
    page.click('button[type="submit"]')

    # 4. Navigate to playground
    page.goto('http://localhost:8000/playground')

    # 5. Summarize text
    sample_text = "This is a sample text for summarization..." * 50
    page.fill('textarea[name="text"]', sample_text)
    page.select_option('select[name="mode"]', 'extractive')
    page.click('button:has-text("Summarize")')

    # 6. Verify summary displayed
    page.wait_for_selector('.summary-result', timeout=15000)
    expect(page.locator('.summary-result')).not_to_be_empty()

    # 7. Check usage updated
    expect(page.locator('.usage-counter')).to_contain_text('characters used')

    # Full journey complete
    page.screenshot(path='artifacts/full-journey-complete.png')
```

## CI/CD Pipeline Enhancement

Update `.github/workflows/ci.yml` to include:

```yaml
# Add after existing jobs

  # Deploy to Staging
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [test-backend, test-playwright]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - name: Deploy to Render Staging
        run: |
          # Trigger Render deploy hook
          curl -X POST ${{ secrets.RENDER_STAGING_DEPLOY_HOOK }}

  # Deploy to Production
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [test-backend, test-playwright]
    if: github.event_name == 'release' && github.event.action == 'published'

    steps:
      - name: Deploy to Render Production
        run: |
          curl -X POST ${{ secrets.RENDER_PRODUCTION_DEPLOY_HOOK }}
```

## Testing Requirements

### Coverage Targets
- Overall: >80%
- Models: >90%
- Views: >75%
- Serializers: >85%

### Test Categories
- Unit tests: ~150+ tests
- Integration tests: ~40+ tests
- E2E tests: ~30+ tests

## Visual QA Handoff

After completion, Visual QA Agent validates:

1. **CI Pipeline Includes Playwright**
   - Playwright tests run in CI
   - Screenshots uploaded as artifacts
   - Visual regression baseline stored

2. **All Tests Passing**
   - Green CI badge on main branch
   - No flaky tests
   - Consistent results

## Acceptance Criteria

- [ ] Pytest suite with >80% coverage
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Playwright E2E suite complete
- [ ] GitHub Actions CI green
- [ ] Pre-commit hooks configured
- [ ] Coverage report uploaded to Codecov
- [ ] No security vulnerabilities (Bandit, Safety)
- [ ] Visual QA approved

## Dependencies
```txt
pytest==7.4.4
pytest-django==4.7.0
pytest-cov==4.1.0
pytest-xdist==3.5.0
factory-boy==3.3.0
faker==22.0.0
playwright==1.41.1
```

## Handoff To
- Release Engineer (for deployment)
- Visual QA Agent (for CI validation)

## Communication Protocol

### On Completion
```
[QA_CI_ENGINEER] → [ORCHESTRATOR_AGENT]
ACTION: COMPLETE
TICKET: TICKET-08
STATUS: COMPLETE
ARTIFACTS:
  - tests/unit/ (25+ files)
  - tests/integration/ (8+ files)
  - tests/e2e_playwright/ (6+ files)
  - .pre-commit-config.yaml
  - pytest.ini
TESTS:
  - Unit: 156 passed
  - Integration: 42 passed
  - E2E: 34 passed
  - Coverage: 84%
VISUAL_QA_REQUIRED: YES
NOTES:
  - All tests green in CI
  - Playwright tests integrated
  - Coverage meets target
READY_FOR_NEXT: [TICKET-09]
```

## Important Notes
- Run tests in parallel with pytest-xdist (`pytest -n auto`)
- Use fixtures extensively to reduce duplication
- Mock external services (Stripe, email) in tests
- Keep E2E tests fast (<5 minutes total)
- Store test data in fixtures, not hardcoded
