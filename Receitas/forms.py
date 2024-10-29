from django import forms
from .models import Receita, Ingrediente, Avaliacao

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['titulo', 'descricao', 'categoria', 'ingredientes', 'modo_preparo', 'tempo_preparo', 'porcoes', 'imagens']

class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ['nome', 'unidade']

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']
