from django.contrib import admin
from .models import SummarizationTask, SummaryResult


@admin.register(SummarizationTask)
class SummarizationTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'mode', 'status', 'max_length', 'created_at']
    list_filter = ['status', 'mode', 'created_at']
    search_fields = ['user__username', 'user__email', 'input_text']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Task Details', {
            'fields': ('input_text', 'mode', 'max_length', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset by selecting related user"""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(SummaryResult)
class SummaryResultAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'get_user', 'characters_processed', 'processing_time_ms']
    list_filter = ['task__mode', 'task__created_at']
    search_fields = ['task__user__username', 'task__user__email', 'output_text']
    ordering = ['-task__created_at']

    fieldsets = (
        ('Task Information', {
            'fields': ('task',)
        }),
        ('Result Details', {
            'fields': ('output_text', 'characters_processed', 'processing_time_ms')
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset by selecting related task and user"""
        qs = super().get_queryset(request)
        return qs.select_related('task__user')

    def get_user(self, obj):
        """Display the user who created the task"""
        return obj.task.user.username
    get_user.short_description = 'User'
    get_user.admin_order_field = 'task__user__username'

    def task_id(self, obj):
        """Display the task ID"""
        return obj.task.id
    task_id.short_description = 'Task ID'
    task_id.admin_order_field = 'task__id'
