from django.contrib import admin
from .models import (
    Author,
    Image,
    Category,
    Place,
    Year
)

admin.site.register(Author)
admin.site.register(Image)
admin.site.register(Category)
admin.site.register(Place)
admin.site.register(Year)
