from django.contrib import admin

from members.models import Member
from users.models import (
    Address,
    ResetPassword,
    UnitOfHistory,
    User,
    UserDeviceToken,
    UserOTP,
    UserProfile,
    UserSocialAccount,
)

admin.site.register(UnitOfHistory)
admin.site.register(Address)
admin.site.register(ResetPassword)
admin.site.register(UserSocialAccount)
admin.site.register(UserDeviceToken)
admin.site.register(UserOTP)


class ProfileStackedInline(admin.StackedInline):
    model = UserProfile


class MemberStackedInline(admin.StackedInline):
    model = Member


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileStackedInline, MemberStackedInline]
    model = User
    list_display = ['username', 'email', 'is_active', 'is_staff', 'is_superuser']
