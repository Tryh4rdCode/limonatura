#Aqui realizamos la importación de las librerías necesarias
from django.contrib import admin
from .models import Producto, Categoria_Coleg, Categoria_Produ, Categoria_Sexo

class ProductoAdmin(admin.ModelAdmin):
    readonly_fields = ( 'creado', 'actualizado')
    list_display = ('nombre', 'precio', 'stock', 'disponibilidad', 'fabricante')
    search_fields = ('nombre', 'fabricante__nombre')
    list_filter = ('disponibilidad', 'categorias_prod', 'categorias_cole', 'categorias_sexo')
    ordering = ('nombre',)

class Categoria_ColegAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')

class Categoria_ProduAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')

class Categoria_SexoAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')


admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria_Coleg, Categoria_ColegAdmin)
admin.site.register(Categoria_Produ, Categoria_ProduAdmin)
admin.site.register(Categoria_Sexo, Categoria_SexoAdmin)