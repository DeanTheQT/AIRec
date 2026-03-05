from django import forms
from .models import Product

class RecommendForm(forms.Form):
    query = forms.CharField(
        label="what are you looking for?",
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g., budget gaming laptop under 30k"
            }
        ),
    )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'tags', 'description', 'price', 'popularity']