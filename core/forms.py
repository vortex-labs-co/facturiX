from django import forms

from .models import Cliente, Contrato, Factura, CuentaCobro, Gasto


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_persona', 'nombre', 'cedula', 'correo', 'telefono_pais', 'telefono',
                  'direccion', 'fecha_nacimiento', 'autorizacion_datos', 'fecha_autorizacion']
        widgets = {
            'fecha_autorizacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'telefono': forms.TextInput(attrs={'pattern': '[0-9]+', 'title': 'Solo números', 'inputmode': 'numeric'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('tipo_persona') == 'natural':
            fn = cleaned.get('fecha_nacimiento')
            if not fn:
                self.add_error('fecha_nacimiento', 'Requerida para persona natural.')
            else:
                from datetime import date
                edad = date.today().year - fn.year - ((date.today().month, date.today().day) < (fn.month, fn.day))
                if edad < 18:
                    self.add_error('fecha_nacimiento', 'El cliente debe ser mayor de 18 años.')
        return cleaned


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
