from django.contrib import admin
from .models import CarMake, CarModel


# Register your models here.

# CarModelInline clas
class CarModelAdmin(admin.ModelAdmin):
    pass

class CarModelInline (admin.StackedInline):
    model = CarModel
    extra = 2

# CarModelAdmin class

#class CarMakerAdmin(admin.ModelAdmin):


# CarMakeAdmin class with CarModelInline

class CarMakeAdmin(admin.ModelAdmin):
    inlines =  [CarModelInline]

# Register models here

admin.site.register(CarModel, CarModelAdmin)
admin.site.register(CarMake, CarMakeAdmin)
