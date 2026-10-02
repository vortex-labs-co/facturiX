from django import forms

from .models import Cliente, Contrato, Factura, CuentaCobro, Gasto


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'cedula', 'correo', 'telefono', 'direccion',
                  'autorizacion_datos', 'fecha_autorizacion']
        widgets = {'fecha_autorizacion': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['numero_contrato', 'cliente', 'descripcion', 'fecha_inicio', 'fecha_fin', 'activo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cliente', 'contrato', 'concepto', 'valor', 'fecha_vencimiento', 'estado', 'pago_validado']
        widgets = {'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'})}


class CuentaCobroForm(forms.ModelForm):
    class Meta:
        model = CuentaCobro
        fields = ['cliente', 'contrato', 'descripcion', 'valor', 'fecha', 'archivo']
        widgets = {'fecha': forms.DateInput(attrs={'type': 'date'})}


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['descripcion', 'valor', 'fecha', 'archivo']
        widgets = {'fecha': forms.DateInput(attrs={'type': 'date'})}
