from django.contrib import admin
from .models import Producto, Categoria_Tipo, Categoria_Temporada, Categoria_Material

class ProductoAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'precio', 'stock', 'disponibilidad', 'fabricante')
    search_fields = ('nombre', 'fabricante__nombre')
    list_filter = ('disponibilidad', 'categorias_temporada', 'categorias_tipo', 'categorias_material')
    ordering = ('nombre',)

class Categoria_TipoAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')

class Categoria_TemporadaAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')

class Categoria_MaterialAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria_Tipo, Categoria_TipoAdmin)
admin.site.register(Categoria_Temporada, Categoria_TemporadaAdmin)
admin.site.register(Categoria_Material, Categoria_MaterialAdmin)