from datetime import timedelta
from decimal import Decimal
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Cliente, Contrato, Factura, CuentaCobro, Gasto


class Command(BaseCommand):
    help = 'Crea datos de prueba (7 clientes con todo lo relacionado)'

    def handle(self, *args, **options):
        hoy = timezone.now().date()
        datos = [
            ('Andrés Felipe Ramírez', '1032456789', 'andres.ramirez@gmail.com', '3001234567', 'Calle 10 #45-20, Medellín'),
            ('María Camila Torres', '43852100', 'maria.torres@hotmail.com', '3109876543', 'Cra 45 #80-15, Bogotá'),
            ('Juan Pablo Gómez', '80123456', 'jpgomez@outlook.com', '3204567890', 'Carrera 12 #33-08, Cali'),
            ('Laura Valentina Mora', '1098765432', 'laura.mora@gmail.com', '3156789012', 'Transversal 5 #12-44, Medellín'),
            ('Carlos Alberto Restrepo', '70543210', 'carlosr@empresa.co', '3112345678', 'Av. El Poblado #34-90, Medellín'),
            ('Natalia Herrera', '1023456780', 'natalia.h@yahoo.com', '3005678901', 'Calle 60 #22-10, Barranquilla'),
            ('Diego Alejandro Vargas', '79456012', 'diego.vargas@gmail.com', '3128901234', 'Cra 70 #48-30, Itagüí'),
        ]
        conceptos = ['Desarrollo web', 'Consultoría en nube', 'Auditoría de seguridad', 'Soporte mensual', 'Landing page', 'Integración de pagos', 'Mantenimiento']
        for i, (nombre, cedula, correo, tel, direccion) in enumerate(datos, start=1):
            cliente, _ = Cliente.objects.get_or_create(
                cedula=cedula,
                defaults={'nombre': nombre, 'correo': correo, 'telefono': tel, 'direccion': direccion,
                          'autorizacion_datos': True, 'fecha_autorizacion': timezone.now()},
            )
            contrato, _ = Contrato.objects.get_or_create(
                numero_contrato=f'VL-2026-{1000 + i}',
                defaults={'cliente': cliente, 'descripcion': conceptos[i - 1],
                          'fecha_inicio': hoy - timedelta(days=30 * i), 'fecha_fin': hoy + timedelta(days=180),
                          'activo': True},
            )
            if not cliente.facturas.exists():
                Factura.objects.create(
                    cliente=cliente, contrato=contrato, concepto=conceptos[i - 1],
                    valor=Decimal('1500000') + i * Decimal('250000'),
                    fecha_vencimiento=hoy + timedelta(days=15 * i),
                    estado='pagada' if i % 3 == 0 else 'pendiente',
                    pago_validado=i % 3 == 0,
                )
            if not cliente.cuentas.exists():
                cc = CuentaCobro(cliente=cliente, contrato=contrato, descripcion=f'Cuenta de cobro {conceptos[i-1]}',
                                 valor=Decimal('1500000') + i * Decimal('250000'), fecha=hoy - timedelta(days=i * 5))
                cc.archivo.save(f'cuenta_{i}.pdf', ContentFile(b'%PDF-1.4 demo'), save=True)
            if i % 2 == 0:
                g = Gasto(descripcion=f'Gasto operativo {i}', valor=Decimal('180000') * i, fecha=hoy - timedelta(days=i * 3))
                g.archivo.save(f'gasto_{i}.pdf', ContentFile(b'%PDF-1.4 demo'), save=True)
        self.stdout.write(self.style.SUCCESS('Datos de prueba creados: 7 clientes con contratos, facturas, cuentas y gastos'))
