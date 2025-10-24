# Playwright Visual Validation Tests

This directory contains end-to-end tests using Playwright for visual validation and user journey testing.

## Purpose

The **Visual QA Agent** uses these tests to validate:
- User flows (signup, login, billing, API usage)
- Responsive design across viewports (mobile, tablet, desktop)
- Accessibility compliance (WCAG 2.1 AA)
- Visual regression (screenshot comparisons)
- Interactive element states (hover, focus, disabled)

## Test Structure

```
tests/e2e_playwright/
├── conftest.py                    # Pytest & Playwright configuration
├── test_sample_visual.py          # Sample tests (template)
├── test_auth_flows.py            # Authentication tests (TICKET-02)
├── test_billing_flows.py         # Billing & subscriptions (TICKET-03)
├── test_api_playground.py        # API playground tests (TICKET-05)
├── test_email_templates.py       # Email rendering tests (TICKET-06)
├── test_full_ui_audit.py         # Complete UI validation (TICKET-07)
└── test_production_smoke.py      # Production smoke tests (TICKET-09)
```

## Running Tests

### Locally
```bash
# Install Playwright browsers (first time only)
playwright install --with-deps

# Run all tests
pytest tests/e2e_playwright/

# Run specific test file
pytest tests/e2e_playwright/test_auth_flows.py -v

# Run with visual debugging (headed mode)
pytest tests/e2e_playwright/ --headed

# Run tests for specific viewport
pytest tests/e2e_playwright/ -m mobile

# Run smoke tests only
pytest tests/e2e_playwright/ -m smoke
```

### In CI (GitHub Actions)
Tests run automatically on:
- Every pull request
- Every push to main
- Before deployments

## Visual QA Agent Workflow

When a ticket reaches a Visual QA checkpoint:

1. **Agent Activation**
   ```
   [ORCHESTRATOR] → [VISUAL_QA_AGENT]
   VALIDATE: TICKET-{N} outputs
   FOCUS: {specific flows}
   SERVER: http://localhost:8000
   ```

2. **Test Execution**
   - Visual QA Agent runs Playwright tests
   - Captures screenshots at all viewports
   - Runs accessibility audits
   - Compares against baselines (if exists)

3. **Report Generation**
   ```
   project_state/tickets/ticket-{N}_qa_report.json
   project_state/artifacts/ticket-{N}/
     ├── screenshots/
     ├── visual-diff-report.html
     └── accessibility-report.json
   ```

4. **Blocking Criteria**
   - ❌ Critical user flow broken
   - ❌ Accessibility score <85
   - ❌ Page load time >5s
   - ❌ UI completely broken on any viewport

## Viewport Matrix

| Viewport | Width | Height | Device Representative |
|----------|-------|--------|----------------------|
| Mobile   | 375px | 667px  | iPhone SE            |
| Tablet   | 768px | 1024px | iPad                 |
| Desktop  | 1920px| 1080px | Full HD monitor      |

## Browser Matrix

- **Chromium** (Chrome/Edge)
- **Firefox**
- **WebKit** (Safari)

## Test Markers

- `@pytest.mark.smoke` - Critical path tests
- `@pytest.mark.visual` - Visual regression tests
- `@pytest.mark.accessibility` - WCAG compliance tests
- `@pytest.mark.mobile` - Mobile-specific tests
- `@pytest.mark.tablet` - Tablet-specific tests
- `@pytest.mark.desktop` - Desktop-specific tests

## Writing New Tests

Visual QA Agent follows this template:

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.visual
def test_feature_name(page: Page):
    """Test description and acceptance criteria."""

    # Navigate
    page.goto("http://localhost:8000/feature")

    # Interact
    page.fill('input[name="field"]', 'value')
    page.click('button[type="submit"]')

    # Assert
    expect(page.locator('.success')).to_be_visible()

    # Screenshot
    page.screenshot(path="artifacts/feature-success.png")
```

## Integration with Tickets

| Ticket | Visual QA Focus | Test File |
|--------|----------------|-----------|
| TICKET-02 | Auth flows | test_auth_flows.py |
| TICKET-03 | Billing pages | test_billing_flows.py |
| TICKET-05 | API playground | test_api_playground.py |
| TICKET-06 | Email templates | test_email_templates.py |
| TICKET-07 | Full UI audit | test_full_ui_audit.py |
| TICKET-09 | Production smoke | test_production_smoke.py |

## Troubleshooting

### Tests failing locally?
```bash
# Ensure Django dev server is running
docker-compose up web

# Check server is accessible
curl http://localhost:8000/health/
```

### Screenshots not generated?
```bash
# Verify directory exists
mkdir -p project_state/artifacts/playwright

# Check permissions
chmod -R 755 project_state/
```

### Browsers not installed?
```bash
# Reinstall Playwright browsers
playwright install --with-deps chromium firefox webkit
```

## Resources

- [Playwright Python Docs](https://playwright.dev/python/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [Visual Regression Best Practices](https://playwright.dev/docs/test-snapshots)
