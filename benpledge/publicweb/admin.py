from django.contrib import admin
from publicweb.models import Measure, Pledge, UserProfile, Dwelling, HatResultsDatabase, HatMeasuresList, Area

admin.site.register(Measure)
admin.site.register(Pledge)
admin.site.register(UserProfile)
admin.site.register(Dwelling)
admin.site.register(HatResultsDatabase)
admin.site.register(HatMeasuresList)
admin.site.register(Area)