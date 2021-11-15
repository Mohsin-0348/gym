from django.contrib import admin

from attendances.models import (
    ClassAttendance,
    ClassWorkOut,
    EmployeeAttendance,
    GymAttendance,
    GymWorkOut,
    WorkOut,
)

admin.site.register(ClassWorkOut)
admin.site.register(GymWorkOut)
admin.site.register(GymAttendance)
admin.site.register(WorkOut)
admin.site.register(EmployeeAttendance)
admin.site.register(ClassAttendance)
