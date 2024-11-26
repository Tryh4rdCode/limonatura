from django.db import models
from django.contrib.auth import get_user_model
from tienda.models import Producto
from django.db.models import F, Sum, FloatField
from django.utils import timezone
from decimal import Decimal

# pedidos/models.py

# Obtener el modelo de usuario
Usuario = get_user_model()

# Modelo Pedido
class Pedido(models.Model):
    # Relación con el usuario
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    finalizado = models.BooleanField(default=False)  # Campo para indicar si el pedido está finalizado
    created_at = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Campo total agregado

    # Representación en cadena del pedido
    def __str__(self):
        return f'Pedido {self.id} - {self.usuario}' # pylint: disable=no-member
    
    class Meta:
        db_table = 'tPedidos'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['id']

    # Propiedad para calcular el total del pedido
    @property
    def total(self):
        return self.detalles.aggregate(  # pylint: disable=no-member
            total=Sum(F('producto__precio') * F('cantidad'), output_field=FloatField())
        )['total'] or 0.0

# Modelo DetallePedido
class DetallePedido(models.Model):
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    producto = models.ForeignKey('tienda.Producto', on_delete=models.CASCADE)  # Cambiar producto_id a producto
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')  # Cambiar pedido_id a pedido
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    comision = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    total_fabricante = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(default=timezone.now)

    

    def calcular_comision(self):
        return self.precio * self.cantidad * Decimal('0.30')
    
     # Método para guardar el detalle del pedido
    def save(self, *args, **kwargs):
        total_pedido = self.precio * self.cantidad
        self.comision = total_pedido * Decimal('0.30')
        self.total_fabricante = total_pedido * Decimal('0.70')
        super().save(*args, **kwargs)


    # Representación en cadena del detalle del pedido
    def __str__(self):
        return f'{self.cantidad} unidades de {self.producto.nombre}'  # pylint: disable=no-member
    
    class Meta:
        db_table = 'tDetallePedidos'
        verbose_name = 'DetallePedido'
        verbose_name_plural = 'DetallePedidos'
        ordering = ['id']
