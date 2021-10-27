from django.contrib import admin

from users.models import (
    ResetPassword,
    UnitOfHistory,
    User,
    UserDeviceToken,
    UserOTP,
    UserProfile,
    UserSocialAccount,
)

admin.site.register(User)
admin.site.register(UnitOfHistory)
admin.site.register(UserProfile)
admin.site.register(ResetPassword)
admin.site.register(UserSocialAccount)
admin.site.register(UserDeviceToken)
admin.site.register(UserOTP)
