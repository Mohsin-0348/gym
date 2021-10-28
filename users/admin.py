from django.contrib import admin

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


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileStackedInline]
    model = User
    list_display = ['username', 'email']
