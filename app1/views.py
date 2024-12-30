from django.shortcuts import render
import statistics
from django.shortcuts import render, redirect
from scipy.stats import bernoulli
from scipy.stats import binom
from scipy.stats import expon
from scipy.stats import norm
from scipy.stats import poisson
from scipy.stats import uniform
from .forms import FileUploadForm
from django.http import HttpResponseBadRequest
import pandas as pd
import numpy as np
from django.templatetags.static import static
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO, BytesIO
import base64
from .forms import FileUploadForm,TraitementForm
import matplotlib
from django.http import HttpResponse


matplotlib.use('Agg')
def visualisation(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            fichier = request.FILES['file']
            traitement_choice = request.POST['processing_choice']

            if traitement_choice == 'visualiser les donnees':
                allowed_file_types = ['application/vnd.ms-excel', 'text/csv', 'text/plain', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
                if fichier.content_type not in allowed_file_types:
                    return HttpResponseBadRequest("Format de fichier non pris en charge. Veuillez télécharger un fichier Excel, CSV ou texte.")

                if fichier.content_type == 'application/vnd.ms-excel' or fichier.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    data = pd.read_excel(fichier)
                else:
                    data = pd.read_csv(fichier)

                df = pd.DataFrame(data)
                search_term = request.POST.get('search_input', '').lower()
                
                if search_term:
                    df = df[df.apply(lambda row: any(str(search_term) in str(cell).lower() for cell in row), axis=1)]

                return render(request, 'app1/parcourir.html', {'form': form, 'df': df.to_html(classes='table table-bordered', index=False)})

            elif traitement_choice == 'graphe':
                allowed_file_types = ['application/vnd.ms-excel', 'text/csv', 'text/plain', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
                if fichier.content_type not in allowed_file_types:
                    return HttpResponseBadRequest("Format de fichier non pris en charge. Veuillez télécharger un fichier Excel, CSV ou texte.")

                if fichier.content_type == 'application/vnd.ms-excel' or fichier.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    data = pd.read_excel(fichier)
                else:
                    data = pd.read_csv(fichier)

                df = pd.DataFrame(data)
                columns_choices = [(col, col) for col in df.columns]
                df_json = df.to_json()
                request.session['df_json'] = df_json
                print("df_head columns:", df.columns)
                return render(request, 'app1/choix_colonnes.html', {'form': form, 'column_names': df.columns})

        else:
            form = FileUploadForm(request.POST, request.FILES)  

    else:
        form = FileUploadForm()

    return render(request, 'app1/visualisation.html', {'form': form})

def parcourir_chart(request):
    df = None
    columns_choices = None
    error_message = ""
    max_row = 0

    if 'df_json' in request.session:
        df_json = request.session['df_json']
        df = pd.read_json(StringIO(df_json))
        columns_choices = [col for col in df.columns]
        max_row = df.shape[0] - 1
        
    if request.method == 'POST':
        selected_columns = request.POST.getlist('selected_columns')
        parcourir_chart_type = request.POST.get('parcourir_chart')
        col_name1 = request.POST.get('col_name1')
        row_numb = request.POST.get('RowNumb')
        
        if selected_columns:
            df = df[selected_columns]

        if parcourir_chart_type == 'GroupBy':
            numeric_column = request.POST.get('numeric_column')
            condition = request.POST.get('condition')
            value = request.POST.get('value')

            if numeric_column and condition and value :
                try:
                    grouped_df = df.groupby(numeric_column)
                    value = float(value)
                    if condition == '>' :
                        df = grouped_df.filter(lambda x: x[numeric_column].mean() > value)
                    elif condition == '<':
                        df = grouped_df.filter(lambda x: x[numeric_column].mean() < value)
                    elif condition == '=':
                        df = grouped_df.filter(lambda x: x[numeric_column].mean() == value)
                except Exception as e:
                    error_message = f"Une erreur est survenue : {str(e)}"

            contexte = {
                'df': df.to_html(classes='table table-bordered') if df is not None else None,
                'column_names': columns_choices,
                'max_row': max_row,
                'error_message': error_message
            }
            return render(request, 'app1/parcourir.html', contexte)
        if parcourir_chart_type == 'FindElem' and df is not None:
            try:
                row_numb = int(row_numb)
                row_numb = min(row_numb, max_row)
                resultats_recherche = df.at[row_numb, col_name1]
                contexte = {'resultat': resultats_recherche, 'column_names': columns_choices, 'df': df.to_html(classes='table table-bordered'), 'max_row': max_row}
                return render(request, 'app1/parcourir.html', contexte)
            except (ValueError, KeyError, IndexError):
                pass

        parcourir_rows_type = request.POST.get('parcourir_rows')

        if parcourir_rows_type == 'NbrOfRowsTop':
            nb_rows_top = int(request.POST.get('Head'))
            df = df.head(nb_rows_top)
        elif parcourir_rows_type == 'NbrOfRowsBottom':
            nb_rows_bottom = int(request.POST.get('Tail'))
            df = df.tail(nb_rows_bottom)
        elif parcourir_rows_type == 'FromRowToRow':
            from_row = int(request.POST.get('FromRowNumb'))
            to_row = int(request.POST.get('ToRowNumb'))
            df = df.loc[from_row:to_row]

    contexte = {
        'df': df.to_html(classes='table table-bordered') if df is not None else None,
        'column_names': columns_choices, 
        'max_row': max_row
    }   
    return render(request, 'app1/parcourir.html', contexte)













def index(request):
    return render(request, 'app1/index.html')


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
            if 'total' in calculations:
                results['Moyenne'] = statistics.mean(values)
                results['Médiane'] = statistics.median(values)
                try:
                    results['Mode'] = statistics.mode(values)
                except statistics.StatisticsError:
                    results['Mode'] = "Pas de mode unique."
                results['Variance'] = statistics.variance(values)
                results['Écart-type'] = statistics.stdev(values)

            return render(request, 'app1/results.html', {'results': results, 'column': column})
        except Exception as e:
            return HttpResponse(f"Erreur lors du calcul : {e}")

    return redirect('select_calculations')




def traitement_fichier(request):
    return render(request, 'app1/traitement_fichier.html')

def visualisation_de_donnnes(request):
    return render(request, 'app1/visualiser_les_donnees.html')
def traitement_graphe(request):
    return render(request, 'app1/traitement_graphe.html')

def choixcolonnes(request):
    return render(request,'app1/choix_colonnes.html')
def diagramme(request):
    return render(request, 'app1/diagramme.html')
def visualiser_chart(request): 
    if request.method == 'POST':
        col1 = request.POST['col_name1']
        col2 = request.POST['col_name2']
        type_chart = request.POST['type_chart']
        df_json = request.session.get('df_json')
        
        df_json_io = StringIO(df_json)
        df = pd.read_json(df_json_io)
        
        chart, error_message = generate_chart(df, type_chart, col1, col2)
        
        if error_message:
            context = {
                'error_message': error_message
            }
            return render(request, 'app1/choix_colonnes.html', context)

        else:
            plot_data = base64.b64encode(chart.getvalue()).decode('utf-8')
            context = {
                'chart': plot_data
            }
            return render(request, 'app1/diagramme.html', context)  
    
    return render(request, 'app1/choix_colonnes.html')

def generate_chart(df, type_chart, col1, col2):
    buffer = BytesIO()
    error_message = None

    def check_col1_string():
        if df[col1].dtype.kind in 'iufc':
                raise ValueError("la première colonne doit être une colonne chaine de caractère")
    def check_col2_string():
        if df[col2].dtype.kind in 'iufc':
                raise ValueError("la deuxieme colonne doit être une colonne chaine de caractère")
    def check_col1_numeric():
        if not pd.api.types.is_numeric_dtype(df[col1]):
            raise ValueError("la première colonne doit être une colonne numérique")
    def check_col2_numeric():
        if not pd.api.types.is_numeric_dtype(df[col2]):
            raise ValueError("la deuxieme colonne doit être une colonne numérique")
    def check_sum_equals_100():
        if df[col2].sum() != 100:
            raise ValueError("La somme des éléments de la deuxième colonne doit être égale à 100")
    try:
        if type_chart == 'bar':
            check_col1_string()
            check_col2_numeric()
            plt.bar(df[col1], df[col2])
            plt.xlabel(col1)
            plt.ylabel(col2)
            plt.title('Bar Plot')

        elif type_chart == 'histogram':
            check_col1_numeric()
            plt.hist(df[col1])
            plt.xlabel(col1)
            plt.ylabel('Fréquence')
            plt.title('Histogramme')

        elif type_chart == 'piechart':
            check_col2_numeric()
            check_sum_equals_100()
            plt.pie(df[col1], labels=df[col2])
            plt.title('Pie Chart')

        elif type_chart == 'histplot':
            check_col1_numeric()
            sns.histplot(df[col1])
            plt.xlabel(col1)
            plt.ylabel('Count')
            plt.title('Histogram Plot')

        elif type_chart == 'scatterplot':
            check_col1_numeric()
            check_col2_numeric()
            plt.scatter(df[col1], df[col2])
            plt.xlabel(col1)
            plt.ylabel(col2)
            plt.title('Scatter Plot')

        elif type_chart == 'heatmap':
            check_col1_numeric()
            check_col2_numeric()
            pivot_table = df.pivot_table(index=col1, columns=col2, aggfunc=len)
            sns.heatmap(pivot_table, cmap='coolwarm')
            plt.title('Heatmap')

        elif type_chart == 'lineplot':
            check_col1_numeric()
            check_col2_numeric()
            plt.plot(df[col1], df[col2]) 
            plt.xlabel(col1)
            plt.ylabel(col2)
            plt.title('Line Plot')

        elif type_chart == 'boxplot':
            check_col1_numeric()
            check_col2_numeric()
            sns.boxplot(x=df[col1], y=df[col2])
            plt.xlabel(col1)
            plt.ylabel(col2)
            plt.title('Box Plot')

        elif type_chart == 'violinplot':
            check_col1_numeric()
            check_col2_numeric()
            sns.violinplot(x=df[col1], y=df[col2])
            plt.xlabel(col1)
            plt.ylabel(col2)
            plt.title('Violin Plot')
            
        elif type_chart == 'kdeplot':
            check_col1_numeric()
            sns.kdeplot(df[col1], shade=True)
            plt.xlabel(col1)
            plt.title('KDE Plot')
 
    except ValueError as e:
        error_message = str(e)

    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return buffer,error_message



def accueil(request):
    return render(request, 'accueil.html')  

def bernoullii(request):
    return render(request, 'app1/lois/bernoullii.html')
def binomial(request):
    return render(request, 'app1/lois/binomial.html')
def exponentielle(request):
    return render(request, 'app1/lois/exponentielle.html')
def normal(request):
    return render(request, 'app1/lois/normal.html')
def poissonn(request):
    return render(request, 'app1/lois/poissonn.html')
def uniforme(request):
    return render(request, 'app1/lois/uniforme.html')
def uniformecontinue(request):
    return render(request, 'app1/lois/uniformecontinue.html')
def afficher_bernoullii(request):
    error_message = None  
    
    if request.method == 'POST':
        try:
            probability_of_success = float(request.POST['probability_of_success'])

            if 0 <= probability_of_success <= 1:
                data = bernoulli.rvs(p=probability_of_success, size=1000)

                plt.hist(data, bins=[0, 1, 2], align='left', rwidth=0.8, color='skyblue')

                plt.title('Distribution de Bernoulli')
                plt.xlabel('Valeurs')
                plt.ylabel('Fréquence')

                plt.xticks([0, 1], ['Échec (0)', 'Succès (1)'])

                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                plt.close()
                chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

                context = {
                    'probability_of_success': probability_of_success,
                    'chart_image': chart_image
                }

                return render(request, 'app1/afficher_loi/afficher_bernoullii.html', context)
            else:
                error_message = "La probabilité de succès doit être comprise entre 0 et 1."
        except ValueError:
            error_message = "La probabilité de succès doit être un nombre valide."

    context = {'error_message': error_message}
    
    return render(request, 'app1/lois/bernoullii.html', context)
def afficher_binomial(request):
    error_message = None

    if request.method == 'POST':
        try:
            probability_of_success = float(request.POST['probability_of_success'])
            number_of_trials = int(request.POST['number_of_trials'])

            if not (0 <= probability_of_success <= 1):
                raise ValueError("La probabilité de succès doit être comprise entre 0 et 1.")

            if number_of_trials <= 0:
                raise ValueError("Le nombre d'essais doit être un entier positif.")

            data = binom.rvs(n=number_of_trials, p=probability_of_success, size=1000)

            plt.hist(data, bins=range(number_of_trials + 2), align='left', rwidth=0.8, color='skyblue')

            plt.title('Distribution Binomiale')
            plt.xlabel('Valeurs')
            plt.ylabel('Fréquence')

            plt.xticks(range(number_of_trials + 1))

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            context = {
                'probability_of_success': probability_of_success,
                'number_of_trials': number_of_trials,
                'chart_image': chart_image
            }

            return render(request, 'app1/afficher_loi/afficher_binomial.html', context)

        except ValueError as e:
            error_message = str(e)

    context = {'error_message': error_message}

    return render(request, 'app1/lois/binomial.html', context)
def afficher_exponentielle(request):
    error_message = None

    if request.method == 'POST':
        try:
            rate_parameter = float(request.POST['rate_parameter'])

            if rate_parameter <= 0:
                raise ValueError("Le paramètre de taux doit être un nombre positif.")

            data = expon.rvs(scale=1/rate_parameter, size=1000)

            plt.hist(data, bins=30, color='skyblue', edgecolor='black')

            plt.title('Distribution Exponentielle')
            plt.xlabel('Valeurs')
            plt.ylabel('Fréquence')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            context = {
                'rate_parameter': rate_parameter,
                'chart_image': chart_image
            }

            return render(request, 'app1/afficher_loi/afficher_exponentielle.html', context)

        except ValueError as e:
            error_message = str(e)

    context = {'error_message': error_message}

    return render(request, 'app1/lois/exponentielle.html', context)
def afficher_normal(request):
    error_message = None

    if request.method == 'POST':
        try:
            mean = float(request.POST['mean'])
            standard_deviation = float(request.POST['standard_deviation'])

            if standard_deviation <= 0:
                raise ValueError("L'écart-type doit être un nombre positif.")

            data = norm.rvs(loc=mean, scale=standard_deviation, size=1000)

            plt.hist(data, bins=30, color='skyblue', edgecolor='black')

            plt.title('Distribution Normale')
            plt.xlabel('Valeurs')
            plt.ylabel('Fréquence')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            context = {
                'mean': mean,
                'standard_deviation': standard_deviation,
                'chart_image': chart_image
            }

            return render(request, 'app1/afficher_loi/afficher_normal.html', context)

        except ValueError as e:
            error_message = str(e)

    context = {'error_message': error_message}

    return render(request, 'app1/lois/normal.html', context)
def afficher_poissonn(request):
    error_message = None

    if request.method == 'POST':
        try:
            average_rate = float(request.POST['average_rate'])

            if average_rate <= 0:
                raise ValueError("Le taux moyen doit être un nombre positif.")

            data = poisson.rvs(mu=average_rate, size=1000)

            plt.hist(data, bins=range(max(data)+2), align='left', rwidth=0.8, color='skyblue')

            plt.title('Distribution de Poisson')
            plt.xlabel('Valeurs')
            plt.ylabel('Fréquence')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            context = {
                'average_rate': average_rate,
                'chart_image': chart_image
            }

            return render(request, 'app1/afficher_loi/afficher_poissonn.html', context)

        except ValueError as e:
            error_message = str(e)

    context = {'error_message': error_message}

    return render(request, 'app1/lois/poissonn.html', context)

def afficher_uniformecontinue(request):
    error_message = None

    if request.method == 'POST':
        try:
            min_value = float(request.POST['min_value'])
            max_value = float(request.POST['max_value'])

            if min_value > max_value:
                raise ValueError("La valeur minimale doit être inférieure à la valeur maximale.")

            data = uniform.rvs(loc=min_value, scale=max_value-min_value, size=1000)

            plt.hist(data, bins=30, color='skyblue', edgecolor='black')

            plt.title('Loi Uniforme Continue')
            plt.xlabel('Valeurs')
            plt.ylabel('Fréquence')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            context = {
                'min_value': min_value,
                'max_value': max_value,
                'chart_image': chart_image
            }

            return render(request, 'app1/afficher_loi/afficher_uniformecontinue.html', context)

        except ValueError as e:
            error_message = str(e)

    context = {'error_message': error_message}

    return render(request, 'app1/lois/uniformecontinue.html', context)

def afficher_uniforme(request):
    error_message = None

    if request.method == 'POST':
        try:
            min_value = float(request.POST['min_value'])
            max_value = float(request.POST['max_value'])

            if min_value >= max_value:
                raise ValueError("La valeur minimale doit être strictement inférieure à la valeur maximale.")

            data = [min_value + (max_value - min_value) * i / 100 for i in range(100)]

            plt.hist(data, bins=30, color='skyblue', edgecolor='black')

            plt.title('Loi Uniforme Discontinue')
            plt.xlabel('Valeurs')
            plt.ylabel('Fréquence')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            context = {
                'min_value': min_value,
                'max_value': max_value,
                'chart_image': chart_image
            }

            return render(request, 'app1/afficher_loi/afficher_uniforme.html', context)

        except ValueError as e:
            error_message = str(e)

    context = {'error_message': error_message}

    return render(request, 'app1/lois/uniforme.html', context)










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