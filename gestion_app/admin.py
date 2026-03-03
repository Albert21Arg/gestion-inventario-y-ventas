from django.contrib import admin
from .models import *

# Registrar modelos en el admin
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "documento", "correo", "celular", "tipo", "fechaRegistro")
    search_fields = ("nombre", "documento", "correo", "celular")
    list_filter = ("tipo", "fechaRegistro")

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "stock")
    search_fields = ("nombre",)
    list_filter = ("precio",)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "cliente", "fecha", "total")
    search_fields = ("codigo", "cliente__nombre")
    list_filter = ("fecha",)

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "cantidad", "precio_unitario", "subtotal")
    search_fields = ("producto__nombre", "venta__codigo")
