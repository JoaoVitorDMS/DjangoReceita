from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Ingrediente(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class IngredienteReceita(models.Model):
    UNIDADES = [
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('xic', 'Xícara'),
        ('colher_sopa', 'Colher de Sopa'),
        ('colher_cha', 'Colher de Chá'),
        ('unidade', 'Unidade'),
        ('a_gosto', 'A gosto'),
    ]
    
    receita = models.ForeignKey('Receita', on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    unidade = models.CharField(max_length=20, choices=UNIDADES)

    def __str__(self):
        return f"{self.quantidade} {self.get_unidade_display()} de {self.ingrediente.nome}"

class ReceitaImagem(models.Model):
    receita = models.ForeignKey('Receita', related_name='imagens', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='receitas/')
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']

class Receita(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredientes = models.ManyToManyField(Ingrediente, through=IngredienteReceita)
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
    data_edicao = models.DateTimeField(auto_now=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"