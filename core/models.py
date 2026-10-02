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
