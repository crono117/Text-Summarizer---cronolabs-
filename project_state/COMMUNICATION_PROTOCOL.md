# 🔄 AGENT COMMUNICATION PROTOCOL

## Message Format Standard

All inter-agent communication follows this standardized format:

```
[SOURCE_AGENT] → [TARGET_AGENT]
ACTION: {ASSIGN|COMPLETE|VALIDATE|BLOCK|REQUEST|APPROVE}
TICKET: TICKET-{N}
STATUS: {PENDING|IN_PROGRESS|COMPLETE|BLOCKED|REQUIRES_REWORK}
TIMESTAMP: {ISO 8601 timestamp}
ARTIFACTS: [list of files, reports, or deliverables]
DEPENDENCIES: {prerequisite tickets or resources}
NOTES: {optional context, warnings, or recommendations}
```

---

## 📤 Message Types

### 1. ASSIGN (Orchestrator → Agent)
Initiates work on a new ticket.

**Template:**
```
[ORCHESTRATOR_AGENT] → [{TARGET_AGENT}]
ACTION: ASSIGN
TICKET: TICKET-{N}
PRIORITY: {HIGH|MEDIUM|LOW}
DEPENDENCIES: {list of completed tickets}
ESTIMATED_COMPLEXITY: {S|M|L|XL}

CONTEXT:
{Brief description of the task and expected outcomes}

DELIVERABLES:
- {Deliverable 1}
- {Deliverable 2}

VISUAL_QA_REQUIRED: {YES|NO}

READY_TO_BEGIN: YES
```

---

### 2. COMPLETE (Agent → Orchestrator)
Signals successful completion of assigned work.

**Template:**
```
[{AGENT_NAME}] → [ORCHESTRATOR_AGENT]
ACTION: COMPLETE
TICKET: TICKET-{N}
STATUS: COMPLETE
TIMESTAMP: {ISO timestamp}

ARTIFACTS:
- {file_path_1}
- {file_path_2}
- {report or documentation}

TESTS:
- Passed: {count}
- Failed: {count}
- Coverage: {percentage}

VISUAL_QA_REQUIRED: {YES|NO}
READY_FOR_NEXT: [TICKET-{N+1}, TICKET-{N+2}]

NOTES:
{Optional observations, warnings, or recommendations}
```

---

### 3. VALIDATE (Orchestrator → Visual QA)
Requests visual validation at quality gate checkpoints.

**Template:**
```
[ORCHESTRATOR_AGENT] → [VISUAL_QA_AGENT]
ACTION: VALIDATE
TICKET: TICKET-{N}
FOCUS: {specific flows, pages, or features to validate}
VIEWPORTS: [375, 768, 1920]
BROWSERS: [chromium, firefox, webkit]
SERVER: http://localhost:8000

VALIDATION_SCOPE:
- {Flow 1: e.g., "User signup with email verification"}
- {Flow 2: e.g., "Billing subscription page"}

ACCEPTANCE_CRITERIA:
- Accessibility score >85
- Page load <3s
- No critical UI breaks
- Keyboard navigation functional

BLOCKING_CRITERIA:
- Critical user flow broken
- Accessibility score <85
- Security issue visible
```

---

### 4. Visual QA Report (Visual QA → Orchestrator)
Reports validation results with PASS/BLOCK/WARN status.

**Template:**
```
[VISUAL_QA_AGENT] → [ORCHESTRATOR_AGENT]
ACTION: VALIDATE_RESULT
TICKET: TICKET-{N}
STATUS: {PASSED|BLOCKED|WARNING}
TIMESTAMP: {ISO timestamp}

FLOWS_TESTED: {X/Y successful}
BROWSERS_TESTED: [chromium ✅, firefox ✅, webkit ✅]
VIEWPORTS_TESTED: [mobile ✅, tablet ✅, desktop ✅]

RESULTS:
✅ PASSED: {count}
⚠️  WARNINGS: {count}
❌ BLOCKERS: {count}

ARTIFACTS:
- Screenshots: /project_state/artifacts/ticket-{N}/screenshots/
- Visual Diff Report: /project_state/artifacts/ticket-{N}/visual-diff-report.html
- Accessibility Report: /project_state/artifacts/ticket-{N}/accessibility-report.json

ACCESSIBILITY_SCORE: {score}/100
PERFORMANCE:
- Average Page Load: {time}ms
- Largest Contentful Paint: {time}ms
- Cumulative Layout Shift: {score}

BLOCKERS:
{List critical issues preventing approval, or "None"}

WARNINGS:
{List minor issues that should be addressed but don't block progress}

RECOMMENDATION: {APPROVE|REQUIRES_REWORK|MINOR_FIXES_OPTIONAL}

NEXT_ACTION:
{Suggested next steps based on validation results}
```

---

### 5. BLOCK (Agent → Orchestrator)
Reports an issue preventing progress.

**Template:**
```
[{AGENT_NAME}] → [ORCHESTRATOR_AGENT]
ACTION: BLOCK
TICKET: TICKET-{N}
STATUS: BLOCKED
TIMESTAMP: {ISO timestamp}

BLOCKER_TYPE: {DEPENDENCY|TECHNICAL|RESOURCE|CLARIFICATION_NEEDED}

DESCRIPTION:
{Clear description of what is blocking progress}

IMPACT:
{How this affects the current ticket and downstream work}

REQUESTED_ACTION:
{What is needed to unblock}

ESTIMATED_DELAY: {time estimate}
```

---

### 6. REQUEST (Agent → Orchestrator or Agent → Agent)
Requests information, resources, or assistance.

**Template:**
```
[{AGENT_NAME}] → [{TARGET_AGENT}]
ACTION: REQUEST
TICKET: TICKET-{N}
REQUEST_TYPE: {INFO|RESOURCE|REVIEW|INTEGRATION}

DESCRIPTION:
{What is being requested and why}

URGENCY: {HIGH|MEDIUM|LOW}

EXPECTED_RESPONSE:
{What kind of response or deliverable is needed}
```

---

### 7. APPROVE (Orchestrator → Agent)
Confirms approval and progression to next phase.

**Template:**
```
[ORCHESTRATOR_AGENT] → [{AGENT_NAME}]
ACTION: APPROVE
TICKET: TICKET-{N}
STATUS: APPROVED ✅
TIMESTAMP: {ISO timestamp}

VALIDATION_SUMMARY:
{Brief summary of what was validated and approved}

NEXT_TICKET: TICKET-{N+1}
ASSIGNED_TO: {Next agent in workflow}

HANDOFF_NOTES:
{Any important context for the next agent}
```

---

## 🎫 Ticket State File Format

Each ticket maintains a state file at: `project_state/tickets/ticket-{N}_state.json`

**Format:**
```json
{
  "ticket_id": "TICKET-02",
  "title": "Django Core & Authentication",
  "assigned_to": "DJANGO_CORE_ENGINEER",
  "status": "COMPLETE",
  "priority": "HIGH",
  "complexity": "L",
  "started_at": "2025-10-16T10:00:00Z",
  "completed_at": "2025-10-16T14:30:00Z",
  "duration_hours": 4.5,

  "dependencies": {
    "required": ["TICKET-01"],
    "blocks": ["TICKET-03", "TICKET-05"]
  },

  "artifacts": [
    "src/accounts/models.py",
    "src/accounts/views.py",
    "templates/registration/login.html",
    "templates/registration/signup.html"
  ],

  "tests": {
    "unit_tests": {
      "passed": 45,
      "failed": 0,
      "coverage": 87
    },
    "integration_tests": {
      "passed": 12,
      "failed": 0
    }
  },

  "visual_qa": {
    "required": true,
    "status": "PASSED",
    "validated_at": "2025-10-16T15:00:00Z",
    "report": "project_state/tickets/ticket-02_qa_report.json",
    "blockers": [],
    "warnings": ["Password strength indicator could be more visible"]
  },

  "communication_log": [
    {
      "timestamp": "2025-10-16T10:00:00Z",
      "from": "ORCHESTRATOR_AGENT",
      "to": "DJANGO_CORE_ENGINEER",
      "action": "ASSIGN",
      "message": "Starting work on authentication system"
    },
    {
      "timestamp": "2025-10-16T14:30:00Z",
      "from": "DJANGO_CORE_ENGINEER",
      "to": "ORCHESTRATOR_AGENT",
      "action": "COMPLETE",
      "message": "Auth system implemented with 87% test coverage"
    },
    {
      "timestamp": "2025-10-16T15:00:00Z",
      "from": "VISUAL_QA_AGENT",
      "to": "ORCHESTRATOR_AGENT",
      "action": "VALIDATE_RESULT",
      "message": "All auth flows validated successfully"
    }
  ],

  "notes": [
    "Implemented django-allauth for social auth support",
    "Added 2FA support (optional for users)",
    "API key generation integrated with organization model"
  ]
}
```

---

## 📊 Visual QA Report Format

Visual QA reports are stored at: `project_state/tickets/ticket-{N}_qa_report.json`

**Format:**
```json
{
  "ticket_id": "TICKET-02",
  "validated_at": "2025-10-16T15:00:00Z",
  "agent": "VISUAL_QA_AGENT",
  "status": "PASSED",

  "test_environment": {
    "server_url": "http://localhost:8000",
    "browsers": ["chromium", "firefox", "webkit"],
    "viewports": {
      "mobile": {"width": 375, "height": 667},
      "tablet": {"width": 768, "height": 1024},
      "desktop": {"width": 1920, "height": 1080}
    }
  },

  "flows_tested": [
    {
      "name": "User Signup - Valid Input",
      "status": "PASSED",
      "duration_ms": 450,
      "screenshots": [
        "artifacts/ticket-02/signup-form-mobile.png",
        "artifacts/ticket-02/signup-success-mobile.png"
      ],
      "issues": []
    },
    {
      "name": "User Signup - Invalid Email",
      "status": "PASSED",
      "duration_ms": 320,
      "screenshots": [
        "artifacts/ticket-02/signup-error-mobile.png"
      ],
      "issues": []
    },
    {
      "name": "Login Flow",
      "status": "PASSED",
      "duration_ms": 380,
      "screenshots": [
        "artifacts/ticket-02/login-form-desktop.png"
      ],
      "issues": []
    },
    {
      "name": "Password Reset",
      "status": "PASSED",
      "duration_ms": 520,
      "screenshots": [],
      "issues": []
    }
  ],

  "summary": {
    "total_flows": 8,
    "passed": 8,
    "failed": 0,
    "warnings": 1
  },

  "accessibility": {
    "score": 94,
    "violations": [],
    "warnings": [
      {
        "severity": "minor",
        "description": "Password strength indicator lacks sufficient color contrast",
        "recommendation": "Increase contrast ratio to 4.5:1 minimum"
      }
    ]
  },

  "performance": {
    "avg_page_load_ms": 1200,
    "largest_contentful_paint_ms": 1800,
    "first_input_delay_ms": 45,
    "cumulative_layout_shift": 0.02
  },

  "visual_regression": {
    "baseline_exists": false,
    "diffs_detected": 0,
    "acceptable_threshold": 0.1,
    "report_path": "artifacts/ticket-02/visual-diff-report.html"
  },

  "blockers": [],

  "warnings": [
    "Password strength indicator could be more visible (low priority)"
  ],

  "recommendations": [
    "Consider adding visual feedback during async form submission",
    "Enhance mobile keyboard handling for email input fields"
  ],

  "approval_status": "APPROVED",
  "approved_by": "VISUAL_QA_AGENT",
  "approved_at": "2025-10-16T15:00:00Z"
}
```

---

## 🔄 Workflow State Transitions

### Standard Ticket Lifecycle
```
PENDING → IN_PROGRESS → COMPLETE → VALIDATED → APPROVED
```

### With Rework Required
```
PENDING → IN_PROGRESS → COMPLETE → VALIDATED → BLOCKED → REQUIRES_REWORK
                                                                ↓
                                                          IN_PROGRESS (retry)
```

---

## 🚦 Quality Gate Checkpoints

| Gate # | After Ticket | Trigger | Agent | Pass Criteria |
|--------|-------------|---------|-------|---------------|
| 1 | TICKET-02 | Auth implementation complete | Visual QA | All auth flows functional |
| 2 | TICKET-03 | Billing pages implemented | Visual QA | Stripe checkout works |
| 3 | TICKET-05 | API endpoints deployed | Visual QA | Playground + error states |
| 4 | TICKET-06 | Email templates created | Visual QA | Emails render correctly |
| 5 | TICKET-07 | All UI pages complete | Visual QA | Full responsive audit passes |
| 6 | TICKET-08 | CI pipeline configured | QA/CI | All tests pass in CI |
| 7 | TICKET-09 | Production deployed | Visual QA | Smoke tests pass on live site |

---

## 📝 Communication Best Practices

1. **Be Explicit**: Always include ticket ID, status, and timestamp
2. **List Artifacts**: Provide file paths or URLs to deliverables
3. **Quantify Results**: Use metrics (test counts, coverage %, scores)
4. **Flag Blockers Early**: Don't wait until completion to report issues
5. **Document Decisions**: Note any architectural choices or trade-offs
6. **Preserve Context**: Include relevant notes for downstream agents

---

## 🔍 Logging

All agent communications are logged to:
- `project_state/agent_logs/{agent_name}.log`
- `project_state/orchestrator_state.json` (high-level status)
- `project_state/tickets/ticket-{N}_state.json` (ticket-specific)

---

## 📡 Example Communication Sequence

```
[ORCHESTRATOR_AGENT] → [DJANGO_CORE_ENGINEER]
ACTION: ASSIGN
TICKET: TICKET-02
...

[DJANGO_CORE_ENGINEER] → [ORCHESTRATOR_AGENT]
ACTION: COMPLETE
TICKET: TICKET-02
STATUS: COMPLETE
VISUAL_QA_REQUIRED: YES
...

[ORCHESTRATOR_AGENT] → [VISUAL_QA_AGENT]
ACTION: VALIDATE
TICKET: TICKET-02
FOCUS: Authentication flows
...

[VISUAL_QA_AGENT] → [ORCHESTRATOR_AGENT]
ACTION: VALIDATE_RESULT
TICKET: TICKET-02
STATUS: PASSED ✅
BLOCKERS: None
...

[ORCHESTRATOR_AGENT] → [DJANGO_CORE_ENGINEER]
ACTION: APPROVE
TICKET: TICKET-02
STATUS: APPROVED ✅
...

[ORCHESTRATOR_AGENT] → [BILLING_ENGINEER]
ACTION: ASSIGN
TICKET: TICKET-03
DEPENDENCIES: TICKET-02 (APPROVED)
...
```

---

This protocol ensures clear, traceable, and efficient communication across all agents throughout the project lifecycle.
