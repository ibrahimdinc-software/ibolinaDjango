from django.contrib import admin

from .models import SignalModel, SignalTargetsModel
# Register your models here.

class SignalTargetsModelAdminTabularInline(admin.TabularInline):
    model = SignalTargetsModel

@admin.register(SignalModel)
class SignalModelAdmin(admin.ModelAdmin):
    inlines = [SignalTargetsModelAdminTabularInline]
    readonly_fields = ["time"]

