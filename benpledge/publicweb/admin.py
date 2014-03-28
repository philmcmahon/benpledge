from django.contrib import admin
from publicweb.models import Measure, Pledge, UserProfile, Dwelling, HatResultsDatabase, HatMeasuresList, Area, TopTip, Organisation

admin.site.register(Measure)
admin.site.register(Pledge)
admin.site.register(UserProfile)
admin.site.register(Dwelling)
admin.site.register(Area)
admin.site.register(TopTip)
admin.site.register(Organisation)