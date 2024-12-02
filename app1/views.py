from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
import statistics

# Vue pour la page d'accueil
def index(request):
    return render(request, 'app1/index.html')
# Vue pour effectuer les calculs statistiques
def calcules(request):
    mean = None
    median = None
    mode = None
    variance = None
    stdev = None
    if request.method == "POST":
        # Récupérer les valeurs saisies par l'utilisateur
        valeurs = request.POST.get('valeurs')
        if valeurs:
            try:
                # Convertir les valeurs saisies en une liste de nombres
                valeurs = list(map(float, valeurs.split(',')))

                # Vérifier le type de calcul demandé via GET
                calcul_type = request.GET.get('type')

                if calcul_type == 'moyenne':
                    mean = statistics.mean(valeurs)
                elif calcul_type == 'mediane':
                    median = statistics.median(valeurs)
                elif calcul_type == 'mode':
                    try:
                        mode = statistics.mode(valeurs)
                    except statistics.StatisticsError:
                        mode = "Pas de mode unique."
                elif calcul_type == 'variance':
                    variance = statistics.variance(valeurs)
                elif calcul_type == 'ecart_type':
                    stdev = statistics.stdev(valeurs)
                elif calcul_type == 'calcul_complet':  # Cas pour le calcul complet
                    mean = statistics.mean(valeurs)
                    median = statistics.median(valeurs)
                    try:
                        mode = statistics.mode(valeurs)
                    except statistics.StatisticsError:
                        mode = "Pas de mode unique."
                    variance = statistics.variance(valeurs)
                    stdev = statistics.stdev(valeurs)
                else:
                    return HttpResponse("Erreur : Type de calcul inconnu.")
            except ValueError:
                return HttpResponse("Erreur : Veuillez entrer uniquement des nombres séparés par des virgules.")
        else:
            return HttpResponse("Erreur : Aucun nombre saisi.")

    return render(request, 'app1/calcules.html', {
        'mean': mean,
        'median': median,
        'mode': mode,
        'variance': variance,
        'stdev': stdev,
    })



# Vue pour l'importation des fichiers Excel
def upload_excel(request):
    if request.method == "POST":
        excel_file = request.FILES.get('excel_file')

        # Vérification de la présence du fichier
        if not excel_file:
            return HttpResponse("Veuillez importer un fichier Excel.")

        # Lecture du fichier Excel avec Pandas
        try:
            # Charger le fichier avec la première ligne comme en-tête (header=0)
            df = pd.read_excel(excel_file, header=0)

            # Vérification des colonnes lues
            print("Colonnes lues dans le fichier Excel :")
            print(df.columns)  # Affiche les colonnes du DataFrame

            # Nettoyer les noms de colonnes, enlever les espaces inutiles
            df.columns = df.columns.str.strip()
         
            # Vérification après nettoyage des noms de colonnes
            print("Colonnes après nettoyage :")
            print(df.columns)

            # Vérification des types de données dans chaque colonne
            print("Types des colonnes :")
            print(df.dtypes)

            # Vérifier si les données semblent correctes
            if df.empty:
                return HttpResponse("Le fichier Excel est vide.")
            df = pd.read_excel(excel_file, header=None)
            # Stocker les données sous forme de dictionnaire dans la session
            request.session['data'] = df.to_dict(orient='list')  # Utilisation de 'list' au lieu de 'dict'

            return redirect('select_calculations')  # Rediriger vers la page des calculs

        except Exception as e:
            return HttpResponse(f"Erreur lors de l'import du fichier : {e}")

    return render(request, "app1/upload_excel.html")


# Vue pour afficher la page de sélection des calculs
def select_calculations(request):
    if 'data' not in request.session:
        return redirect('upload_excel')  # Rediriger si aucun fichier n'a été importé

    # Récupérer les colonnes disponibles
    data = pd.DataFrame(request.session['data'])
    columns = data.columns.tolist()  # Liste des colonnes

    # Vérification des colonnes disponibles dans le fichier
    print("Colonnes disponibles dans les données :", columns)  # Afficher les colonnes dans la console pour le debug

    return render(request, 'app1/select_calculations.html', {'columns': columns})


# Vue pour effectuer les calculs statistiques
def perform_calculations(request):
    if 'data' not in request.session:
        return redirect('upload_excel')  # Rediriger si aucun fichier n'a été importé

    # Charger les données depuis la session
    data = pd.DataFrame(request.session['data'])

    if request.method == "POST":
        column = request.POST.get('column')  # Colonne choisie
        calculations = request.POST.getlist('calculations')  # Calculs choisis

        # Vérification de la validité de la colonne
        if column not in data.columns:
            return HttpResponse(f"Erreur : la colonne '{column}' n'existe pas dans les données.")  # Message d'erreur plus spécifique

        try:
            # Filtrer et convertir les valeurs en float uniquement si elles sont valides
            values = pd.to_numeric(data[column], errors='coerce').dropna()  # 'coerce' remplace les valeurs non numériques par NaN, qui seront ensuite supprimées avec dropna()

            if values.empty:
                return HttpResponse(f"Erreur : la colonne '{column}' ne contient pas de valeurs numériques valides.")  # Si aucune valeur numérique n'est trouvée

            results = {}

            # Effectuer les calculs demandés
            if 'moyenne' in calculations:
                results['Moyenne'] = statistics.mean(values)
            if 'mediane' in calculations:
                results['Médiane'] = statistics.median(values)
            if 'mode' in calculations:
                try:
                    results['Mode'] = statistics.mode(values)
                except statistics.StatisticsError:
                    results['Mode'] = "Pas de mode unique."
            if 'variance' in calculations:
                try:
                    results['Variance'] = statistics.variance(values)
                except statistics.StatisticsError:
                    results['Variance'] = "Pas assez de données pour calculer la variance."
            if 'ecart_type' in calculations:
                try:
                    results['Écart-type'] = statistics.stdev(values)
                except statistics.StatisticsError:
                    results['Écart-type'] = "Pas assez de données pour calculer l'écart-type."
            if 'total' in calculations:
                results['Moyenne'] = statistics.mean(values)
                results['Médiane'] = statistics.median(values)
                try:
                    results['Mode'] = statistics.mode(values)
                except statistics.StatisticsError:
                    results['Mode'] = "Pas de mode unique."
                try:
                    results['Variance'] = statistics.variance(values)
                except statistics.StatisticsError:
                    results['Variance'] = "Pas assez de données pour calculer la variance."
                try:
                    results['Écart-type'] = statistics.stdev(values)
                except statistics.StatisticsError:
                    results['Écart-type'] = "Pas assez de données pour calculer l'écart-type."

            return render(request, 'app1/results.html', {'results': results, 'column': column})
        except Exception as e:
            return HttpResponse(f"Erreur lors du calcul : {e}")

    return redirect('select_calculations')

