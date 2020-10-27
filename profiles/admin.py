from django.contrib import admin

from profiles.models import Profile


class ProfileInline(admin.TabularInline):
    fields = ['user', 'current_balance']
    list_display = ('last_first', 'current_balanace')
    readonly_fields = ['current_balance']
    model = Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'current_balance', 'role', 'status', 'grade_level', 'school',
              'room', 'phone', 'lunch_id', 'user_number', 'student_dcid', 'user_dcid', 'last_sync']
    list_display = ('last_first', 'role', 'lunch_id', 'current_balance')
    list_filter = ['role', 'status', 'school']
    inlines = [ProfileInline, ]
    ordering = ['user__last_name']
    readonly_fields = ['grade_level', 'last_sync', 'lunch_id', 'phone',
                       'role', 'room', 'school', 'student_dcid', 'user_dcid', 'user_number']
    search_fields = ['user__first_name',
                     'user__last_name', 'user_number', 'lunch_id']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
