from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.test import RequestFactory
from xhtml2pdf import pisa

from core.models import Factura


class Command(BaseCommand):
    help = 'Envía automáticamente las facturas con pago validado que aún no han sido enviadas'

    def handle(self, *args, **options):
        pendientes = Factura.objects.filter(pago_validado=True, enviada_email=False)
        for factura in pendientes:
            html = render_to_string('core/factura_pdf.html', {'factura': factura})
            response = HttpResponse(content_type='application/pdf')
            pisa.CreatePDF(html, dest=response)
            email = EmailMessage(
                subject=f'Factura {factura.numero} - Vortex Labs',
                body=f'Estimado/a {factura.cliente.nombre}, adjunto encontrará la factura {factura.numero}.',
                to=[factura.cliente.correo],
            )
            email.attach(f'{factura.numero}.pdf', response.content, 'application/pdf')
            email.send()
            factura.enviada_email = True
            factura.estado = 'enviada'
            factura.save()
            self.stdout.write(f'Enviada: {factura.numero}')
        self.stdout.write(self.style.SUCCESS(f'Total enviadas: {pendientes.count()}'))
