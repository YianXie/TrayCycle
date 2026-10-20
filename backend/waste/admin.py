from django.contrib import admin

from .models import (
    Capture,
    Compartment,
    Device,
    Dish,
    Label,
    MenuDay,
    MenuItem,
    OverproductionLog,
    Prediction,
    User,
)

admin.site.register(User)
admin.site.register(Dish)
admin.site.register(Compartment)
admin.site.register(MenuDay)
admin.site.register(MenuItem)
admin.site.register(Device)
admin.site.register(Capture)
admin.site.register(Prediction)
admin.site.register(Label)
admin.site.register(OverproductionLog)
