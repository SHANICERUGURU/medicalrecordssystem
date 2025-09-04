from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role',)
    search_fields = ('username', 'email', 'first_name', 'last_name')


class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth','phone')
    search_fields = ('first_name', 'last_name', 'phone', 'user__username', 'user__email')



admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(User)
admin.site.register(Doctor)


