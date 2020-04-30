from django.contrib import admin

from .models import KLADRRegion, KLADRCity, KLADRDistrict


@admin.register(KLADRRegion)
class KLADRRegionAdmin(admin.ModelAdmin):
    list_display = ('region_code', 'name')


admin.site.register(KLADRCity)
admin.site.register(KLADRDistrict)
