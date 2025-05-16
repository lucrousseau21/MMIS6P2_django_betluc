from setuptools import setup, find_packages, Command
import os
import subprocess
import sys

class InstallCommand(Command):
    description = 'Installe le projet et initialise les données'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Exécute le script de gestion pour initialiser les données."""
        try:
            # Vérifier que nous sommes dans le bon répertoire
            if not os.path.exists('manage.py'):
                print("Erreur : Le fichier manage.py n'est pas trouvé. Veuillez exécuter ce script depuis le répertoire racine du projet.")
                sys.exit(1)

            # Exécuter les migrations
            subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
            
            # Exécuter le script de gestion
            subprocess.run([sys.executable, 'manage.py', 'setup_league_data'], check=True)
            
            print("Installation terminée avec succès !")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'installation : {e}")
            sys.exit(1)

setup(
    name="betluc",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'Django>=4.2.0',
        'django-crispy-forms>=2.0',
        'crispy-bootstrap5>=0.7',
    ],
    cmdclass={
        'install': InstallCommand,
    },
    author="Votre Nom",
    author_email="votre.email@example.com",
    description="Application de paris sportifs",
    long_description=open('README.md').read() if os.path.exists('README.md') else "",
    long_description_content_type="text/markdown",
    url="https://github.com/votre-repo/betluc",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
) 