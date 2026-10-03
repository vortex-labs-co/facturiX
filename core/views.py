from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from .forms import ClienteForm, ContratoForm, FacturaForm, CuentaCobroForm, GastoForm
from .models import Cliente, Contrato, Factura, CuentaCobro, Gasto


@login_required
def dashboard(request):
    hoy = timezone.now().date()
    total_facturado = Factura.objects.aggregate(t=Sum('valor'))['t'] or 0
    total_cobrado = CuentaCobro.objects.aggregate(t=Sum('valor'))['t'] or 0
    total_gastos = Gasto.objects.aggregate(t=Sum('valor'))['t'] or 0
    facturas_pendientes = Factura.objects.filter(estado='pendiente').count()
    return render(request, 'dashboard.html', {
        'total_facturado': total_facturado,
        'total_cobrado': total_cobrado,
        'total_gastos': total_gastos,
        'rendimiento': total_facturado - total_gastos,
        'facturas_pendientes': facturas_pendientes,
    })


@login_required
def cliente_lista(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.filter(nombre__icontains=q) | Cliente.objects.filter(cedula__icontains=q)
    return render(request, 'core/cliente_lista.html', {'clientes': clientes.distinct(), 'q': q})


@login_required
def cliente_crear(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('cliente_lista')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Nuevo cliente'})


@login_required
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        return redirect('cliente_lista')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Editar cliente'})


@login_required
def cliente_detalle(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'core/cliente_detalle.html', {'cliente': cliente})


@login_required
def contrato_lista(request):
    contratos = Contrato.objects.select_related('cliente').all()
    return render(request, 'core/contrato_lista.html', {'contratos': contratos})


@login_required
def contrato_crear(request):
    form = ContratoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('contrato_lista')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Nuevo contrato'})


@login_required
def contrato_editar(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    form = ContratoForm(request.POST or None, instance=contrato)
    if form.is_valid():
        form.save()
        return redirect('contrato_lista')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Editar contrato'})


@login_required
def contrato_documento(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    return render(request, 'core/contrato_documento.html', {'contrato': contrato})


@login_required
def contrato_pdf(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    html = render_to_string('core/contrato_documento_pdf.html', {'contrato': contrato})
    from django.http import HttpResponse as _HR
    from xhtml2pdf import pisa
    response = _HR(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{contrato.numero_contrato}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response


def _factura_pdf(factura):
    html = render_to_string('core/factura_pdf.html', {'factura': factura})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{factura.numero}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response


@login_required
def factura_lista(request):
    facturas = Factura.objects.select_related('cliente').all()
    return render(request, 'core/factura_lista.html', {'facturas': facturas})


@login_required
def factura_crear(request):
    form = FacturaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('factura_lista')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Nueva factura'})


@login_required
def factura_pdf(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    return _factura_pdf(factura)


@login_required
def factura_vista(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    return render(request, 'core/factura_vista.html', {'factura': factura})


@login_required
def factura_enviar(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        pdf = _factura_pdf(factura)
        email = EmailMessage(
            subject=f'Factura {factura.numero} - Vortex Labs',
            body=f'Estimado/a {factura.cliente.nombre}, adjunto encontrará la factura {factura.numero}.',
            to=[factura.cliente.correo],
        )
        email.attach(f'{factura.numero}.pdf', pdf.content, 'application/pdf')
        email.send()
        factura.enviada_email = True
        factura.estado = 'enviada'
        factura.save()
        return redirect('factura_lista')
    return render(request, 'core/factura_enviar.html', {'factura': factura})


@login_required
def cuenta_lista(request):
    cuentas = CuentaCobro.objects.select_related('cliente').all()
    return render(request, 'core/cuenta_lista.html', {'cuentas': cuentas})


@login_required
def cuenta_crear(request):
    form = CuentaCobroForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('cuenta_lista')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Nueva cuenta de cobro', 'enctype': True})


@login_required
def gasto_lista(request):
    gastos = Gasto.objects.all()
    return render(request, 'core/gasto_lista.html', {'gastos': gastos})


@login_required
def gasto_crear(request):
    form = GastoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('gasto_lista')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Nuevo gasto', 'enctype': True})


@login_required
def informe(request):
    hoy = timezone.now().date()
    mes = int(request.GET.get('mes', hoy.month))
    anio = int(request.GET.get('anio', hoy.year))
    facturas = Factura.objects.filter(fecha_emision__month=mes, fecha_emision__year=anio)
    cuentas = CuentaCobro.objects.filter(fecha__month=mes, fecha__year=anio)
    gastos = Gasto.objects.filter(fecha__month=mes, fecha__year=anio)
    return render(request, 'core/informe.html', {
        'facturas': facturas, 'cuentas': cuentas, 'gastos': gastos, 'mes': mes, 'anio': anio,
        'total_facturas': facturas.aggregate(t=Sum('valor'))['t'] or 0,
        'total_cuentas': cuentas.aggregate(t=Sum('valor'))['t'] or 0,
        'total_gastos': gastos.aggregate(t=Sum('valor'))['t'] or 0,
        'balance': (facturas.aggregate(t=Sum('valor'))['t'] or 0) - (gastos.aggregate(t=Sum('valor'))['t'] or 0),
    })
