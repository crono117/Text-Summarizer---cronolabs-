# IMPROVED Multi-Tenant Auth System Orchestration Prompt

## 📋 Context & Purpose

You are the **Orchestrator Agent** for SummaSaaS implementing a production-ready multi-tenant SaaS authentication and billing system. This prompt has been refined to avoid "spaghetto code" by providing:

1. **Explicit field-level contracts** (no naming ambiguity)
2. **Clear app boundaries** (User belongs in `accounts`, not `core`)
3. **Type specifications** (CharField vs ForeignKey, etc.)
4. **Method signatures** with return types
5. **Signal/middleware contracts**

## ⚠️ Critical Rules

1. **Follow the spec EXACTLY** - if spec says CharField, don't use ForeignKey
2. **Field names must match precisely** - `char_limit` not `character_limit`
3. **One model per responsibility** - don't mix concerns
4. **Return code to Orchestrator for review** before proceeding to next phase
5. **No shortcuts** - implement all methods, signals, and middleware as specified

---

## 🎯 Implementation Phases

### Phase 1: Models & Database (Django Core Engineer)
### Phase 2: Stripe Integration & Helpers (Billing Engineer)  
### Phase 3: DRF Permissions & Middleware (API Engineer)
### Phase 4: Dashboards (Web UI Engineer)
### Phase 5: Tests (QA/CI + Visual QA)
### Phase 6: Documentation (All)

---

## 📦 Django App Structure

```
src/
├── accounts/          # User, CustomerAccount, AccountMembership
│   ├── models.py
│   ├── admin.py
│   ├── signals.py     # Subscription → User.current_plan sync
│   └── migrations/
├── billing/           # Plan, Subscription
│   ├── models.py
│   ├── admin.py
│   └── migrations/
├── security/          # AccountSecurityState, UserSession
│   ├── models.py
│   ├── admin.py
│   ├── middleware.py  # Session enforcement
│   └── migrations/
├── api/
│   ├── permissions.py # DRF permission classes
│   ├── throttling.py  # Quota enforcement
│   └── urls.py
└── core/
    └── settings.py    # AUTH_USER_MODEL = 'accounts.User'
```

**IMPORTANT:** User model lives in `accounts` app, NOT `core` app.

---

## 🗂️ DATA MODEL CONTRACT (Exact Specification)

### 1. User (accounts/models.py)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user extending AbstractUser.
    
    IMPORTANT: User belongs in 'accounts' app, not 'core'.
    """
    
    # Staff flags
    is_staff_support = models.BooleanField(
        default=False,
        help_text="Support staff can manage customer accounts"
    )
    is_superadmin = models.BooleanField(
        default=False,
        help_text="Superadmins have full system access"
    )
    
    # Denormalized plan cache (CharField, NOT ForeignKey!)
    current_plan = models.CharField(
        max_length=20,
        choices=[
            ('FREE', 'Free'),
            ('PLUS', 'Plus'),
            ('PRO', 'Pro'),
            ('ENTERPRISE', 'Enterprise')
        ],
        default='FREE',
        help_text="Cached from active Subscription.plan.code for fast lookups"
    )
    
    # Usage counters (BigIntegerField as spec requires)
    monthly_char_used = models.BigIntegerField(
        default=0,
        help_text="Characters processed this billing period"
    )
    monthly_requests_used = models.BigIntegerField(
        default=0,
        help_text="API requests this billing period"
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email or self.username
    
    # REQUIRED METHODS (spec says these must exist)
    def is_paying_customer(self) -> bool:
        """Return True if user is on a paid plan (not FREE)"""
        return self.current_plan != 'FREE'
    
    def is_internal(self) -> bool:
        """Return True if user is staff support or superadmin"""
        return self.is_staff_support or self.is_superadmin
```

**Settings update required:**
```python
# core/settings.py
AUTH_USER_MODEL = 'accounts.User'
```

**Admin registration:**
```python
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'email', 
        'username', 
        'current_plan', 
        'is_staff_support', 
        'is_superadmin', 
        'last_login'
    ]
    # ... extend BaseUserAdmin fieldsets
```

---

### 2. Plan (billing/models.py)

```python
from django.db import models

class Plan(models.Model):
    """
    Billing plan tiers.
    
    CRITICAL: Must have separate 'code' and 'display_name' fields.
    """
    
    # Identification (spec requires BOTH fields)
    code = models.CharField(
        max_length=20,
        unique=True,
        choices=[
            ('FREE', 'FREE'),
            ('PLUS', 'PLUS'),
            ('PRO', 'PRO'),
            ('ENTERPRISE', 'ENTERPRISE')
        ],
        help_text="Internal plan code (FREE, PLUS, PRO, ENTERPRISE)"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Marketing label (e.g., 'Professional Plan')"
    )
    
    # Pricing
    monthly_price_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in USD per month"
    )
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Stripe Price ID (e.g., price_xxxxx)"
    )
    
    # Quota limits (EXACT field names from spec!)
    char_limit = models.BigIntegerField(
        help_text="Monthly character limit"
    )
    req_per_hour = models.IntegerField(
        help_text="API requests allowed per hour"
    )
    
    # Team features
    max_seats = models.IntegerField(
        help_text="Maximum team members (1 for FREE/PLUS, 5+ for PRO/ENTERPRISE)"
    )
    max_concurrent_sessions = models.IntegerField(
        default=2,
        help_text="Max concurrent sessions per user"
    )
    allow_team_members = models.BooleanField(
        default=False,
        help_text="Whether plan allows inviting team members"
    )
    
    # Support SLA
    priority_support = models.BooleanField(
        default=False,
        help_text="Dedicated support channel"
    )
    sla = models.BooleanField(
        default=False,
        help_text="SLA guarantee (99.9% uptime, etc.)"
    )
    
    class Meta:
        ordering = ['monthly_price_usd']
    
    def __str__(self):
        return f"{self.code} - ${self.monthly_price_usd}/mo"
```

**Admin registration:**
```python
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = [
        'code', 
        'monthly_price_usd', 
        'max_seats', 
        'allow_team_members', 
        'sla'
    ]
```

**Seed data (management command or fixture):**
```python
FREE: max_seats=1, allow_team_members=False, max_concurrent_sessions=2, 
      char_limit=10_000, req_per_hour=10, monthly_price_usd=0

PLUS: max_seats=1, allow_team_members=False, max_concurrent_sessions=2,
      char_limit=100_000, req_per_hour=100, monthly_price_usd=9.99

PRO: max_seats=5, allow_team_members=True, max_concurrent_sessions=8,
     char_limit=1_000_000, req_per_hour=1000, monthly_price_usd=29.99

ENTERPRISE: max_seats=20, allow_team_members=True, max_concurrent_sessions=40,
            char_limit=10_000_000, req_per_hour=None, sla=True, 
            priority_support=True, monthly_price_usd=99.99
```

---

### 3. CustomerAccount (accounts/models.py)

```python
class CustomerAccount(models.Model):
    """
    Workspace/organization for paying customers.
    
    Even solo users get a CustomerAccount.
    """
    
    name = models.CharField(
        max_length=200,
        help_text="Account/organization name"
    )
    
    # REQUIRED: Direct owner FK (spec explicitly requires this)
    owner = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name='owned_accounts',
        help_text="Primary account owner"
    )
    
    # Stripe linkage
    stripe_customer_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Stripe Customer ID (cus_xxxxx)"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="False = suspended/locked"
    )
    
    def __str__(self):
        return self.name
```

**Admin registration:**
```python
@admin.register(CustomerAccount)
class CustomerAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'stripe_customer_id', 'is_active']
    search_fields = ['name', 'owner__email', 'stripe_customer_id']
```

---

### 4. Subscription (billing/models.py)

```python
class Subscription(models.Model):
    """
    Links CustomerAccount to a Plan.
    
    CRITICAL: Must be OneToOneField, not ForeignKey!
    Each account has exactly ONE active subscription at a time.
    """
    
    # OneToOne relationship (only 1 active subscription per account)
    account = models.OneToOneField(
        'accounts.CustomerAccount',
        on_delete=models.CASCADE,
        related_name='subscription'  # Note: singular, not plural!
    )
    
    plan = models.ForeignKey(
        'Plan',
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    
    # Stripe integration
    stripe_subscription_id = models.CharField(
        max_length=100,
        blank=True,
        default=''
    )
    
    # Billing period
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    
    # Trial state (BooleanField as spec requires, NOT status CharField!)
    is_trial = models.BooleanField(
        default=False,
        help_text="True if in trial period"
    )
    
    # Cancellation state (BooleanField as spec requires)
    is_canceled = models.BooleanField(
        default=False,
        help_text="True if subscription is canceled"
    )
    
    def __str__(self):
        return f"{self.account.name} - {self.plan.code}"
    
    def is_active(self) -> bool:
        """
        Subscription is active if:
        - Not canceled
        - Period hasn't expired
        - Account is active
        """
        from django.utils import timezone
        return (
            not self.is_canceled and
            self.current_period_end >= timezone.now() and
            self.account.is_active
        )
```

**REQUIRED SIGNAL (accounts/signals.py):**
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from billing.models import Subscription

@receiver(post_save, sender=Subscription)
def sync_user_current_plan(sender, instance, **kwargs):
    """
    When Subscription.plan changes, update owner's current_plan.
    
    This keeps User.current_plan in sync for fast template/throttle lookups.
    """
    owner = instance.account.owner
    owner.current_plan = instance.plan.code
    owner.save(update_fields=['current_plan'])
```

---

### 5. AccountMembership (accounts/models.py)

```python
class AccountMembership(models.Model):
    """
    Links users to accounts with roles (RBAC).
    
    Permissions:
    - OWNER: Full control (billing, members, API usage)
    - ADMIN: Manage members, no billing access
    - MEMBER: Use API only
    - READONLY: View dashboards only
    """
    
    ROLE_CHOICES = [
        ('OWNER', 'Owner'),
        ('ADMIN', 'Administrator'),
        ('MEMBER', 'Member'),
        ('READONLY', 'Read-Only')
    ]
    
    account = models.ForeignKey(
        'CustomerAccount',
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='account_memberships'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='MEMBER'
    )
    
    class Meta:
        unique_together = [('account', 'user')]
    
    def __str__(self):
        return f"{self.user.email} → {self.account.name} ({self.role})"
    
    def clean(self):
        """
        Enforce seat limits from Plan.max_seats.
        
        Raise ValidationError if adding this member would exceed limit.
        """
        super().clean()
        
        plan = self.account.subscription.plan
        active_members = AccountMembership.objects.filter(
            account=self.account
        ).exclude(pk=self.pk).count()
        
        if active_members >= plan.max_seats:
            raise ValidationError(
                f"Account has reached max seats ({plan.max_seats}). "
                f"Upgrade to add more members."
            )
```

**Admin registration:**
```python
@admin.register(AccountMembership)
class AccountMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'account', 'role']
    search_fields = ['user__email', 'account__name']
    list_filter = ['role']
```

---

### 6. AccountSecurityState (security/models.py)

```python
class AccountSecurityState(models.Model):
    """
    Fraud/abuse tracking per account.
    
    Support staff can manually lock/unlock accounts.
    """
    
    account = models.OneToOneField(
        'accounts.CustomerAccount',
        on_delete=models.CASCADE,
        related_name='security_state'
    )
    
    # REQUIRED: Per-account session cap override
    concurrent_session_cap = models.IntegerField(
        default=2,
        help_text="Account-specific session limit (overrides Plan default)"
    )
    
    # Lock state
    is_temp_locked = models.BooleanField(
        default=False,
        help_text="If True, block all API requests for this account"
    )
    last_flag_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Why account was flagged/locked"
    )
    warning_count = models.IntegerField(
        default=0,
        help_text="Number of times account has been flagged"
    )
    
    def __str__(self):
        status = "LOCKED" if self.is_temp_locked else "OK"
        return f"{self.account.name} - {status}"
```

---

### 7. UserSession (security/models.py)

```python
import hashlib

class UserSession(models.Model):
    """
    Track active sessions for concurrency enforcement.
    
    IMPORTANT: Store ip_hash, not raw IP (GDPR/privacy).
    """
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    session_key = models.CharField(
        max_length=100,
        unique=True
    )
    
    # CRITICAL: Hash IP, don't store raw! (spec says ip_hash, not ip_address)
    ip_hash = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="SHA256 hash of IP address for privacy"
    )
    
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    
    is_flagged_suspicious = models.BooleanField(
        default=False,
        help_text="Flagged by concurrency enforcement"
    )
    
    def __str__(self):
        return f"{self.user.email} - {self.session_key[:8]}..."
    
    @staticmethod
    def hash_ip(ip_address: str) -> str:
        """Hash IP address for privacy"""
        return hashlib.sha256(ip_address.encode()).hexdigest()
```

---

## 🔒 DRF Permissions (api/permissions.py)

```python
from rest_framework.permissions import BasePermission

class IsAuthenticatedAndActive(BasePermission):
    """
    User must be authenticated AND their account not locked.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get user's primary account
        account = request.user.owned_accounts.first() or \
                  request.user.account_memberships.first().account
        
        if not account.is_active:
            return False
        
        # Check security lock
        if hasattr(account, 'security_state'):
            if account.security_state.is_temp_locked:
                return False
        
        return True


class IsAccountOwnerOrSupportStaff(BasePermission):
    """
    Allow if:
    - User is superadmin/support staff, OR
    - User is OWNER/ADMIN of the account
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_internal():
            return True
        
        membership = request.user.account_memberships.filter(
            account=obj
        ).first()
        
        return membership and membership.role in ['OWNER', 'ADMIN']
```

---

## 🛡️ Session Enforcement Middleware (security/middleware.py)

```python
from django.utils.deprecation import MiddlewareMixin
from .models import UserSession, AccountSecurityState

class SessionEnforcementMiddleware(MiddlewareMixin):
    """
    Track sessions and enforce concurrent session limits.
    
    For each authenticated request:
    1. Upsert UserSession row
    2. Count active sessions for account
    3. If exceeds Plan.max_concurrent_sessions AND allow_team_members=False:
       - Lock account
       - Return 403 (unless staff)
    """
    
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        
        # Don't restrict internal staff
        if request.user.is_internal():
            return None
        
        # Upsert session
        session_key = request.session.session_key
        ip_hash = UserSession.hash_ip(request.META.get('REMOTE_ADDR', ''))
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        UserSession.objects.update_or_create(
            session_key=session_key,
            defaults={
                'user': request.user,
                'ip_hash': ip_hash,
                'user_agent': user_agent
            }
        )
        
        # Count concurrent sessions for this account
        account = request.user.get_primary_account()
        if not account:
            return None
        
        plan = account.subscription.plan
        
        # Only enforce if plan doesn't allow team members
        if plan.allow_team_members:
            return None
        
        # Count active sessions for all account members
        member_user_ids = account.memberships.values_list('user_id', flat=True)
        active_sessions = UserSession.objects.filter(
            user_id__in=member_user_ids,
            last_seen_at__gte=timezone.now() - timedelta(minutes=30)
        ).count()
        
        # Compare against limit
        limit = plan.max_concurrent_sessions
        
        if active_sessions > limit:
            # Lock account
            security_state, _ = AccountSecurityState.objects.get_or_create(
                account=account
            )
            security_state.is_temp_locked = True
            security_state.last_flag_reason = (
                f"Concurrent session limit exceeded ({active_sessions}/{limit})"
            )
            security_state.warning_count += 1
            security_state.save()
            
            return HttpResponse(
                "Account locked due to suspicious concurrent usage. "
                "Please upgrade or contact support.",
                status=403
            )
        
        return None
```

---

## 📝 Done Conditions

This implementation is complete when:

✅ All 7 models exist with EXACT field names from spec  
✅ User.current_plan is CharField (not ForeignKey)  
✅ Plan has code, display_name, allow_team_members, sla fields  
✅ Plan uses char_limit and req_per_hour (not character_limit/api_rate_limit_per_hour)  
✅ CustomerAccount has owner FK and stripe_customer_id  
✅ Subscription is OneToOneField (not ForeignKey)  
✅ Subscription has is_trial and is_canceled BooleanFields  
✅ AccountSecurityState has concurrent_session_cap  
✅ UserSession uses ip_hash (hashed), not ip_address (raw)  
✅ User has is_paying_customer() and is_internal() methods  
✅ Subscription signal exists to sync User.current_plan  
✅ DRF permissions implemented  
✅ Session enforcement middleware implemented  
✅ All models registered in admin with proper list_display  
✅ Migrations created and applied  
✅ Plan seed data loaded (FREE/PLUS/PRO/ENTERPRISE)  
✅ Basic pytest tests pass  
✅ /docs/AUTH_MODEL.md created  

---

## 🚨 Common Mistakes to Avoid

1. ❌ Don't make User.current_plan a ForeignKey
2. ❌ Don't omit Plan.code and Plan.display_name
3. ❌ Don't use different field names (character_limit vs char_limit)
4. ❌ Don't make Subscription a ForeignKey (must be OneToOne)
5. ❌ Don't store raw IP addresses (must hash)
6. ❌ Don't forget the signal to sync User.current_plan
7. ❌ Don't put User in 'core' app (belongs in 'accounts')
8. ❌ Don't skip the allow_team_members field
9. ❌ Don't implement before getting Orchestrator approval

---

## ✅ First Action

**Django Core Engineer:** Create all 7 models in the exact structure above. Return files for Orchestrator review before proceeding.

