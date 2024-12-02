from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from .models import Categoria, Receita, Ingrediente, Avaliacao, Profile
from .forms import ReceitaForm, IngredienteForm, AvaliacaoForm, CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.db.models import Avg

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

class IndexView(TemplateView):
    template_name = 'padrao/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['receitas'] = Receita.objects.all().order_by('-data_publicacao')[:6]  # Get latest 6 recipes
        return context

class SobreView(TemplateView):
    template_name = 'padrao/sobre.html'

class ReceitaListView(ListView):
    model = Receita
    template_name = 'receitas/receita_list.html'
    context_object_name = 'receitas'

class ReceitaDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Receita
    template_name = 'receitas/receita_detail.html'
    context_object_name = 'receita'
    form_class = AvaliacaoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avaliacoes'] = Avaliacao.objects.filter(receita=self.object)
        context['form'] = self.get_form()
        context['is_author'] = self.object.autor == self.request.user
        context['media_avaliacoes'] = Avaliacao.objects.filter(receita=self.object).aggregate(Avg('nota'))['nota__avg']
        return context

    def post(self, request, *args, **kwargs):
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
        form.instance.autor = self.request.user
        receita = form.save()
        
        nome_ingredientes = self.request.POST.getlist('ingrediente_nome')
        unidades = self.request.POST.getlist('ingrediente_unidade')
        quantidades = self.request.POST.getlist('ingrediente_quantidade')

        for nome, unidade, quantidade in zip(nome_ingredientes, unidades, quantidades):
            if nome:
                ingrediente, created = Ingrediente.objects.get_or_create(nome=nome, unidade=unidade)
                receita.ingredientes.add(ingrediente)

        return redirect(self.success_url)
    
class ReceitaUpdateView(LoginRequiredMixin, UpdateView):
    model = Receita
    template_name = 'receitas/receita_form.html'
    form_class = ReceitaForm
    success_url = reverse_lazy('receita-list')

class ReceitaDeleteView(LoginRequiredMixin, DeleteView):
    model = Receita
    template_name = 'receitas/receita_confirm_delete.html'
    success_url = reverse_lazy('receita-list')



# def buscar_ingredientes(request):
#     if 'q' in request.GET:
#         query = request.GET['q']
#         ingredientes = Ingrediente.objects.filter(nome__icontains(query)[:10]
#         resultados = [{'id': i.id, 'nome': i.nome} for i in ingredientes]
#         return JsonResponse(resultados, safe=False)
#     return JsonResponse([], safe=False)

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
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()

class IngredienteDeleteView(UserPassesTestMixin, DeleteView):
    model = Ingrediente
    template_name = 'ingredientes/ingrediente_confirm_delete.html'
    success_url = reverse_lazy('ingrediente-list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administradores').exists()
