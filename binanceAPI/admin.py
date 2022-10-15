from django.contrib import admin
from django.http import HttpResponseRedirect

from .models import BinanceApiModel, KlineIndicatorModel, PairModel, PairPosModel, PairTpModel, StrategyModel
# Register your models here.

class KlineIndicatorModelAdminTabularInline(admin.TabularInline):
    model = KlineIndicatorModel
    extra = 0

    def get_queryset(self, request):
        parentId = request.get_full_path().split('/')[4]
        if parentId != 'add': 
            qs = super(KlineIndicatorModelAdminTabularInline, self).get_queryset(request)
            ids = qs.filter(pair=parentId).order_by('-openTime').values('pk')[:5]
            qs = KlineIndicatorModel.objects.filter(pk__in=ids).order_by('-openTime')
            return qs

class PairTpModelAdminTabularInline(admin.TabularInline):
    model = PairTpModel
    extra = 0

class PairPosModelAdminTabularInline(admin.TabularInline):
    model = PairPosModel
    extra = 0

@admin.register(BinanceApiModel)
class BinanceApiModelAdmin(admin.ModelAdmin):
    pass

@admin.register(StrategyModel)
class StrategyModelAdmin(admin.ModelAdmin):
    pass

@admin.register(PairModel)
class PairModelAdmin(admin.ModelAdmin):
    inlines=[
        PairTpModelAdminTabularInline,
        PairPosModelAdminTabularInline,
        KlineIndicatorModelAdminTabularInline
    ]
    change_form_template = 'admin/binanceAPI/pairModel.html'
    list_display = ['pair', 'interval' ]


    def response_change(self, request, obj):
        if 'getDatas' in request.POST:
            obj.getDatas()

            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

@admin.register(KlineIndicatorModel)
class KlineIndicatorModelAdmin(admin.ModelAdmin):
    list_display=['__str__','openTime', 'closeTime']
    list_filter = ['pair']