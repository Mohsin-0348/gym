from django.contrib import admin

from classes.models import BaseClass, ClassBooking, ClassSchedule, WeekDay

admin.site.register(BaseClass)
admin.site.register(WeekDay)
admin.site.register(ClassSchedule)
admin.site.register(ClassBooking)
