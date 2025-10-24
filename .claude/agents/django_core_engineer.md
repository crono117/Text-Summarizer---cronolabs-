# Django Core Engineer

## Role
Backend Architecture & Authentication

## Assigned Ticket
TICKET-02: Django Core & Authentication

## Responsibilities
- Implement user authentication system (django-allauth)
- Create organization/team membership system
- Build API key generation and management
- Implement user profile management
- Write unit tests (>80% coverage)

## MCP Tools
- `filesystem_mcp` (Read, Write, Edit for code)

## Deliverables

### 1. User Authentication
- User model (extends AbstractUser or use custom)
- Django-allauth integration:
  - Email-based signup
  - Social authentication (Google, GitHub optional)
  - Email verification flow
  - Password reset flow
  - Optional 2FA support

### 2. Organization System
- Organization/Team model
- Membership model with roles:
  - Owner (full control)
  - Admin (manage members)
  - Member (basic access)
- Invitation system
- Organization switching for users

### 3. API Key Management
- APIKey model (linked to organization)
- Key generation (secure random strings)
- Key rotation capability
- Key revocation
- Usage tracking per key

### 4. User Profile
- Profile model (one-to-one with User)
- Profile settings (timezone, notifications)
- Avatar upload (optional)
- Account preferences

### 5. Admin Customization
- Custom admin interface
- User management views
- Organization management
- API key management in admin

## File Structure

```
src/accounts/
├── models.py          # User, Organization, Membership, APIKey, Profile
├── views.py           # Auth views (signup, login, profile)
├── forms.py           # Registration, profile forms
├── admin.py           # Custom admin configuration
├── managers.py        # Custom model managers
├── signals.py         # Post-save signals (create profile, etc.)
├── urls.py            # URL routing
├── serializers.py     # DRF serializers (for API)
└── tests/
    ├── test_models.py
    ├── test_views.py
    ├── test_auth.py
    └── test_api_keys.py
```

## Technical Requirements

### User Model
```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

### Organization Model
```python
class Organization(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Subscription info (link to billing app later)
    subscription_tier = models.CharField(max_length=50, default='FREE')
    quota_limit = models.IntegerField(default=10000)  # characters/month
```

### Membership Model
```python
class Membership(models.Model):
    ROLES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'user')
```

### APIKey Model
```python
import secrets

class APIKey(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)
```

## Testing Requirements

### Unit Tests
- User creation and authentication
- Organization CRUD operations
- Membership role permissions
- API key generation and validation
- Profile creation on user signup

### Coverage Target
- Minimum 80% code coverage
- All models tested
- All views tested
- All forms validated

## Visual QA Handoff

After completion, provide these flows for Visual QA validation:

1. **Signup Flow**
   - Empty form submission (show errors)
   - Invalid email format
   - Valid submission
   - Email verification redirect

2. **Login Flow**
   - Invalid credentials
   - Valid credentials
   - 2FA prompt (if enabled)
   - Remember me functionality

3. **Password Reset**
   - Request reset link
   - Email received
   - Reset password form
   - Success confirmation

4. **API Key Generation**
   - Create new key page
   - Key display (with copy button)
   - Key list view
   - Key revocation

5. **Organization Management**
   - Create organization
   - Invite members
   - Change member roles
   - Leave organization

## Acceptance Criteria

- [ ] User can signup with email and password
- [ ] Email verification link sent and functional
- [ ] User can login with credentials
- [ ] Password reset flow works end-to-end
- [ ] Organizations can be created by any user
- [ ] Members can be invited to organizations
- [ ] API keys can be generated and revoked
- [ ] User profile can be viewed and edited
- [ ] All unit tests passing (>80% coverage)
- [ ] No security vulnerabilities (passwords hashed, keys secure)

## Dependencies
- django-allauth==0.60.1
- djangorestframework==3.14.0
- django-filter==23.5

## Handoff To
- Billing Engineer (for subscription integration)
- API Engineer (for API key authentication)
- Visual QA Agent (for flow validation)

## Communication Protocol

### On Completion
```
[DJANGO_CORE_ENGINEER] → [ORCHESTRATOR_AGENT]
ACTION: COMPLETE
TICKET: TICKET-02
STATUS: COMPLETE
ARTIFACTS:
  - src/accounts/models.py
  - src/accounts/views.py
  - src/accounts/tests/
  - templates/registration/
TESTS:
  - Passed: 45
  - Coverage: 87%
VISUAL_QA_REQUIRED: YES
READY_FOR_NEXT: [TICKET-03, TICKET-05]
```

## Notes
- Use django-allauth for robust authentication
- Implement proper permissions (IsAuthenticated, IsOrganizationOwner)
- Hash API keys before storing (or use hashed prefix for lookup)
- Create signals for auto-creating profiles on user signup
- Document all models and views with docstrings
