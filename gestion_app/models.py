from django.db import models
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils.timezone import now
import uuid
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Max
from decimal import Decimal
from django.db.models import Sum

# Validadores de celular (con prefijo, mínimo 10 y máximo 15 dígitos)
celular_validator = RegexValidator(
    regex=r'^\+\d{10,15}$',
    message='Ingrese un número de celular válido con prefijo (+57..., mínimo 10 y máximo 15 dígitos).'
)
# Validadores de teléfono fijo (7 a 10 dígitos, sin prefijo)
fijo_validator = RegexValidator(
    regex=r'^\d{7,10}$',
    message='Ingrese un número de teléfono fijo válido (7 a 10 dígitos, sin prefijo).'
)

#Cliente
class Cliente(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('regular', 'Regular'),
        ('frecuente', 'Frecuente'),
        ('vip', 'VIP´S'),
    ]

    nombre = models.CharField("Nombre", max_length=100)
    documento = models.CharField("Documento", max_length=20, unique=True, null=True, blank=True)
    correo = models.EmailField("Correo", unique=True, null=True, blank=True)

    telefono_fijo = models.CharField(
        "Teléfono fijo",
        max_length=10,
        null=True,
        blank=True,
        validators=[fijo_validator]
    )
    celular = models.CharField(
        "Celular",
        max_length=15,
        unique=True,
        validators=[celular_validator]
    )

    direccion = models.TextField("Dirección", null=True, blank=True)
    tipo = models.CharField("Tipo de cliente", max_length=10, choices=TIPO_CLIENTE_CHOICES, default='regular')
    notas = models.TextField("Notas internas", null=True, blank=True)
    fechaRegistro = models.DateTimeField("Fecha de registro", auto_now_add=True)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ['-fechaRegistro']

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    def actualizar_tipo(self):
        cantidad_ventas = self.ventas.count()  # asumiendo que 'ventas' es el related_name de Venta
        if cantidad_ventas > 15:
            self.tipo = 'vip'
        elif cantidad_ventas > 6:
            self.tipo = 'frecuente'
        else:
            self.tipo = 'regular'
        self.save()

    def actualizar_tipo(self):
        cantidad_ventas = self.ventas.count()  # asumiendo que 'ventas' es el related_name de Venta
        if cantidad_ventas > 15:
            self.tipo = 'vip'
        elif cantidad_ventas > 6:
            self.tipo = 'frecuente'
        else:
            self.tipo = 'regular'
        self.save()

    @property
    def total_deuda(self):
        """
        Devuelve la suma de los valores 'restante' de todas las ventas del cliente.
        Si no tiene ventas o todas están pagadas, devuelve 0.
        """
        return self.ventas.aggregate(
            total=Sum('restante')
        )['total'] or 0

    @property
    def primer_nombre(self):
        return self.nombre.split()[0] if self.nombre else ""

# Producto
from django.urls import reverse

class Producto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(
        upload_to='productos/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

    class Meta:
        ordering = ["nombre"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def get_absolute_url(self):
        return reverse('detalle_producto', args=[str(self.id)])

# Venta (historial de compras)
class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="ventas")
    codigo = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    abono = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    restante = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    pago_completo = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Buscar el último consecutivo
            ultimo = Venta.objects.aggregate(ultimo=Max("id"))["ultimo"] or 0
            nuevo_numero = ultimo + 1
            self.codigo = f"VEN-{nuevo_numero:06d}"

        # Inicializar restante y pago_completo si es una venta nueva
        if not self.pk:  # si es nueva venta
            self.restante = self.total
            self.abono = Decimal('0.00')
            self.pago_completo = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.cliente.nombre}"



# Detalle de Venta (productos de cada compra)
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey("Producto", on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs):
        if not self.pk:  # Solo al crear
            # Si no se ha establecido un precio personalizado, usar el del producto
            if not self.precio_unitario:
                self.precio_unitario = self.producto.precio

            # Descontar stock solo si hay suficiente
            if self.producto.stock >= self.cantidad:
                self.producto.stock -= self.cantidad
                self.producto.save()

        # Calcular subtotal siempre
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

        # Recalcular total de la venta
        self.venta.total = sum(d.subtotal for d in self.venta.detalles.all())
        self.venta.save()

    @transaction.atomic
    def eliminar_con_confirmacion(self, password, user):
        """
        Elimina el detalle de venta solo si la contraseña del usuario es correcta.
        """
        if not authenticate(username=user.username, password=password):
            raise PermissionDenied("Contraseña incorrecta. No se puede eliminar el detalle de venta.")

        # Devolver el stock
        self.producto.stock += self.cantidad
        self.producto.save()

        # Guardamos y eliminamos
        venta = self.venta
        super().delete()

        # Recalcular el total de la venta
        venta.total = sum(d.subtotal for d in venta.detalles.all())
        venta.save()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} ({self.venta.codigo})"