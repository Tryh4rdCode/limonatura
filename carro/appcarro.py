# carro/appcarro.py

from decimal import Decimal
from tienda.models import Producto

class Carro:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carro = self.session.get('carro')
        if not carro:
            carro = self.session['carro'] = {}
        self.carro = carro

    def agregar(self, producto):
        producto_id = str(producto.id)
        if producto_id not in self.carro:
            self.carro[producto_id] = {
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'preciounitario': str(producto.precio),
                'cantidad': 1,
                'imagen': producto.imagen.url if producto.imagen else None
            }
            producto.stock -= 1
            producto.save()
        else:
            for key, value in self.carro.items():
                if key == producto_id:
                    value['cantidad'] += 1
                    value['precio'] = str(Decimal(value['precio']) + producto.precio)
                    producto.stock -= 1
                    producto.save()
                    break
        self.guardar_carro()

    def guardar_carro(self):
        self.session['carro'] = self.carro
        self.session.modified = True

    def eliminar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carro:
            cantidad = self.carro[producto_id]['cantidad']
            del self.carro[producto_id]
            producto.stock += cantidad
            producto.save()
            self.guardar_carro()

    def restar_producto(self, producto):
        for key, value in self.carro.items():
            if key == str(producto.id):
                value['cantidad'] -= 1
                value['precio'] = str(Decimal(value['precio']) - producto.precio)
                producto.stock += 1
                producto.save()
                if value['cantidad'] < 1:
                    self.eliminar(producto)
                break
        self.guardar_carro()

    def limpiar_carro(self):
        self.session['carro'] = {}
        self.session.modified = True

    def contar_productos(self):
        return sum(item['cantidad'] for item in self.carro.values())