from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Dealer)
admin.site.register(Car)
admin.site.register(UsedCar)
admin.site.register(Review)
admin.site.register(News)
admin.site.register(CarLoan)
admin.site.register(CarValuation)
