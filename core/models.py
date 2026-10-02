from django.db import models
from django.urls import reverse


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    cedula = models.CharField(max_length=30, unique=True, verbose_name='Cédula/NIT')
    correo = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=300, blank=True)
    autorizacion_datos = models.BooleanField(
        default=False, verbose_name='Autorización tratamiento de datos')
    fecha_autorizacion = models.DateTimeField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.cedula})'

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
    pago_validado = models.BooleanField(default=False)
    enviada_email = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha_emision']

    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = Factura.objects.order_by('-id').first()
            siguiente = (ultimo.id if ultimo else 0) + 1
            self.numero = f'FAC-{siguiente:06d}'
        super().save(*args, **kwargs)

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
