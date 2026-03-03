from django.urls import path
from django.contrib.auth.decorators import user_passes_test
from . import views
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

# Decorador para permitir solo superusuarios
admin_only = user_passes_test(lambda u: u.is_superuser, login_url='/')

urlpatterns = [
    # Rutas públicas
    path("", views.listado_productos, name="listado_productos"),

    # Rutas solo para admin
    path('crear/', admin_only(views.crear_producto), name='crear_producto'),
    path('editar/<int:pk>/', admin_only(views.editar_producto), name='editar_producto'),
    path('eliminar/<int:pk>/', admin_only(views.eliminar_producto), name='eliminar_producto'),
    path("cliente_list/", admin_only(views.cliente_list), name="cliente_list"),
    path("clientes/nuevo/", admin_only(views.crear_cliente), name="crear_cliente"),
    path("<int:pk>/", admin_only(views.cliente_detail), name="cliente_detail"),
    path("ventas/nueva/", admin_only(views.crear_venta), name="crear_venta"),
    path("ventas/<int:pk>/", admin_only(views.detalle_venta), name="detalle_venta"),
    path('venta/<int:venta_id>/actualizar/', admin_only(views.actualizar_venta), name='actualizar_venta'),
    path('ventas/<int:venta_id>/factura/', admin_only(views.descargar_factura), name='descargar_factura'),
    path('clientes/exportar/', admin_only(views.exportar_clientes_excel), name='exportar_clientes_excel'),
    path("clientes/buscar/", views.buscar_cliente, name="buscar_cliente"),
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
    path('productos/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('ventas/factura/<int:venta_id>/', views.imprimir_factura, name='imprimir_factura'),



]
