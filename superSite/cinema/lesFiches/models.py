from django.db import models

# Create your models here.

class MovieCard (models.Model):
    titre = models.CharField( max_length =250)
    date_sortie = models.DateField()
    realisateur = models.CharField( max_length =250)
    act_prin = models.CharField( max_length =250)
    avis = models.TextField()
    pub = models.BooleanField(default = False)
    note = models.IntegerField(default = 0)
    
    def __str__(self):
        return self.titre