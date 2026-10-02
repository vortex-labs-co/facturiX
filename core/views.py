from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm, ContratoForm
from .models import Cliente, Contrato


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
