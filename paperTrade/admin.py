from django.contrib import admin

from paperTrade.models import PaperAccountModel, PaperPositionLogModel, PaperPositionModel

# Register your models here.


@admin.register(PaperAccountModel)
class PaperAccountModelAdmin(admin.ModelAdmin):
    pass


@admin.register(PaperPositionModel)
class PaperPositionModelAdmin(admin.ModelAdmin):
    pass


@admin.register(PaperPositionLogModel)
class PaperPositionLogModelAdmin(admin.ModelAdmin):
    pass


