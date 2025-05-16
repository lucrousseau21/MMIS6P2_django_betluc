from django.contrib import admin
from lesFiches.models import MovieCard
from django.utils.html import format_html

# Register your models here.

# admin.site.register( MovieCard )
@admin.register( MovieCard )
class MovieCardAdmin (admin. ModelAdmin ):
    list_display =('titre','date_sortie','realisateur', 'view_note')

    @admin.display( empty_value ="pas de note")
    def view_note (self, obj ):
        if obj.note >10:
            color = 'green'
        else:
            color = 'red'
        return format_html ("<span style=color:{} >{} </span >".format(color, obj.note ))
