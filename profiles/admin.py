from django.contrib import admin

from profiles.models import Profile


class StudentsInline(admin.TabularInline):
    extra = 0
    fields = ["user", "current_balance"]
    list_display = ("last_first", "current_balanace")
    readonly_fields = ["user", "current_balance"]
    model = Profile
    verbose_name = "Homeroom Student"
    verbose_name_plural = "Homeroom Students"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("last_first", "role", "current_balance", "last_sync")
    list_filter = ["role", "active", "pending", "grade", "school"]
    ordering = ["user__last_name"]
    readonly_fields = [
        "cards_printed",
        "children",
        "grade",
        "homeroom_teacher",
        "last_sync",
        "phone",
        "role",
        "room",
        "school",
        "student_dcid",
        "user_dcid",
        "user_number",
    ]
    search_fields = ["user__first_name", "user__last_name", "user_number"]

    def get_fields(self, request, obj=None):
        role_fields = {
            Profile.STAFF: [
                "user",
                "current_balance",
                "role",
                "active",
                "pending",
                "grade",
                "room",
                "phone",
                "cards_printed",
                "user_number",
                "user_dcid",
                "last_sync",
            ],
            Profile.STUDENT: [
                "user",
                "current_balance",
                "role",
                "active",
                "pending",
                "grade",
                "homeroom_teacher",
                "school",
                "cards_printed",
                "user_number",
                "student_dcid",
                "last_sync",
            ],
            Profile.GUARDIAN: [
                "user",
                "role",
                "active",
                "user_dcid",
                "children",
                "last_sync",
            ],
        }
        return role_fields.get(obj.role, [])

    def get_inlines(self, request, obj):
        if obj.role == Profile.STAFF:
            return [
                StudentsInline,
            ]
        return []

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
