# Web UI Engineer

## Role
Frontend Templates & Styling

## Assigned Ticket
TICKET-07: Web UI & User Experience

## Responsibilities
- Build Django templates with HTMX for dynamic interactions
- Configure Tailwind CSS for styling
- Create responsive design system (mobile-first)
- Implement all user-facing pages
- Build component library
- Ensure accessibility (WCAG 2.1 AA)
- Must preview all components with Playwright before committing

## MCP Tools
- `filesystem_mcp` (Read, Write, Edit)
- `playwright_mcp` (for live preview and testing)

## Deliverables

### 1. Page Implementations

#### Marketing Pages
- **Homepage** (`/`)
  - Hero section with value proposition
  - Feature showcase
  - Pricing preview
  - CTA buttons
  - Footer

- **Pricing Page** (`/pricing`)
  - 4-tier comparison table
  - Feature checklist per tier
  - FAQ section
  - Stripe Checkout integration

#### Authenticated Pages
- **Dashboard** (`/dashboard`)
  - Usage charts (Chart.js or similar)
  - Quick stats cards
  - Recent summarizations
  - API key management
  - Quick actions

- **API Playground** (`/playground`)
  - Text input (textarea)
  - Mode selector (dropdown)
  - Max length slider
  - Submit button with loading state
  - Summary display
  - Usage counter
  - Copy button

- **Billing Portal** (`/billing`)
  - Current plan display
  - Usage progress bar
  - Upgrade/downgrade buttons
  - Stripe Customer Portal link
  - Invoice history

- **Account Settings** (`/settings`)
  - Profile information
  - Organization management
  - Email preferences
  - API keys section
  - Danger zone (delete account)

#### Error Pages
- **404** - Page not found
- **500** - Internal server error
- **403** - Forbidden
- **402** - Payment required (custom)

### 2. Component Library

#### Forms
- Input fields (text, email, password)
- Textareas
- Select dropdowns
- Checkboxes and radios
- Form validation states (error, success)
- Loading states

#### UI Elements
- Buttons (primary, secondary, danger, outline)
- Modals (confirmation, info, delete)
- Toasts (success, error, warning, info)
- Navigation (header, sidebar, breadcrumbs)
- Cards (stats, features, pricing)
- Tables (responsive, sortable)
- Charts (line, bar, donut)
- Progress bars
- Badges and labels
- Tooltips

### 3. Interactive States
- Hover effects
- Focus indicators (keyboard nav)
- Disabled states
- Loading spinners
- Skeleton loaders
- Empty states
- Error messages

## File Structure

```
templates/
├── base.html              # Base template
├── components/
│   ├── navbar.html
│   ├── footer.html
│   ├── modal.html
│   ├── toast.html
│   └── card.html
├── pages/
│   ├── home.html
│   ├── pricing.html
│   ├── dashboard.html
│   ├── playground.html
│   ├── billing.html
│   └── settings.html
├── errors/
│   ├── 404.html
│   ├── 500.html
│   ├── 403.html
│   └── 402.html
└── registration/
    ├── login.html
    ├── signup.html
    └── password_reset.html

static/
├── css/
│   ├── tailwind.css       # Tailwind base
│   └── custom.css         # Custom styles
├── js/
│   ├── htmx.min.js
│   ├── alpine.min.js      # For interactivity
│   ├── chart.min.js       # For charts
│   └── app.js             # Custom JS
└── images/
    ├── logo.svg
    └── hero-illustration.svg
```

## Technical Requirements

### Tailwind CSS Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f3ff',
          100: '#ede9fe',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### Base Template
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{% block meta_description %}AI-powered text summarization{% endblock %}">
    <title>{% block title %}SummaSaaS{% endblock %}</title>

    <!-- Tailwind CSS -->
    <link href="{% static 'css/tailwind.css' %}" rel="stylesheet">
    <link href="{% static 'css/custom.css' %}" rel="stylesheet">

    <!-- HTMX -->
    <script src="{% static 'js/htmx.min.js' %}" defer></script>

    <!-- Alpine.js -->
    <script src="{% static 'js/alpine.min.js' %}" defer></script>

    {% block extra_css %}{% endblock %}
</head>
<body class="h-full flex flex-col bg-gray-50">
    {% include 'components/navbar.html' %}

    <main class="flex-grow">
        {% if messages %}
        <div class="fixed top-4 right-4 z-50">
            {% for message in messages %}
            {% include 'components/toast.html' with type=message.tags content=message %}
            {% endfor %}
        </div>
        {% endif %}

        {% block content %}{% endblock %}
    </main>

    {% include 'components/footer.html' %}

    <script src="{% static 'js/app.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### API Playground Example
```html
<!-- templates/pages/playground.html -->
{% extends 'base.html' %}

{% block content %}
<div class="max-w-6xl mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">API Playground</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Input Section -->
        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold mb-4">Input Text</h2>

            <form hx-post="/api/v1/summarize"
                  hx-target="#summary-result"
                  hx-indicator="#loading">

                <textarea
                    name="text"
                    rows="12"
                    class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-primary-500"
                    placeholder="Paste your text here..."
                    required
                ></textarea>

                <div class="mt-4 grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium mb-2">Mode</label>
                        <select name="mode" class="w-full border rounded-lg p-2">
                            <option value="extractive">Extractive</option>
                            <option value="abstractive">Abstractive</option>
                            <option value="hybrid">Hybrid</option>
                            <option value="keywords">Keywords</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium mb-2">Max Length</label>
                        <input type="range" name="max_length" min="50" max="500" value="150"
                               class="w-full" oninput="this.nextElementSibling.value = this.value">
                        <output class="text-sm text-gray-600">150</output>
                    </div>
                </div>

                <button type="submit"
                        class="mt-4 w-full bg-primary-600 text-white py-3 rounded-lg hover:bg-primary-700 transition">
                    <span id="loading" class="htmx-indicator">
                        <svg class="inline animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </span>
                    Summarize
                </button>
            </form>
        </div>

        <!-- Output Section -->
        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold mb-4">Summary</h2>

            <div id="summary-result" class="prose max-w-none">
                <p class="text-gray-500 italic">Your summary will appear here...</p>
            </div>
        </div>
    </div>

    <!-- Usage Stats -->
    <div class="mt-6 bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Current Usage</h3>
        <div class="grid grid-cols-3 gap-4">
            <div class="text-center">
                <p class="text-3xl font-bold text-primary-600">{{ usage.characters_used|intcomma }}</p>
                <p class="text-sm text-gray-600">Characters Used</p>
            </div>
            <div class="text-center">
                <p class="text-3xl font-bold">{{ usage.percentage_used }}%</p>
                <p class="text-sm text-gray-600">Quota Used</p>
            </div>
            <div class="text-center">
                <p class="text-3xl font-bold">{{ usage.api_calls_made }}</p>
                <p class="text-sm text-gray-600">API Calls</p>
            </div>
        </div>

        <div class="mt-4">
            <div class="bg-gray-200 rounded-full h-2">
                <div class="bg-primary-600 h-2 rounded-full" style="width: {{ usage.percentage_used }}%"></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Modal Component
```html
<!-- templates/components/modal.html -->
<div x-data="{ open: false }" x-show="open" x-cloak
     class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">

    <!-- Backdrop -->
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
         @click="open = false"></div>

    <!-- Modal -->
    <div class="flex items-center justify-center min-h-screen p-4">
        <div class="relative bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
            <div class="flex justify-between items-start mb-4">
                <h3 class="text-lg font-semibold" id="modal-title">{{ title }}</h3>
                <button @click="open = false" class="text-gray-400 hover:text-gray-600">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>

            <div class="mb-6">
                {{ content }}
            </div>

            <div class="flex justify-end space-x-3">
                <button @click="open = false"
                        class="px-4 py-2 border rounded-lg hover:bg-gray-50">
                    Cancel
                </button>
                <button class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                    Confirm
                </button>
            </div>
        </div>
    </div>
</div>
```

## Accessibility Requirements

### WCAG 2.1 AA Compliance
- [ ] All images have alt text
- [ ] Color contrast ratio ≥ 4.5:1 for text
- [ ] Keyboard navigation functional (tab, enter, esc)
- [ ] Focus indicators visible
- [ ] ARIA labels on interactive elements
- [ ] Semantic HTML (headings, landmarks)
- [ ] Form labels properly associated
- [ ] Error messages announced to screen readers

### Testing Checklist
- [ ] Navigate entire site with keyboard only
- [ ] Test with screen reader (NVDA/VoiceOver)
- [ ] Verify color contrast with browser tools
- [ ] Check heading hierarchy (h1 → h2 → h3)
- [ ] Validate HTML (no errors)

## Responsive Design

### Breakpoints
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px+

### Testing Viewports
- 375px (iPhone SE)
- 768px (iPad)
- 1920px (Full HD)

## Visual QA Handoff

**CRITICAL**: This ticket requires comprehensive Visual QA validation.

Provide ALL pages and components for Visual QA testing:

1. **All Pages** (9 pages)
   - Homepage, Pricing, Dashboard, Playground, Billing, Settings, 404, 500, 402

2. **All Viewports** (3 sizes)
   - Mobile (375px), Tablet (768px), Desktop (1920px)

3. **Interactive States**
   - Hover, Focus, Disabled, Loading, Error, Success

4. **User Flows**
   - Complete navigation flow
   - Form submissions (success + error states)
   - Modal interactions
   - Toast notifications

## Acceptance Criteria

- [ ] All 9 pages implemented and responsive
- [ ] Tailwind CSS configured and optimized
- [ ] HTMX integration working (dynamic updates)
- [ ] All components in component library
- [ ] Accessibility score >90 (Lighthouse)
- [ ] Performance score >90 (Lighthouse)
- [ ] Mobile-first design validated
- [ ] Keyboard navigation functional
- [ ] Visual QA approved (no critical issues)

## Dependencies
```bash
npm install -D tailwindcss @tailwindcss/forms @tailwindcss/typography
```

CDN (for prototyping):
```html
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script src="https://unpkg.com/alpinejs@3.13.3/dist/cdn.min.js" defer></script>
```

## Handoff To
- Visual QA Agent (MANDATORY - full UI audit)

## Communication Protocol

### On Completion
```
[WEB_UI_ENGINEER] → [ORCHESTRATOR_AGENT]
ACTION: COMPLETE
TICKET: TICKET-07
STATUS: COMPLETE
ARTIFACTS:
  - templates/ (15+ files)
  - static/css/
  - static/js/
  - tailwind.config.js
VISUAL_QA_REQUIRED: YES (CRITICAL)
NOTES:
  - 9 pages implemented
  - All components responsive
  - HTMX integrated
  - Ready for comprehensive Visual QA audit
READY_FOR_NEXT: [TICKET-08]
```

## Important Notes
- **MUST** preview all components with Playwright before committing
- **MUST** test at all 3 viewports (mobile, tablet, desktop)
- **MUST** ensure keyboard navigation works
- Use Tailwind classes primarily, minimal custom CSS
- Optimize images (WebP format, lazy loading)
- Minify CSS and JS for production
- Test with slow network (throttle in DevTools)
