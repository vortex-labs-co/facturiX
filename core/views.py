from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from .forms import ClienteForm, ContratoForm, FacturaForm
from .models import Cliente, Contrato, Factura


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


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
