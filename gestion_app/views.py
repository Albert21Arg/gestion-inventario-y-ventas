from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
import random
from django.http import HttpResponse
from openpyxl import Workbook # type: ignore
from decimal import Decimal,  InvalidOperation
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import get_template
from xhtml2pdf import pisa # type: ignore
from django.db.models import Q
from django.utils.text import slugify  # para limpiar el nombre
from datetime import datetime
from django.db.models import Sum, Max

# ====================
# CLIENTES
# ====================
@method_decorator(login_required, name='dispatch')
class ClienteListView(ListView):
    model = Cliente
    template_name = "clientes/lista.html"
    context_object_name = "clientes"

@method_decorator(login_required, name='dispatch')
class ClienteDetailView(DetailView):
    model = Cliente
    template_name = "clientes/detalle.html"
    context_object_name = "cliente"

@method_decorator(login_required, name='dispatch')
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes-lista")

@method_decorator(login_required, name='dispatch')
class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes-lista")

@receiver(post_save, sender=Venta)
def actualizar_tipo_cliente(sender, instance, **kwargs):
    cliente = instance.cliente
    cliente.actualizar_tipo()

# ====================
# PRODUCTOS
# ====================
@method_decorator(login_required, name='dispatch')
class ProductoListView(ListView):
    model = Producto
    template_name = "productos/lista.html"
    context_object_name = "productos"

@method_decorator(login_required, name='dispatch')
class ProductoDetailView(DetailView):
    model = Producto
    template_name = "productos/detalle.html"
    context_object_name = "producto"

@method_decorator(login_required, name='dispatch')
class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos/form.html"
    success_url = reverse_lazy("productos-lista")

@method_decorator(login_required, name='dispatch')
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos/form.html"
    success_url = reverse_lazy("productos-lista")


# ====================
# VENTAS
# ====================
@method_decorator(login_required, name='dispatch')
class VentaListView(ListView):
    model = Venta
    template_name = "productos/lista.html"
    context_object_name = "productos"

@method_decorator(login_required, name='dispatch')
class VentaDetailView(DetailView):
    model = Venta
    template_name = "productos/detalle.html"
    context_object_name = "venta"

@method_decorator(login_required, name='dispatch')
class VentaCreateView(CreateView):
    model = Venta
    form_class = VentaForm
    template_name = "productos/form.html"
    success_url = reverse_lazy("productos-lista")

def listado_productos(request):
    productos = Producto.objects.filter(pk__isnull=False)
    return render(request, "productos/listado_productos.html", {"productos": productos})


# Decorador para solo admin
def admin_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_staff)(view_func))
    return decorated_view_func

def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    context = {
        'producto': producto,
        'admin_telefono': '573004407014',  # sin '+'
    }
    return render(request, 'productos/detalle_producto.html', context)

def lista_productos(request):
    query = request.GET.get('q', '')  # Obtener término de búsqueda
    if query:
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )
    else:
        productos = Producto.objects.all()

    context = {
        'productos': productos,
        'query': query,
        'admin_telefono': '573004407014',  # número para WhatsApp
    }
    return render(request, 'productos/lista_productos.html', context)

# Crear producto
@admin_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listado_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/formulario.html', {'form': form, 'accion': 'Crear'})

# Editar producto
@admin_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listado_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/formulario.html', {'form': form, 'accion': 'Editar'})

# Eliminar producto
@admin_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('listado_productos')
    return render(request, 'productos/eliminar.html', {'producto': producto})

def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, "clientes/cliente_detail.html", {"cliente": cliente})

def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    detalles = venta.detalles.all()  # relación con DetalleVenta
    return render(request, "ventas/detalle_venta.html", {
        "venta": venta,
        "detalles": detalles
    })

def admin_required(view_func):
    """Decorator para permitir solo superusuarios"""
    decorated_view_func = user_passes_test(lambda u: u.is_superuser, login_url='/')(view_func)
    return decorated_view_func

@admin_required
def crear_venta(request):
    if request.method == "POST":
        # === Cliente ===
        cliente_id = request.POST.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debe seleccionar un cliente válido")
            return redirect('crear_venta')

        cliente = get_object_or_404(Cliente, id=cliente_id)

        # === Productos ===
        productos_ids = request.POST.getlist("producto_id[]")
        cantidades = request.POST.getlist("cantidad[]")
        precios = request.POST.getlist("precio[]")  # precios personalizados

        # === Abono y pago completo ===
        abono_raw = request.POST.get("abono", "0").replace(".", "")
        pago_completo_checked = "pago_completo" in request.POST

        try:
            abono = Decimal(abono_raw)
            if abono < 0:
                abono = Decimal('0.00')
        except:
            abono = Decimal('0.00')

        # === Crear venta preliminar ===
        venta = Venta(cliente=cliente, total=Decimal('0.00'))
        venta.save()  # Guardar para obtener ID

        total = Decimal('0.00')
        productos_validos = 0

        # === Crear detalles de venta ===
        for prod_id, cant, prec in zip(productos_ids, cantidades, precios):
            if not prod_id or int(cant) <= 0:
                continue
            producto = get_object_or_404(Producto, id=prod_id)
            cantidad = int(cant)
            try:
                precio = Decimal(prec)
                if precio < 0:
                    precio = producto.precio  # fallback si precio inválido
            except:
                precio = producto.precio

            subtotal = precio * cantidad
            total += subtotal

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio  # precio personalizado asignado
                # subtotal no se pasa porque se calcula en el save() del modelo
            )
            productos_validos += 1

        if productos_validos == 0:
            venta.delete()
            messages.error(request, "Debe agregar al menos un producto válido")
            return redirect('crear_venta')

        # === Ajustar abono y pago completo ===
        if abono > total:
            abono = total

        venta.total = total
        venta.abono = abono
        venta.restante = total - abono
        venta.pago_completo = pago_completo_checked or (venta.restante == 0)
        venta.save()

        # === Redirigir o mostrar PDF ===
        return render(request, "ventas/descargar_y_redir.html", {"venta": venta})

    # GET: renderizar formulario
    clientes = Cliente.objects.all()
    productos = Producto.objects.all()
    return render(request, "ventas/crear_venta.html", {"clientes": clientes, "productos": productos})


@admin_required
def descargar_factura(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    template = get_template("ventas/factura.html")
    html = template.render({"venta": venta})

    # Formatea la fecha (por ejemplo: 2025-10-25)
    fecha_str = venta.fecha.strftime("%Y-%m-%d") if venta.fecha else datetime.now().strftime("%Y-%m-%d")

    # Limpia el nombre del cliente para el nombre del archivo
    nombre_cliente = slugify(venta.cliente.nombre)

    # Nombre final del archivo: fecha_nombrecliente.pdf
    nombre_archivo = f"{fecha_str}_{nombre_cliente}.pdf"

    # Configura la respuesta HTTP con el nombre del archivo
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'

    # Genera el PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error al generar el PDF")

    return response

@admin_required
def exportar_clientes_excel(request):
    # Crear workbook y hoja
    wb = Workbook()
    ws = wb.active
    ws.title = "Clientes y Ventas"

    # Encabezados
    ws.append([
        "Nombre Cliente", "Tipo", "Celular",
        "Código Venta", "Producto",
        "Cantidad", "Precio Unitario", "Valor Cantidad",
        "Total Venta", "Abono", "Restante"
    ])

    clientes = Cliente.objects.all().prefetch_related("ventas__detalles__producto")

    for cliente in clientes:
        if cliente.ventas.exists():
            for venta in cliente.ventas.all():
                if venta.detalles.exists():
                    for detalle in venta.detalles.all():
                        ws.append([
                            cliente.nombre,
                            cliente.tipo,
                            cliente.celular,
                            venta.codigo,
                            detalle.producto.nombre,
                            detalle.cantidad,
                            detalle.producto.precio,      # 🔹 Precio unitario
                            detalle.subtotal,             # Valor Cantidad
                            venta.total,                   # Total de la venta
                            venta.abono,                   # Abono
                            venta.restante                 # Restante
                        ])
                else:
                    # Venta sin detalles
                    ws.append([
                        cliente.nombre,
                        cliente.tipo,
                        cliente.celular,
                        venta.codigo,
                        "-", "-", "-", "-",               # Producto, Cantidad, Precio Unitario, Valor Cantidad
                        venta.total,
                        venta.abono,
                        venta.restante
                    ])
        else:
            # Cliente sin ventas
            ws.append([
                cliente.nombre,
                cliente.tipo,
                cliente.celular,
                "-", "-", "-", "-", "-", "-", "-", "-"
            ])

    # Crear respuesta
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response['Content-Disposition'] = 'attachment; filename=clientes.xlsx'
    wb.save(response)
    return response

@admin_required
def crear_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cliente_list')
    else:
        form = ClienteForm()

    return render(request, "clientes/crear_cliente.html", {"form": form})

@admin_required
def cliente_list(request):
    # Anotar la última venta de cada cliente
    clientes = Cliente.objects.annotate(
        ultima_venta=Max('ventas__fecha')
    )

    # Como total_deuda es una propiedad (no campo), calculamos manualmente:
    total_deuda = sum(cliente.total_deuda for cliente in clientes)

    # Total pagado (sumando todos los abonos registrados en ventas)
    total_pagado = Venta.objects.aggregate(total=Sum('abono'))['total'] or 0

    return render(request, "clientes/cliente_list.html", {
        "clientes": clientes,
        "total_deuda": total_deuda,
        "total_pagado": total_pagado,
    })

@admin_required
def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    # Ordenar las ventas de más reciente a más antigua
    ventas_ordenadas = cliente.ventas.all().order_by('-fecha')
    return render(request, 'tu_template.html', {
        'cliente': cliente,
        'ventas_ordenadas': ventas_ordenadas

    })


@admin_required
def actualizar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    abono_nuevo = request.POST.get('abono', '0')

    try:
        abono_nuevo = Decimal(abono_nuevo)
        if abono_nuevo < 0:
            raise InvalidOperation("El abono no puede ser negativo")
    except (InvalidOperation, ValueError):
        messages.error(request, "El valor del abono no es válido.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if abono_nuevo > venta.total:
        abono_nuevo = venta.total
        messages.warning(request, f"El abono se ajustó al total de la venta (${venta.total}).")

    venta.abono = abono_nuevo
    venta.restante = venta.total - abono_nuevo
    venta.pago_completo = abono_nuevo >= venta.total
    venta.save()

    messages.success(request, "El abono se actualizó correctamente.")

    # 🔹 Redirigir con parámetro para reabrir la modal
    return redirect(f"{request.META.get('HTTP_REFERER','/')}?modal={venta.cliente.id}")


from django.http import JsonResponse

def buscar_cliente(request):
    query = request.GET.get("q", "")
    resultados = []
    if query:
        clientes = Cliente.objects.filter(nombre__icontains=query)[:10]
        for c in clientes:
            resultados.append({"id": c.id, "nombre": c.nombre})
    return JsonResponse(resultados, safe=False)

def buscar_producto(request):
    q = request.GET.get("q", "")
    productos = Producto.objects.filter(nombre__icontains=q)[:10] if q else []
    data = [{"id": p.id, "nombre": p.nombre, "precio": float(p.precio)} for p in productos]
    return JsonResponse(data, safe=False)

def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'El cliente fue actualizado correctamente.')
            return redirect('cliente_list')  # Ajusta el nombre de tu URL de listado
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/editar_cliente.html', {'form': form, 'cliente': cliente})

def imprimir_factura(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request, 'factura.html', {'venta': venta})