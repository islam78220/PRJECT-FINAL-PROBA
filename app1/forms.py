from django import forms

class FileUploadForm(forms.Form):
    file = forms.FileField(label='Sélectionnez un fichier')
    processing_choice = forms.ChoiceField(
        choices=[ ('graphe', 'Graphe'), ('visualiser les donnees', 'Visualiser les donnees')],
        widget=forms.RadioSelect,
        label='Choisissez le traitement'
    )
class TraitementForm(forms.Form):
    valeurs = forms.CharField(label='Liste de valeurs', widget=forms.TextInput(attrs={'placeholder': 'Entrez les valeurs séparées par des tirets (-) ou des virgules (,)'}))