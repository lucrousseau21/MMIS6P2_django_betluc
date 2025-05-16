from django.shortcuts import render

def rules_view(request):
    """Vue pour afficher la page des règles de paris"""
    return render(request, 'pages/rules.html') 