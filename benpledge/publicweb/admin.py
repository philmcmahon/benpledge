from django.contrib import admin
from publicweb.models import Measure, Pledge, UserProfile, Dwelling, HatResultsDatabase, HatMeasuresList, Area, TopTip, Organisation, HomepageCheckList, AboutPage, FundingOption, Provider

admin.site.register(Measure)
admin.site.register(UserProfile)
admin.site.register(Dwelling)
admin.site.register(Area)
admin.site.register(TopTip)
admin.site.register(Organisation)
admin.site.register(HomepageCheckList)
admin.site.register(AboutPage)
admin.site.register(FundingOption)
admin.site.register(Provider)

class PledgeAdmin(admin.ModelAdmin):
    raw_id_fields = ('hat_results',)

admin.site.register(Pledge, PledgeAdmin)