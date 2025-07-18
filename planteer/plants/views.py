from django.shortcuts import render, redirect, get_object_or_404
from .models import Plant
from .forms import PlantForm , CommentForm
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.

def plant_list_view(request):
    plants = Plant.objects.all()

    # GET filter values
    category = request.GET.get('category')
    is_edible = request.GET.get('is_edible')

    # Filter if selected
    if category:
        plants = plants.filter(category=category)

    if is_edible == 'true':
        plants = plants.filter(is_edible=True)
    elif is_edible == 'false':
        plants = plants.filter(is_edible=False)

    # Paginate
    # here to to confirm howmany plant per page (6)
    paginator = Paginator(plants, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'plants': page_obj,
        'page_obj': page_obj,
        'category': category,
        'is_edible': is_edible,
    }
    return render(request, 'plants/plant_list.html', context)

def plant_create_view(request):
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('plants:plant_list') 
    else:
        form = PlantForm()

    return render(request, 'plants/plant_form.html', {'form': form})

def plant_search_view(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    is_edible = request.GET.get('is_edible')

    plants = Plant.objects.all()

    if query:
        plants = plants.filter(Q(name__icontains=query))

    if category and category != 'all':
        plants = plants.filter(category=category)

    if is_edible == 'true':
        plants = plants.filter(is_edible=True)
    elif is_edible == 'false':
        plants = plants.filter(is_edible=False)
    
    #._meta.get_field used to access model info
    categories = Plant._meta.get_field('category').choices

    context = {
        'plants': plants,
        'query': query,
        'category': category,
        'is_edible': is_edible,
        'categories': categories,
    }
    return render(request, 'plants/plant_search.html', context)

def plant_detail_view(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)
    related_plants = Plant.objects.filter(category=plant.category).exclude(id=plant.id)[:4]

    form = CommentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        comment = form.save(commit=False)
        comment.plant = plant
        comment.save()
        return redirect('plants:plant_detail', plant_id=plant.id)

    context = {
        'plant': plant,
        'related_plants': related_plants,
        'form': form,
    }
    return render(request, 'plants/plant_detail.html', context)

def plant_update_view(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES, instance=plant)
        if form.is_valid():
            form.save()
            return redirect('plants:plant_detail', plant_id=plant.id)
    else:
        form = PlantForm(instance=plant)

    return render(request, 'plants/plant_form.html', {'form': form, 'update': True})

def plant_delete_view(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)
    if request.method == 'POST':
        plant.delete()
        return redirect('plants:plant_list')
    return render(request, 'plants/plant_confirm_delete.html', {'plant': plant})