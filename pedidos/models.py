#Limonatur/pedidos/models.py
from django.db import models
from django.contrib.auth import get_user_model
from tienda.models import Producto
from django.db.models import F, Sum, FloatField
from django.utils import timezone
from decimal import Decimal
from django.db.models.signals import pre_save
from django.dispatch import receiver

User = get_user_model()

class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    finalizado = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        # Asegurarse de que el id no sea None antes de guardar
        if self.id is None:
            # No se permite el guardado si no se asigna un id
            raise ValueError("El ID del pedido no puede ser None antes de guardar.")
        super().save(*args, **kwargs)




    def __str__(self):
        return f'Pedido {self.id} - {self.usuario}'

    class Meta:
        db_table = 'tPedidos'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['id']

    @property
    def recalcular_total(self):
        total = self.detalles.aggregate(
            total=Sum(F('precio') * F('cantidad'), output_field=FloatField())
        )['total'] or 0.0
        self.total = total
        self.save()
        return total

@receiver(pre_save, sender=Pedido)
def asegurar_id_no_none(sender, instance, **kwargs):
    if instance.id is None:
        raise ValueError("El ID del pedido no puede ser None antes de guardar.")

class DetallePedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    finalizado = models.BooleanField(default=False)  # Campo para indicar si el pedido está finalizado
    comision = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    total_fabricante = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(default=timezone.now)

    def calcular_comision(self):
        return self.precio * self.cantidad * Decimal('0.30')

    def save(self, *args, **kwargs):
        total_pedido = self.precio * self.cantidad
        self.comision = total_pedido * Decimal('0.30')
        self.total_fabricante = total_pedido * Decimal('0.70')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.cantidad} unidades de {self.producto.nombre}'

    class Meta:
        db_table = 'tDetallePedidos'
        verbose_name = 'DetallePedido'
        verbose_name_plural = 'DetallePedidos'
        ordering = ['id']