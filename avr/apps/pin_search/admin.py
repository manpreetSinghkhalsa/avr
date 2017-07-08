from django.contrib import admin
from apps.pin_search import models as pin_search_models
# Register your models here.
admin.register(pin_search_models.Office)
admin.register(pin_search_models.OfficeLocation)