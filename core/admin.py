from django.contrib import admin

from .models import Cliente, Contrato, Factura

admin.site.register(Cliente)
admin.site.register(Contrato)
admin.site.register(Factura)
