from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    path('clientes/nuevo/', views.cliente_crear, name='cliente_crear'),
    path('clientes/<int:pk>/', views.cliente_detalle, name='cliente_detalle'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path('contratos/', views.contrato_lista, name='contrato_lista'),
    path('contratos/nuevo/', views.contrato_crear, name='contrato_crear'),
    path('contratos/<int:pk>/editar/', views.contrato_editar, name='contrato_editar'),
    path('contratos/<int:pk>/documento/', views.contrato_documento, name='contrato_documento'),
    path('contratos/<int:pk>/pdf/', views.contrato_pdf, name='contrato_pdf'),
    path('facturas/', views.factura_lista, name='factura_lista'),
    path('facturas/nueva/', views.factura_crear, name='factura_crear'),
    path('facturas/<int:pk>/pdf/', views.factura_pdf, name='factura_pdf'),
    path('facturas/<int:pk>/vista/', views.factura_vista, name='factura_vista'),
    path('facturas/<int:pk>/enviar/', views.factura_enviar, name='factura_enviar'),
    path('cuentas/', views.cuenta_lista, name='cuenta_lista'),
    path('cuentas/nueva/', views.cuenta_crear, name='cuenta_crear'),
    path('cuentas/<int:pk>/vista/', views.cuenta_vista, name='cuenta_vista'),
    path('gastos/', views.gasto_lista, name='gasto_lista'),
    path('gastos/nuevo/', views.gasto_crear, name='gasto_crear'),
    path('gastos/<int:pk>/vista/', views.gasto_vista, name='gasto_vista'),
    path('informe/', views.informe, name='informe'),
]
