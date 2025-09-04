from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import DesignAsset, DesignCategory, DesignReview
from django.db.models import Q
from .forms import DesignReviewForm
from django.contrib import messages


def marketplace(request):
    qs = DesignAsset.objects.filter(is_active=True).select_related('category')
    cat_type = request.GET.get('type')
    cat_slug = request.GET.get('category')
    if cat_type:
        qs = qs.filter(category__type=cat_type)
    if cat_slug:
        qs = qs.filter(category__slug=cat_slug)
    search = request.GET.get('q')
    if search:
        qs = qs.filter(translations__name__icontains=search)
    try:
        per_page = int(request.GET.get('page_size', '12'))
    except ValueError:
        per_page = 12
    per_page = max(6, min(per_page, 60))
    paginator = Paginator(qs, per_page)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    categories = DesignCategory.objects.all().order_by('type', 'translations__name')
    context = {
        'assets': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'categories': categories,
        'current_type': cat_type,
        'current_category': cat_slug,
        'search_query': search,
        'page_size': per_page,
        'page_size_options': [12, 24, 36, 48],
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('designs/partials/_asset_grid.html', context, request=request)
        pagination = render_to_string('designs/partials/_pagination.html', context, request=request)
        return JsonResponse({'html': html, 'pagination': pagination})
    return render(request, 'designs/marketplace.html', context)


def asset_detail(request, slug):
    asset = get_object_or_404(DesignAsset, slug=slug, is_active=True)
    images = asset.images.all()
    related = DesignAsset.objects.filter(category=asset.category, is_active=True).exclude(pk=asset.pk)[:8]
    reviews = asset.reviews.select_related('user')
    form = None
    if request.method == 'POST' and request.POST.get('form_type') == 'review':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to leave a review.')
            return redirect('login')
        existing = DesignReview.objects.filter(asset=asset, user=request.user).first()
        form = DesignReviewForm(request.POST, instance=existing)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.asset = asset
            rev.user = request.user
            rev.save()
            messages.success(request, 'Your review has been saved.')
            return redirect('designs:asset_detail', slug=asset.slug)
    else:
        if request.user.is_authenticated:
            existing = DesignReview.objects.filter(asset=asset, user=request.user).first()
            form = DesignReviewForm(instance=existing)
    return render(request, 'designs/asset_detail.html', {
        'asset': asset,
        'images': images,
        'related': related,
        'reviews': reviews,
        'review_form': form,
    })
