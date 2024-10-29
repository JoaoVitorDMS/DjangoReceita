from django.urls import path
from django.contrib.auth import views as auth_views
from .views import IndexView, SobreView, ReceitaCreateView, ReceitaUpdateView, ReceitaListView, ReceitaDetailView, ReceitaDeleteView, CustomLoginView, responder_comentario, RegistroView
from .views import CategoriaDeleteView, CategoriaCreateView, CategoriaDetailView, CategoriaListView, CategoriaUpdateView, IngredienteListView, IngredienteDetailView, IngredienteCreateView, IngredienteUpdateView, IngredienteDeleteView

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('sobre/', SobreView.as_view(), name="sobre"),
    path('receita/', ReceitaListView.as_view(), name="receita-list"),
    path('receita/<int:pk>', ReceitaDetailView.as_view(), name="receita-detail"),
    path('receita/novo/', ReceitaCreateView.as_view(), name="receita-create"),
    path('receita/editar/<int:pk>', ReceitaUpdateView.as_view(), name="receita-update"),
    path('receita/deletar/<int:pk>', ReceitaDeleteView.as_view(), name="receita-delete"),
    path('responder-comentario/<int:pk>/', responder_comentario, name='responder-comentario'),

    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout', kwargs={'next_page': 'login'}),

    path('categoria/', CategoriaListView.as_view(), name="categoria-list"),
    path('categoria/<int:pk>', CategoriaDetailView.as_view(), name="categoria-detail"),
    path('categoria/novo/', CategoriaCreateView.as_view(), name="categoria-create"),
    path('categoria/editar/<int:pk>', CategoriaUpdateView.as_view(), name="categoria-update"),
    path('categoria/deletar/<int:pk>', CategoriaDeleteView.as_view(), name="categoria-delete"),

    path('ingrediente/', IngredienteListView.as_view(), name="ingrediente-list"),
    path('ingrediente/<int:pk>', IngredienteDetailView.as_view(), name="ingrediente-detail"),
    path('ingrediente/novo/', IngredienteCreateView.as_view(), name="ingrediente-create"),
    path('ingrediente/editar/<int:pk>', IngredienteUpdateView.as_view(), name="ingrediente-update"),
    path('ingrediente/deletar/<int:pk>', IngredienteDeleteView.as_view(), name="ingrediente-delete"),
]
