"""
Playwright test configuration for SummaSaaS visual validation.

This file configures the Playwright testing framework for end-to-end
and visual regression testing across multiple browsers and viewports.
"""

import os
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright


# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
VIEWPORT_MOBILE = {"width": 375, "height": 667}
VIEWPORT_TABLET = {"width": 768, "height": 1024}
VIEWPORT_DESKTOP = {"width": 1920, "height": 1080}

SCREENSHOT_DIR = "project_state/artifacts/playwright"


@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig):
    """Configure browser launch arguments."""
    return {
        "headless": True,
        "args": ["--disable-dev-shm-usage"],
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, pytestconfig):
    """Configure browser context with common settings."""
    return {
        **browser_context_args,
        "viewport": VIEWPORT_DESKTOP,
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "permissions": [],
    }


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def mobile_page(browser: Browser) -> Generator[Page, None, None]:
    """Create a mobile viewport page."""
    context = browser.new_context(
        viewport=VIEWPORT_MOBILE,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    )
    page = context.new_page()
    yield page
    page.close()
    context.close()


@pytest.fixture
def tablet_page(browser: Browser) -> Generator[Page, None, None]:
    """Create a tablet viewport page."""
    context = browser.new_context(viewport=VIEWPORT_TABLET)
    page = context.new_page()
    yield page
    page.close()
    context.close()


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    """Create an authenticated session (to be implemented after auth is ready)."""
    # TODO: Implement after TICKET-02 (authentication)
    # This will log in a test user and return the authenticated page
    return page


def pytest_configure(config):
    """Create screenshot directory if it doesn't exist."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)


# Markers for different test categories
def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: Smoke tests for critical paths")
    config.addinivalue_line("markers", "visual: Visual regression tests")
    config.addinivalue_line("markers", "accessibility: Accessibility audit tests")
    config.addinivalue_line("markers", "mobile: Mobile-specific tests")
    config.addinivalue_line("markers", "tablet: Tablet-specific tests")
    config.addinivalue_line("markers", "desktop: Desktop-specific tests")
