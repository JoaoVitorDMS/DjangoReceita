from django_filters import FilterSet, CharFilter, NumberFilter, DateTimeFilter
from .models import Receita, Ingrediente
from django import forms

class ReceitaFilter(FilterSet):
    titulo = CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'form-control'}))
    categoria = CharFilter(field_name='categoria__nome', lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'form-control'}))
    tempo_preparo = NumberFilter(lookup_expr='lte', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    porcoes = NumberFilter(lookup_expr='exact', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    data_publicacao = DateTimeFilter(lookup_expr='gte', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Receita
        fields = ['titulo', 'categoria', 'tempo_preparo', 'porcoes', 'data_publicacao']

class IngredienteFilter(FilterSet):
    nome = CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Ingrediente
        fields = ['nome']
