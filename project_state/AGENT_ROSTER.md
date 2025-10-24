# 🎭 SUMMASAAS AGENT ROSTER

**Project**: Text Summarizer SaaS Platform
**Architecture**: Multi-Agent Development with Visual Validation Pipeline
**Initialized**: 2025-10-16

---

## 🎯 ACTIVE AGENTS

### 1️⃣ ORCHESTRATOR AGENT
**Status**: 🟢 ACTIVE
**Role**: Senior Technical Lead & Project Manager
**MCP Tools**: `github_mcp`, `filesystem_mcp`
**Responsibilities**:
- Manage agent task queue and dependencies
- Coordinate handoffs between agents
- Enforce quality gates before progression
- Maintain project timeline and blockers
- Synthesize agent outputs into coherent product

**Current Task**: Initializing project structure (TICKET-01)

---

### 2️⃣ VISUAL QA AGENT
**Status**: ⏸️ STANDBY
**Role**: Visual Validation & User Experience Guardian
**MCP Tools**: `playwright_mcp`, `filesystem_mcp`
**Trigger Points**:
- After TICKET-02 (Auth flows)
- After TICKET-03 (Billing pages)
- After TICKET-05 (API playground)
- After TICKET-06 (Email templates)
- After TICKET-07 (Full UI audit - CRITICAL)
- After TICKET-09 (Production smoke tests)

**Validation Matrix**:
- Browsers: Chromium, Firefox, WebKit
- Viewports: 375px (mobile), 768px (tablet), 1920px (desktop)
- Accessibility: WCAG 2.1 AA compliance
- Performance: Lighthouse score >90

---

### 3️⃣ DJANGO CORE ENGINEER
**Status**: ⏸️ STANDBY
**Role**: Backend Architecture & Authentication
**MCP Tools**: `filesystem_mcp`
**Assigned Tickets**: TICKET-02
**Deliverables**:
- Django project scaffold
- Allauth integration (signup, login, 2FA)
- Organization membership system
- API key generation
- User profile management

**Handoff To**: Billing Engineer, API Engineer
**Visual QA Required**: ✅ Auth flows validation

---

### 4️⃣ BILLING & ENTITLEMENTS ENGINEER
**Status**: ⏸️ STANDBY
**Role**: Stripe Integration & Subscription Logic
**MCP Tools**: `filesystem_mcp`
**Assigned Tickets**: TICKET-03
**Deliverables**:
- djaodjin-saas installation
- Stripe product/price setup (4 plans: FREE, STARTER, PRO, ENTERPRISE)
- Subscription lifecycle management
- Webhook receiver (payment success, cancellation)
- Customer portal integration
- Entitlement enforcement (quota checks)

**Handoff To**: API Engineer, Web UI Engineer
**Visual QA Required**: ✅ Billing pages & Stripe checkout flow

---

### 5️⃣ SUMMARIZATION ENGINEER
**Status**: ⏸️ STANDBY
**Role**: NLP Engine Integration
**MCP Tools**: `filesystem_mcp`
**Assigned Tickets**: TICKET-04
**Deliverables**:
- Integrate existing NLP models from base repo
- Implement 4 summarization modes:
  - Extractive (TextRank)
  - Abstractive (T5/BART)
  - Hybrid
  - Keyword extraction
- Character counting and input validation
- Model optimization (quantization, caching)

**Handoff To**: API Engineer
**Visual QA Required**: ❌ (Backend only until API integration)

---

### 6️⃣ API & QUOTAS ENGINEER
**Status**: ⏸️ STANDBY
**Role**: REST API & Rate Limiting
**MCP Tools**: `filesystem_mcp`
**Assigned Tickets**: TICKET-05
**Deliverables**:
- DRF API endpoints:
  - `POST /api/v1/summarize`
  - `GET /api/v1/usage`
  - `GET /api/v1/history`
- API key authentication
- Rate limiting per plan tier
- Quota enforcement (402/429 responses)
- Usage tracking

**Handoff To**: Web UI Engineer, Visual QA Agent
**Visual QA Required**: ✅ API playground & error states

---

### 7️⃣ BACKGROUND JOBS & INFRA ENGINEER
**Status**: ⏸️ STANDBY
**Role**: Celery, Redis, S3, Email
**MCP Tools**: `filesystem_mcp`
**Assigned Tickets**: TICKET-06
**Deliverables**:
- Celery worker configuration
- Redis setup (cache + message broker)
- S3 integration for document storage
- Email service (Postmark/SendGrid):
  - Welcome emails
  - Invoice emails
  - Quota alerts (80%, 100%)
  - Password reset
- Scheduled tasks (monthly quota reset)

**Handoff To**: Web UI Engineer, Visual QA Agent
**Visual QA Required**: ✅ Email template rendering

---

### 8️⃣ WEB UI ENGINEER
**Status**: ⏸️ STANDBY
**Role**: Frontend Templates & Styling
**MCP Tools**: `filesystem_mcp`, `playwright_mcp`
**Assigned Tickets**: TICKET-07
**Deliverables**:
- Django templates with HTMX
- Tailwind CSS configuration
- Responsive design system
- Pages:
  - Marketing homepage
  - Pricing page
  - Dashboard (usage charts)
  - API playground
  - Billing portal
  - 404/500 error pages
- Interactive components (forms, modals, toasts)

**Handoff To**: Visual QA Agent (MANDATORY)
**Visual QA Required**: ✅ Full UI audit across all viewports

**Special Requirements**:
- Must use Playwright to preview components before committing
- Must capture screenshots at mobile/tablet/desktop
- Must test keyboard navigation

---

### 9️⃣ QA & CI ENGINEER
**Status**: ⏸️ STANDBY
**Role**: Automated Testing & CI/CD
**MCP Tools**: `github_mcp`, `filesystem_mcp`
**Assigned Tickets**: TICKET-08
**Deliverables**:
- Pytest suite (unit + integration tests)
- Playwright test suite (E2E)
- GitHub Actions workflows:
  - Test on PR
  - Visual regression tests
  - Coverage reporting
- Pre-commit hooks (black, isort, flake8)
- Test fixtures and factories

**Handoff To**: Release Engineer
**Visual QA Required**: ✅ CI includes Playwright tests

---

### 🔟 RELEASE ENGINEER
**Status**: ⏸️ STANDBY
**Role**: Deployment & Launch
**MCP Tools**: `github_mcp`, `filesystem_mcp`, `playwright_mcp`
**Assigned Tickets**: TICKET-09
**Deliverables**:
- Render/Railway deployment configuration
- Environment setup (staging + production)
- Database migrations
- Static files CDN
- Domain configuration
- SSL certificates
- Health check endpoints
- Error monitoring (Sentry)

**Handoff To**: Orchestrator (for final sign-off)
**Visual QA Required**: ✅ Production smoke tests

---

## 📊 AGENT COMMUNICATION PROTOCOL

### Message Format
```
[AGENT_NAME] → [TARGET_AGENT]
ACTION: {ASSIGN|COMPLETE|VALIDATE|BLOCK}
TICKET: TICKET-{N}
STATUS: {PENDING|IN_PROGRESS|COMPLETE|BLOCKED}
ARTIFACTS: [list of files/reports]
NOTES: {optional context}
```

### Visual QA Checkpoint Protocol
```
[ORCHESTRATOR] → [VISUAL_QA_AGENT]
VALIDATE: TICKET-{N} outputs
FOCUS: {specific flows/pages}
VIEWPORTS: [375, 768, 1920]
SERVER: http://localhost:8000

[VISUAL_QA_AGENT] → [ORCHESTRATOR]
TICKET-{N} VALIDATION: {PASSED|BLOCKED|WARNING}
FLOWS_TESTED: {X/Y successful}
SCREENSHOTS: /project_state/artifacts/ticket-{N}/
ACCESSIBILITY: {score}/100
BLOCKERS: {count}
RECOMMENDATION: {next action}
```

---

## 🎫 TICKET DEPENDENCY GRAPH

```
TICKET-01 (Infrastructure)
    ↓
TICKET-02 (Django Core) → TICKET-03 (Billing) → TICKET-05 (API) → TICKET-07 (Web UI) → TICKET-08 (Testing) → TICKET-09 (Deploy)
    ↓                           ↓                      ↑                  ↑
TICKET-04 (Summarization) ──────┘                      │                  │
                                                        │                  │
                    TICKET-06 (Background Jobs) ────────┴──────────────────┘
```

**Critical Path**: TICKET-01 → TICKET-02 → TICKET-03 → TICKET-05 → TICKET-07 → TICKET-08 → TICKET-09

---

## 🚦 QUALITY GATES

| Gate # | After Ticket | Agent | Validation Focus | Blocking Criteria |
|--------|-------------|-------|------------------|-------------------|
| 1 | TICKET-02 | Visual QA | Auth flows | Login/signup broken |
| 2 | TICKET-03 | Visual QA | Billing pages | Stripe checkout fails |
| 3 | TICKET-05 | Visual QA | API playground | Error states missing |
| 4 | TICKET-06 | Visual QA | Email templates | Emails unreadable |
| 5 | TICKET-07 | Visual QA | Full UI audit | Any critical flow broken |
| 6 | TICKET-08 | QA/CI | CI pipeline | Tests failing |
| 7 | TICKET-09 | Visual QA | Production smoke | Critical path broken |

---

## 📈 PROGRESS TRACKING

Track progress at: `/project_state/orchestrator_state.json`

**Current Status**: 🟡 TICKET-01 IN PROGRESS
**Next Milestone**: TICKET-02 (Django Core) - Ready to assign after TICKET-01 complete
