from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Ingrediente(models.Model):
    UNIDADES = [
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('colher_sopa', '1 colher de sopa'),
        ('1/2', '1/2'),
        ('porcao', 'Porção'),
    ]
    
    nome = models.CharField(max_length=100)
    unidade = models.CharField(max_length=20, choices=UNIDADES, null=True)

    def __str__(self):
        return f"{self.nome} ({self.unidade})"

class Receita(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredientes = models.ManyToManyField(Ingrediente)
    quantidade = models.CharField(max_length=200)
    imagem = models.ImageField(upload_to='receitas/', blank=True, null=True)
    modo_preparo = models.TextField()
    tempo_preparo = models.IntegerField()
    porcoes = models.IntegerField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    data_edicao = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.titulo

class Avaliacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE)
    nota = models.IntegerField()
    comentario = models.TextField()
    data_avaliacao = models.DateTimeField(auto_now_add=True)
    data_edicao = models.DateTimeField(auto_now=True)  # Add this line

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"