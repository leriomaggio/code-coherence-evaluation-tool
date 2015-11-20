from django.contrib import admin

# Register your models here.

from .models import Example

class ExampleAdmin(admin.ModelAdmin):
    list_display = ['id', 'method', 'target']
    list_filter = ['target', 'method__project']

admin.site.register(Example, ExampleAdmin)
