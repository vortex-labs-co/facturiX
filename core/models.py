from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from datetime import date

TELEFONO_VALIDATOR = RegexValidator(r'^\d+$', 'El teléfono solo debe contener números.')

TIPOS_PERSONA = [('natural', 'Persona Natural'), ('juridica', 'Persona Jurídica')]

PAISES = [
    ('CO', 'Colombia (+57)'), ('US', 'Estados Unidos (+1)'), ('MX', 'México (+52)'),
    ('ES', 'España (+34)'), ('AR', 'Argentina (+54)'), ('CL', 'Chile (+56)'),
    ('PE', 'Perú (+51)'), ('BR', 'Brasil (+55)'), ('PA', 'Panamá (+507)'),
    ('EC', 'Ecuador (+593)'), ('VE', 'Venezuela (+58)'), ('Otro', 'Otro'),
]


class Cliente(models.Model):
    tipo_persona = models.CharField(max_length=20, choices=TIPOS_PERSONA, default='juridica')
    nombre = models.CharField(max_length=200)
    cedula = models.CharField(max_length=30, unique=True, verbose_name='Cédula/NIT')
    correo = models.EmailField()
    telefono_pais = models.CharField(max_length=10, choices=PAISES, default='CO', verbose_name='País del teléfono')
    telefono = models.CharField(max_length=30, blank=True, validators=[TELEFONO_VALIDATOR])
    direccion = models.CharField(max_length=300, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    autorizacion_datos = models.BooleanField(
        default=False, verbose_name='Autorización tratamiento de datos')
    fecha_autorizacion = models.DateTimeField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.cedula})'

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

    def clean(self):
        if self.tipo_persona == 'natural':
            if not self.fecha_nacimiento:
                raise ValidationError({'fecha_nacimiento': 'Requerida para persona natural.'})
            edad = self.edad
            if edad is not None and edad < 18:
                raise ValidationError({'fecha_nacimiento': 'El cliente debe ser mayor de 18 años.'})

    def get_absolute_url(self):
        return reverse('cliente_detalle', args=[self.pk])


ESTADOS = [('pendiente', 'Pendiente'), ('enviada', 'Enviada'), ('pagada', 'Pagada')]


class Factura(models.Model):
    numero = models.CharField(max_length=40, unique=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='facturas')
    contrato = models.ForeignKey('Contrato', on_delete=models.SET_NULL, null=True, blank=True)
    concepto = models.TextField()
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    moneda = models.CharField(max_length=3, default='COP', choices=[('COP', 'COP'), ('USD', 'USD'), ('EUR', 'EUR')])
    pago_validado = models.BooleanField(default=False)
    pago_verificado_fecha = models.DateTimeField(null=True, blank=True)
    tasa_cop = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    valor_cop = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    enviada_email = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha_emision']

    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = Factura.objects.order_by('-id').first()
            siguiente = (ultimo.id if ultimo else 0) + 1
            self.numero = f'FAC-{siguiente:06d}'
        # Al validar el pago (verificado en cuenta bancaria) se fija la tasa del momento
        if self.pago_validado and self.valor_cop is None:
            from django.utils import timezone
            from .tasas import tasa_a_cop
            self.tasa_cop = tasa_a_cop(self.moneda)
            self.valor_cop = (self.valor * self.tasa_cop).quantize(Decimal('0.01'))
            self.pago_verificado_fecha = timezone.now()
        super().save(*args, **kwargs)

    @property
    def valor_cop_estimado(self):
        """Valor en COP usado para estadísticas: verificado si existe, si no el valor sin convertir."""
        return self.valor_cop if self.valor_cop is not None else self.valor

    def __str__(self):
        return self.numero


class Contrato(models.Model):
    numero_contrato = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='contratos')
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Contratos'
        ordering = ['numero_contrato']

    def __str__(self):
        return self.numero_contrato


class CuentaCobro(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cuentas')
    contrato = models.ForeignKey(Contrato, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.CharField(max_length=300)
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    fecha = models.DateField()
    archivo = models.FileField(upload_to='cuentas/')
    moneda = models.CharField(max_length=3, default='COP', choices=[('COP', 'COP'), ('USD', 'USD'), ('EUR', 'EUR')])
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Cuentas de cobro'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.descripcion} - {self.cliente.nombre}'


class Gasto(models.Model):
    descripcion = models.CharField(max_length=300)
    concepto = models.CharField(max_length=200, blank=True, verbose_name='Concepto')
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    fecha = models.DateField()
    archivo = models.FileField(upload_to='gastos/')
    moneda = models.CharField(max_length=3, default='COP', choices=[('COP', 'COP'), ('USD', 'USD'), ('EUR', 'EUR')])
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return self.descripcion
