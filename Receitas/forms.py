from django import forms
from .models import Receita, Ingrediente, Avaliacao
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['titulo', 'descricao', 'categoria', 'ingredientes', 'modo_preparo', 'tempo_preparo', 'porcoes', 'imagem']

class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ['nome', 'unidade']

class AvaliacaoForm(forms.ModelForm):
    nota = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.RadioSelect(choices=[
            (1, '★ - Péssimo'), (2, '★★ - Ruim'), (3, '★★★ - Ok'), (4, '★★★★ - Bom'), (5, '★★★★★ - Muito bom')
        ], attrs={'class': 'star-rating'})
    )

    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]  # Set username same as email
        if commit:
            user.save()
        return user
