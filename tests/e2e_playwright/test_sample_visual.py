"""
Sample Playwright visual validation test.

This demonstrates the Visual QA Agent's testing capabilities.
VISUAL_QA_AGENT will generate similar tests for each ticket checkpoint.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_homepage_loads(page: Page):
    """
    Verify homepage loads successfully (basic smoke test).

    This test will be enhanced after TICKET-07 (Web UI) is complete.
    """
    # Navigate to homepage
    page.goto("http://localhost:8000/")

    # Verify page loads (will fail until Django is set up)
    # expect(page).to_have_title("SummaSaaS - AI Text Summarization")


@pytest.mark.visual
@pytest.mark.parametrize("viewport", ["mobile", "tablet", "desktop"])
def test_homepage_responsive(page: Page, viewport: str):
    """
    Test homepage renders correctly across viewports.

    Visual QA Agent will use this pattern for all responsive tests.
    """
    viewports = {
        "mobile": {"width": 375, "height": 667},
        "tablet": {"width": 768, "height": 1024},
        "desktop": {"width": 1920, "height": 1080},
    }

    # Set viewport
    page.set_viewport_size(viewports[viewport])

    # Navigate and screenshot
    page.goto("http://localhost:8000/")
    page.screenshot(path=f"project_state/artifacts/playwright/homepage-{viewport}.png")

    # Visual assertions (to be implemented)
    # expect(page.locator('.hero-section')).to_be_visible()


@pytest.mark.accessibility
def test_homepage_accessibility(page: Page):
    """
    Run accessibility audit on homepage.

    Visual QA Agent will run WCAG 2.1 AA compliance checks.
    """
    page.goto("http://localhost:8000/")

    # TODO: Integrate axe-core or similar accessibility testing library
    # accessibility_scan_results = page.accessibility.snapshot()
    # assert len(violations) == 0, f"Accessibility violations found: {violations}"


@pytest.mark.skip(reason="Auth not implemented yet - enable after TICKET-02")
def test_signup_flow(page: Page):
    """
    Test complete signup flow (to be implemented after TICKET-02).

    Visual QA Agent will validate:
    - Form rendering
    - Validation error states
    - Success messages
    - Email verification redirect
    """
    page.goto("http://localhost:8000/signup")

    # Fill form with invalid email
    page.fill('input[name="email"]', 'invalid-email')
    page.fill('input[name="password"]', 'short')
    page.click('button[type="submit"]')

    # Verify error messages appear
    expect(page.locator('.error-message')).to_be_visible()
    page.screenshot(path="project_state/artifacts/playwright/signup-error.png")

    # Fill form with valid data
    page.fill('input[name="email"]', 'test@example.com')
    page.fill('input[name="password"]', 'SecurePassword123!')
    page.click('button[type="submit"]')

    # Verify success state
    expect(page.locator('.success-message')).to_be_visible()
    page.screenshot(path="project_state/artifacts/playwright/signup-success.png")


@pytest.mark.skip(reason="Billing not implemented yet - enable after TICKET-03")
def test_billing_subscription_flow(page: Page):
    """
    Test billing page and Stripe checkout (to be implemented after TICKET-03).

    Visual QA Agent will validate:
    - All 4 plan tiers visible
    - Pricing displayed correctly
    - Stripe checkout redirect works
    """
    page.goto("http://localhost:8000/billing/subscribe")

    # Verify all plans visible
    plans = page.locator('.plan-card')
    expect(plans).to_have_count(4)

    # Click STARTER plan
    page.click('[data-plan="starter"]')

    # Wait for Stripe redirect
    page.wait_for_url('**/checkout.stripe.com/**', timeout=10000)
    page.screenshot(path="project_state/artifacts/playwright/stripe-checkout.png")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
