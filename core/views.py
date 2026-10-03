from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
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
    fact_por_moneda = {}
    for m in ['COP', 'USD', 'EUR']:
        fact_por_moneda[m] = Factura.objects.filter(moneda=m).aggregate(t=Sum('valor'))['t'] or 0
    facturas_pendientes = Factura.objects.filter(estado='pendiente').count()
    total_facturado = sum(f.valor_cop_estimado for f in Factura.objects.all()) or 0
    from dateutil.relativedelta import relativedelta
    meses = []
    series_fact = []
    series_gas = []
    series_cuentas = []
    for i in range(5, -1, -1):
        ref = hoy - relativedelta(months=i)
        meses.append(ref.strftime('%m/%Y'))
        series_fact.append(float(sum(f.valor_cop_estimado for f in Factura.objects.filter(fecha_emision__month=ref.month, fecha_emision__year=ref.year)) or 0))
        series_gas.append(float(Gasto.objects.filter(fecha__month=ref.month, fecha__year=ref.year).aggregate(t=Sum('valor'))['t'] or 0))
        series_cuentas.append(float(CuentaCobro.objects.filter(fecha__month=ref.month, fecha__year=ref.year).aggregate(t=Sum('valor'))['t'] or 0))
    return render(request, 'dashboard.html', {
        'total_facturado': total_facturado,
        'total_cobrado': total_cobrado,
        'total_gastos': total_gastos,
        'rendimiento': total_facturado - total_gastos,
        'facturas_pendientes': facturas_pendientes,
        'meses': meses, 'series_fact': series_fact, 'series_gas': series_gas, 'series_cuentas': series_cuentas,
        'capital_caja': total_facturado - total_gastos,
        'total_ingresos': total_facturado + total_cobrado,
        'fact_por_moneda': fact_por_moneda,
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


@login_required
def borrar(request, modelo, pk):
    modelos = {'cliente': Cliente, 'contrato': Contrato, 'factura': Factura, 'cuenta': CuentaCobro, 'gasto': Gasto}
    M = modelos.get(modelo)
    obj = get_object_or_404(M, pk=pk)
    nombre_campo = {'cliente': 'cliente_lista', 'contrato': 'contrato_lista', 'factura': 'factura_lista', 'cuenta': 'cuenta_lista', 'gasto': 'gasto_lista'}
    if request.method == 'POST':
        from django.db.models import ProtectedError
        try:
            obj.delete()
            messages.success(request, 'Registro eliminado.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar: tiene registros relacionados.')
        return redirect(nombre_campo[modelo])
    return render(request, 'core/confirmar_borrar.html', {'obj': obj, 'modelo': modelo})


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
def cuenta_editar(request, pk):
    cuenta = get_object_or_404(CuentaCobro, pk=pk)
    form = CuentaCobroForm(request.POST or None, request.FILES or None, instance=cuenta)
    if form.is_valid():
        form.save()
        return redirect('cuenta_lista')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Editar cuenta de cobro', 'enctype': True})


@login_required
def cuenta_vista(request, pk):
    cuenta = get_object_or_404(CuentaCobro, pk=pk)
    url = cuenta.archivo.url if cuenta.archivo else ''
    es_pdf = url.lower().endswith('.pdf')
    es_imagen = url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    return render(request, 'core/cuenta_vista.html', {'cuenta': cuenta, 'es_pdf': es_pdf, 'es_imagen': es_imagen})


@login_required
def gasto_vista(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    url = gasto.archivo.url if gasto.archivo else ''
    es_pdf = url.lower().endswith('.pdf')
    es_imagen = url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    return render(request, 'core/gasto_vista.html', {'gasto': gasto, 'es_pdf': es_pdf, 'es_imagen': es_imagen})


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
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    facturas = Factura.objects.all()
    cuentas = CuentaCobro.objects.all()
    gastos = Gasto.objects.all()
    if desde:
        facturas = facturas.filter(fecha_emision__gte=desde)
        cuentas = cuentas.filter(fecha__gte=desde)
        gastos = gastos.filter(fecha__gte=desde)
    if hasta:
        facturas = facturas.filter(fecha_emision__lte=hasta)
        cuentas = cuentas.filter(fecha__lte=hasta)
        gastos = gastos.filter(fecha__lte=hasta)
    return render(request, 'core/informe.html', {
        'facturas': facturas, 'cuentas': cuentas, 'gastos': gastos, 'desde': desde, 'hasta': hasta,
        'total_facturas': sum(f.valor_cop_estimado for f in facturas) or 0,
        'total_cuentas': cuentas.aggregate(t=Sum('valor'))['t'] or 0,
        'total_gastos': gastos.aggregate(t=Sum('valor'))['t'] or 0,
        'balance': (facturas.aggregate(t=Sum('valor'))['t'] or 0) - (gastos.aggregate(t=Sum('valor'))['t'] or 0),
    })


@login_required
def informe_csv(request):
    import csv
    hoy = timezone.now().date()
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    facturas = Factura.objects.all()
    if desde:
        facturas = facturas.filter(fecha_emision__gte=desde)
    if hasta:
        facturas = facturas.filter(fecha_emision__lte=hasta)
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="informe_facturas.csv"'
    writer = csv.writer(response)
    writer.writerow(['Numero', 'Cliente', 'Fecha emision', 'Vencimiento', 'Valor', 'Estado'])
    for f in facturas:
        writer.writerow([f.numero, f.cliente.nombre, f.fecha_emision, f.fecha_vencimiento, f.valor, f.get_estado_display()])
    return response
