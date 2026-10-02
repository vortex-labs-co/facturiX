from django.contrib import admin

from .models import Cliente, Contrato, Factura, CuentaCobro, Gasto

admin.site.register(Cliente)
admin.site.register(Contrato)
admin.site.register(Factura)
admin.site.register(CuentaCobro)
admin.site.register(Gasto)
