from django.shortcuts import render, redirect
from .forms import RecommendForm
from .services.recommender import recommend_products
from .db_connection import product_collection
from datetime import datetime
from .forms import ProductForm
from .models import Product
        
def recommend_view(request):
    form = RecommendForm(request.GET or None)
    results = []
    mode = None

    if form.is_valid():
        q = form.cleaned_data["query"]
        results, mode = recommend_products(q, top_k=8)

    return render(
        request,
        "shop/recommend.html",
        {
            "form": form,
            "results": results,
            "mode": mode,
        },
    )
    
def product_list(request):
    products = list(product_collection.find())
    
    return render(request, 'shop/product_list.html', {'products': products})

def add_product(request):
    if request.method == 'POST':  
        form = ProductForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            tags = data.get('tags', [])

            if "Samsung" in tags:
                tags = ["Samsung", "Flagship", "5G", "Android"]

            data['tags'] = tags
            data['price'] = float(data['price'])
            data['created_at'] = datetime.now()

            product_collection.insert_one(data)

            return redirect('product_list')

    else:
        form = ProductForm()

    return render(request, 'shop/add_product.html', {'form': form})