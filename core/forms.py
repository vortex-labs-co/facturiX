from django import forms

from .models import Cliente, Contrato


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
