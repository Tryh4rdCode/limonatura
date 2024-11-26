from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver

User = get_user_model()

class Fabricante(models.Model):
    nombre = models.CharField(max_length=100)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

class Categoria_Producto(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'categoria_prod'
        verbose_name_plural = 'categorias_prod'

    def __str__(self):
        return self.nombre

class Categoria_Tipo(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'categoria_tipo'
        verbose_name_plural = 'categorias_tipo'

    def __str__(self):
        return self.nombre

class Categoria_Material(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'categoria_material'
        verbose_name_plural = 'categorias_material'

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categorias_prod = models.ForeignKey(Categoria_Producto, on_delete=models.CASCADE, default=1)
    categorias_tipo = models.ForeignKey(Categoria_Tipo, on_delete=models.CASCADE, default=1)
    categorias_material = models.ForeignKey(Categoria_Material, on_delete=models.CASCADE, default=1)
    imagen = models.ImageField(upload_to='productos', null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    disponibilidad = models.BooleanField(default=True)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.CASCADE, related_name='productos')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    sku = models.CharField(max_length=50, unique=True, blank=True)

    class Meta:
        db_table = 'tProductos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.precio < 0:
            raise ValidationError('El precio no puede ser negativo.')

@receiver(pre_save, sender=Producto)
def set_sku(sender, instance, **kwargs):
    if not instance.sku:
        instance.sku = f"{instance.categorias_prod.codigo}-{instance.categorias_material.codigo}-{instance.categorias_tipo.codigo}-{instance.id or ''}"