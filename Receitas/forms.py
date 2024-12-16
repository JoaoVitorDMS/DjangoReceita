from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Receita, Ingrediente, Avaliacao, IngredienteReceita

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ReceitaForm(forms.ModelForm):
    imagens = MultipleFileField(
        required=False,
        help_text='Você pode selecionar até 5 imagens'
    )

    class Meta:
        model = Receita
        fields = ['titulo', 'descricao', 'categoria', 'modo_preparo', 
                 'tempo_preparo', 'porcoes']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'modo_preparo': forms.Textarea(attrs={'rows': 5}),
        }

class IngredienteReceitaForm(forms.ModelForm):
    class Meta:
        model = IngredienteReceita
        fields = ['ingrediente', 'quantidade', 'unidade']

class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ['nome']

class AvaliacaoForm(forms.ModelForm):
    nota = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.RadioSelect(choices=[
            (1, '★ - Péssimo'), 
            (2, '★★ - Ruim'), 
            (3, '★★★ - Ok'), 
            (4, '★★★★ - Bom'), 
            (5, '★★★★★ - Muito bom')
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
        fields = ("username", "email", "password1", "password2")  # Adicionado username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email ou Username')
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if user is None:
                try:
                    user_with_email = User.objects.get(email=username)
                    user = authenticate(username=user_with_email.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is None:
                raise forms.ValidationError(
                    "Email/Username ou senha inválidos.",
                    code='invalid_login'
                )
            else:
                if not user.is_active:
                    raise forms.ValidationError(
                        "Esta conta está inativa.",
                        code='inactive',
                    )
                
            self.user_cache = user
        return self.cleaned_data
