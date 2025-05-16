from django.shortcuts import render
from django.http import HttpResponse
from django.template import Template, Context
from .models import MovieCard

from django.forms import ModelForm
from django.contrib import messages


# Create your views here.

def home(request, film='Un singe en hiver'):
    return HttpResponse (f'Mon film préféré est : {film}')

def listeMovies(request):
    films = MovieCard.objects.all().order_by('date_sortie')
    page = """
    {% for film in films %}
    <h3>Titre : {{ film.titre }}</h3>
    Date de sortie : {{ film.date_sortie }} <br>
    Réalisateur : {{ film.realisateur }} <br>
    <br>
    {% endfor %}
    """
    template = Template(page)
    context = Context({'films':films})
    return HttpResponse(template.render(context))

def listeMoviesTemplate(request ):
    films = MovieCard.objects.all().order_by('date_sortie')
    return render(request , template_name = 'list.html', context = {'films':films})

def listeMoviesTemplate2 (request ):
    films = MovieCard.objects.all().order_by('date_sortie')
    return render(request , template_name = 'index.html', context = {'films':films})

class MovieCardForm(ModelForm):
    class Meta:
        model = MovieCard
        fields = ('titre','avis','date_sortie','realisateur','act_prin','note')
        
def formu(request):
    avis_form = MovieCardForm ()
    if request.method == "POST":
        form = MovieCardForm(request.POST)
        if form.is_valid():
            new_movie = form.save()
            messages.success(request, 'Nouveau Film' + new_movie .titre)
            context = {'film': new_movie }
            return render(request ,'details.html', context)
    return render(request , 'formulaire.html', {'avis_form' : avis_form })