from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from .models import Categoria, IngredienteReceita, Receita, Ingrediente, Avaliacao, Profile, ReceitaImagem
from .forms import ReceitaForm, IngredienteForm, AvaliacaoForm, CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.db.models import Avg
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .filters import ReceitaFilter, IngredienteFilter
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

class RegistroView(generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = 'autenticacao/registro.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        logado_group, created = Group.objects.get_or_create(name='Logado')
        self.object.groups.add(logado_group)
        
        # Create profile with avatar
        Profile.objects.create(
            user=self.object,
            avatar=form.cleaned_data.get('avatar')
        )
        
        return response
    
class CustomLoginView(auth_views.LoginView):
    template_name = 'autenticacao/login.html'
    form_class = CustomAuthenticationForm
    
    def get_success_url(self):
        return reverse_lazy('index')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

class IndexView(TemplateView):
    template_name = 'padrao/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['receitas'] = (Receita.objects.select_related('autor', 'categoria')
                             .prefetch_related('ingredientes')
                             .order_by('-data_publicacao')[:6])
        return context

class SobreView(TemplateView):
    template_name = 'padrao/sobre.html'

class ReceitaListView(LoginRequiredMixin, ListView):
    model = Receita
    template_name = 'receitas/receita_list.html'
    context_object_name = 'receitas'

    def get_queryset(self):
        queryset = (Receita.objects.select_related('autor', 'categoria')
                   .prefetch_related('ingredientes')
                   .order_by('-data_publicacao'))
        self.filterset = ReceitaFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class ReceitaDetailView(FormMixin, DetailView):  # Removed LoginRequiredMixin
    model = Receita
    template_name = 'receitas/receita_detail.html'
    context_object_name = 'receita'
    form_class = AvaliacaoForm

    def get_queryset(self):
        return (Receita.objects.select_related('autor', 'categoria')
                .prefetch_related(
                    'ingredientereceita_set',
                    'ingredientereceita_set__ingrediente'
                ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredientes'] = (self.object.ingredientereceita_set
                                 .select_related('ingrediente')
                                 .all())
        avaliacoes = (Avaliacao.objects.select_related('usuario')
                     .filter(receita=self.object))
        context['avaliacoes'] = avaliacoes
        context['form'] = self.get_form() if self.request.user.is_authenticated else None
        context['is_author'] = self.request.user.is_authenticated and self.object.autor == self.request.user
        context['media_avaliacoes'] = avaliacoes.aggregate(Avg('nota'))['nota__avg']
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        avaliacao = form.save(commit=False)
        avaliacao.usuario = self.request.user
        avaliacao.receita = self.object
        avaliacao.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('receita-detail', kwargs={'pk': self.object.pk})

def responder_comentario(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    if request.method == 'POST' and request.user == avaliacao.receita.autor:
        resposta = request.POST.get('resposta')
        if resposta:
            avaliacao.resposta = resposta
            avaliacao.save()
    return redirect('receita-detail', pk=avaliacao.receita.pk)

def editar_avaliacao(request, pk):
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    
    if request.user != avaliacao.usuario:
        return redirect('receita-detail', pk=avaliacao.receita.pk)
    
    if request.method == 'POST':
        avaliacao.nota = request.POST.get('nota')
        avaliacao.comentario = request.POST.get('comentario')
        avaliacao.save()
        
    return redirect('receita-detail', pk=avaliacao.receita.pk)

class ReceitaCreateView(LoginRequiredMixin, CreateView):
    model = Receita
    template_name = 'receitas/receita_form.html'
    form_class = ReceitaForm
    success_url = reverse_lazy('receita-list')

    def form_valid(self, form):
        # Salva a receita primeiro
        form.instance.autor = self.request.user
        self.object = form.save()
        
        # Handle image uploads
        images = self.request.FILES.getlist('imagens')
        for i, img in enumerate(images[:5]):  # Limit to 5 images
            ReceitaImagem.objects.create(
                receita=self.object,
                imagem=img,
                ordem=i
            )

        # Processa os ingredientes do formulário
        post_data = self.request.POST
        indices = []
        
        # Encontra todos os índices de ingredientes no formulário
        for key in post_data:
            if key.startswith('ingrediente_nome_'):
                index = key.split('_')[-1]
                indices.append(index)
        
        # Para cada conjunto de ingrediente
        for idx in indices:
            nome = post_data.get(f'ingrediente_nome_{idx}')
            quantidade = post_data.get(f'ingrediente_quantidade_{idx}')
            unidade = post_data.get(f'ingrediente_unidade_{idx}')
            
            if nome and quantidade:
                try:
                    # Limpa o nome do ingrediente
                    nome = nome.strip().lower()
                    quantidade = float(quantidade)
                    
                    # Cria ou obtém o ingrediente
                    ingrediente, _ = Ingrediente.objects.get_or_create(nome=nome)
                    
                    # Cria a relação ingrediente-receita
                    IngredienteReceita.objects.create(
                        receita=self.object,
                        ingrediente=ingrediente,
                        quantidade=quantidade,
                        unidade=unidade
                    )
                except ValueError:
                    continue  # Ignora se a quantidade não for um número válido

        return redirect(self.success_url)

class ReceitaUpdateView(LoginRequiredMixin, UpdateView):
    model = Receita
    template_name = 'receitas/receita_form.html'
    form_class = ReceitaForm
    success_url = reverse_lazy('receita-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona os ingredientes existentes ao contexto
        context['ingredientes_existentes'] = self.object.ingredientereceita_set.all()
        return context

    def form_valid(self, form):
        # Salva a receita primeiro
        self.object = form.save()
        
        # Handle image uploads
        images = self.request.FILES.getlist('imagens')
        current_images = self.object.imagens.count()
        
        # Only add new images if total won't exceed 5
        for i, img in enumerate(images[:5-current_images]):
            ReceitaImagem.objects.create(
                receita=self.object,
                imagem=img,
                ordem=current_images + i
            )

        # Remove ingredientes existentes
        self.object.ingredientereceita_set.all().delete()
        
        # Processa os novos ingredientes
        post_data = self.request.POST
        indices = []
        
        for key in post_data:
            if key.startswith('ingrediente_nome_'):
                index = key.split('_')[-1]
                indices.append(index)
        
        for idx in indices:
            nome = post_data.get(f'ingrediente_nome_{idx}')
            quantidade = post_data.get(f'ingrediente_quantidade_{idx}')
            unidade = post_data.get(f'ingrediente_unidade_{idx}')
            
            if nome and quantidade:
                try:
                    nome = nome.strip().lower()
                    quantidade = float(quantidade)
                    ingrediente, _ = Ingrediente.objects.get_or_create(nome=nome)
                    
                    IngredienteReceita.objects.create(
                        receita=self.object,
                        ingrediente=ingrediente,
                        quantidade=quantidade,
                        unidade=unidade
                    )
                except ValueError:
                    continue

        return redirect(self.success_url)

class ReceitaDeleteView(LoginRequiredMixin, DeleteView):
    model = Receita
    template_name = 'receitas/receita_confirm_delete.html'
    success_url = reverse_lazy('receita-list')


#-------------- # categoria # ------------#
class CategoriaListView(UserPassesTestMixin, ListView):
    model = Categoria
    template_name = 'categorias/categoria_list.html'
    context_object_name = 'categorias'
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()

class CategoriaDetailView(UserPassesTestMixin, DetailView):
    model = Categoria
    template_name = 'categorias/categoria_detail.html'
    context_object_name = 'categoria'
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()

class CategoriaCreateView(UserPassesTestMixin, CreateView):
    model = Categoria
    template_name = 'categorias/categoria_form.html'
    fields = ['nome']
    success_url = reverse_lazy('categoria-list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()

class CategoriaUpdateView(UserPassesTestMixin, UpdateView):
    model = Categoria
    template_name = 'categorias/categoria_form.html'
    fields = ['nome']
    success_url = reverse_lazy('categoria-list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()

class CategoriaDeleteView(UserPassesTestMixin, DeleteView):
    model = Categoria
    template_name = 'categorias/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria-list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()


class IngredienteListView(ListView):
    model = Ingrediente
    template_name = 'ingredientes/ingrediente_list.html'
    context_object_name = 'ingredientes'

    def get_queryset(self):
        queryset = Ingrediente.objects.all()
        self.filterset = IngredienteFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class IngredienteDetailView(DetailView):
    model = Ingrediente
    template_name = 'ingredientes/ingrediente_detail.html'
    context_object_name = 'ingrediente'

class IngredienteCreateView(UserPassesTestMixin, CreateView):
    model = Ingrediente
    template_name = 'ingredientes/ingrediente_form.html'
    fields = ['nome']
    success_url = reverse_lazy('ingrediente-list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()

class IngredienteUpdateView(UserPassesTestMixin, UpdateView):
    model = Ingrediente
    template_name = 'ingredientes/ingrediente_form.html'
    fields = ['nome']
    success_url = reverse_lazy('ingrediente-list')
    
    def test_func(self):
        success_url = reverse_lazy('ingrediente-list')
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()

class IngredienteDeleteView(UserPassesTestMixin, DeleteView):
    model = Ingrediente
    template_name = 'ingredientes/ingrediente_confirm_delete.html'
    success_url = reverse_lazy('ingrediente-list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()

    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()

class IngredienteDeleteView(UserPassesTestMixin, DeleteView):
    model = Ingrediente
    template_name = 'ingredientes/ingrediente_confirm_delete.html'
    success_url = reverse_lazy('ingrediente-list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()

@login_required
def remover_imagem(request, pk):
    imagem = get_object_or_404(ReceitaImagem, pk=pk)
    receita = receita.imagem
        
    if request.user == receita.autor:
        imagem.delete()
    
    return redirect('receita-detail', pk=receita.pk)

