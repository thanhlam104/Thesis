from django.contrib import admin

# Register your models here.

from .models import Project
# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name','date']
    list_filter = ['date']
admin.site.register(Project, ProjectAdmin)