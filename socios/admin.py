from django.contrib import admin
from .models import Socio, PagoMensualidad, Prestamo

admin.site.register(Socio)
admin.site.register(PagoMensualidad)
admin.site.register(Prestamo)

# Register your models here.
