from django.contrib import admin
from .models import Categoria, Ingrediente, Receita, Avaliacao

admin.site.register(Categoria)
admin.site.register(Ingrediente)
admin.site.register(Receita)
admin.site.register(Avaliacao)

