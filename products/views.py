from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib import messages
from users.models import Contact
from .forms import ContactForm, ReviewForm
from .models import Product, Category, Review
from decimal import Decimal, InvalidOperation
from designs.models import DesignAsset  # added for mixed cart
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string

def home(request):
    products = Product.objects.filter(discount__gte=10)[:3]
    message = ''
    success = False

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            message = "Your message has been sent successfully!"
            success = True
    else:
        form = ContactForm()

    return render(
        request,
        'index.html',
        {
            'message': message,
            'success': success,
            'products': products,
            'form': form,
        }
    )


# ------------------------- CART UTILITIES -------------------------
def _get_cart(session):
    # cart structure: {"P:<uuid>": qty, "D:<uuid>": qty}
    return session.get('cart', {})

def _save_cart(session, cart):
    session['cart'] = cart
    session.modified = True


# ------------------------- STORE VIEW -----------------------------
def store_view(request):
    qs = Product.objects.filter(is_active=True).select_related('category')
    category_slug = request.GET.get('category')
    if category_slug:
        qs = qs.filter(category__name__iexact=category_slug)
    search = request.GET.get('q')
    if search:
        qs = qs.filter(name__icontains=search)
    try:
        per_page = int(request.GET.get('page_size', '9'))
    except ValueError:
        per_page = 9
    per_page = max(3, min(per_page, 48))  # sane bounds
    paginator = Paginator(qs, per_page)
    page = request.GET.get('page')
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    categories = Category.objects.all()
    context = {
        'products': products_page.object_list,
        'page_obj': products_page,
        'paginator': paginator,
        'is_paginated': products_page.has_other_pages(),
        'categories': categories,
        'current_category': category_slug,
        'search_query': search,
        'page_size': per_page,
    'page_size_options': [9, 18, 27, 36],
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return only the products grid + pagination
        html = render_to_string('partials/_product_grid.html', context, request=request)
        pagination = render_to_string('partials/_pagination.html', context, request=request)
        return JsonResponse({'html': html, 'pagination': pagination})
    return render(request, 'store.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:8]
    reviews = product.reviews.select_related('user').order_by('-created_at')
    form = None
    # Handle review submission
    if request.method == 'POST' and request.POST.get('form_type') == 'review':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to leave a review.')
            return redirect('login')
        # Prevent duplicate review (unique_together)
        existing = Review.objects.filter(product=product, user=request.user).first()
        form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been saved.')
            return redirect('product_detail', slug=product.slug)
    else:
        if request.user.is_authenticated:
            existing = Review.objects.filter(product=product, user=request.user).first()
            form = ReviewForm(instance=existing)
    context = {
        'product': product,
        'related': related,
        'reviews': reviews,
        'review_form': form,
    }
    return render(request, 'product_detail.html', context)


@require_POST
def add_to_cart(request):
    item_id = request.POST.get('product_id')  # existing param name
    item_type = request.POST.get('type', 'product')  # 'product' or 'design'
    qty = request.POST.get('qty', '1')
    try:
        qty = int(qty)
    except ValueError:
        return HttpResponseBadRequest('Invalid qty')
    if qty < 1:
        qty = 1
    if item_type == 'design':
        obj = get_object_or_404(DesignAsset, pk=item_id, is_active=True)
        key = f"D:{obj.pk}"
    else:
        obj = get_object_or_404(Product, pk=item_id, is_active=True)
        key = f"P:{obj.pk}"
    cart = _get_cart(request.session)
    cart[key] = cart.get(key, 0) + qty
    _save_cart(request.session, cart)
    count = sum(cart.values())
    return JsonResponse({'ok': True, 'count': count, 'key': key})


@require_POST
def update_cart_item(request):
    product_id = request.POST.get('product_id')  # may include prefix P: or D:
    action = request.POST.get('action')  # inc, dec, remove
    cart = _get_cart(request.session)
    key = str(product_id)
    if key not in cart:
        return HttpResponseBadRequest('Item not in cart')
    if action == 'inc':
        cart[key] += 1
    elif action == 'dec':
        cart[key] = max(1, cart[key] - 1)
    elif action == 'remove':
        del cart[key]
    else:
        return HttpResponseBadRequest('Bad action')
    _save_cart(request.session, cart)
    # Compute updated subtotal and line total (if item still exists)
    product = None
    line_total = 0
    if key in cart:
        if key.startswith('P:'):
            pid = key.split(':',1)[1]
            product = Product.objects.filter(pk=pid).first()
            if product:
                line_total = float(product.price) * cart[key]
        elif key.startswith('D:'):
            did = key.split(':',1)[1]
            product = DesignAsset.objects.filter(pk=did).first()
            if product:
                line_total = float(product.price) * cart[key]
        elif key.startswith('C:'):
            # Donation / advance payment
            price = request.session.get('donation_price')
            try:
                price_val = float(price)
            except (TypeError, ValueError):
                price_val = 0
            line_total = price_val * cart[key]
    subtotal = 0
    if cart:
        product_ids = [k.split(':',1)[1] for k in cart.keys() if k.startswith('P:')]
        design_ids = [k.split(':',1)[1] for k in cart.keys() if k.startswith('D:')]
        products = Product.objects.filter(pk__in=product_ids)
        designs = DesignAsset.objects.filter(pk__in=design_ids)
        price_map = {f"P:{p.pk}": float(p.price) for p in products}
        price_map.update({f"D:{d.pk}": float(d.price) for d in designs})
        donation_price = request.session.get('donation_price')
        if donation_price is not None and 'C:DONATION' in cart:
            try:
                price_map['C:DONATION'] = float(donation_price)
            except (TypeError, ValueError):
                price_map['C:DONATION'] = 0
        subtotal = sum(price_map.get(k, 0) * q for k, q in cart.items())
    return JsonResponse({
        'ok': True,
        'qty': cart.get(key, 0),
        'count': sum(cart.values()),
        'line_total': round(line_total, 2),
        'subtotal': round(subtotal, 2),
        'removed': key not in cart
    })


def cart_view(request):
    cart = _get_cart(request.session)
    product_ids = [k.split(':',1)[1] for k in cart.keys() if k.startswith('P:')]
    design_ids = [k.split(':',1)[1] for k in cart.keys() if k.startswith('D:')]
    products = Product.objects.filter(pk__in=product_ids)
    designs = DesignAsset.objects.filter(pk__in=design_ids)
    prod_map = {f"P:{p.pk}": p for p in products}
    design_map = {f"D:{d.pk}": d for d in designs}
    items = []
    subtotal = 0
    for key, qty in cart.items():
        obj = prod_map.get(key) or design_map.get(key)
        if key.startswith('C:'):
            price = request.session.get('donation_price')
            try:
                price_dec = Decimal(str(price))
            except (InvalidOperation, TypeError):
                price_dec = Decimal('0')
            line_total = price_dec * qty
            items.append({'key': key, 'product': type('Tmp', (), {'name': 'Advance Payment', 'price': price_dec, 'image': None})(), 'qty': qty, 'line_total': line_total, 'is_design': False, 'is_donation': True})
            subtotal += line_total
            continue
        if not obj:
            continue
        line_total = obj.price * qty
        subtotal += line_total
        items.append({'key': key, 'product': obj, 'qty': qty, 'line_total': line_total, 'is_design': key.startswith('D:'), 'is_donation': False})
    return render(request, 'cart.html', {'items': items, 'subtotal': subtotal})


def checkout_view(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.info(request, 'Your cart is empty.')
        return redirect('store')
    product_ids = [k.split(':',1)[1] for k in cart.keys() if k.startswith('P:')]
    design_ids = [k.split(':',1)[1] for k in cart.keys() if k.startswith('D:')]
    products = Product.objects.filter(pk__in=product_ids)
    designs = DesignAsset.objects.filter(pk__in=design_ids)
    prod_map = {f"P:{p.pk}": p for p in products}
    design_map = {f"D:{d.pk}": d for d in designs}
    items = []
    total = 0
    donation_price = request.session.get('donation_price')
    for key, qty in cart.items():
        if key.startswith('C:'):
            try:
                price_dec = Decimal(str(donation_price))
            except (InvalidOperation, TypeError):
                price_dec = Decimal('0')
            line_total = price_dec * qty
            total += line_total
            items.append({'product': type('Tmp', (), {'name': 'Advance Payment', 'price': price_dec, 'image': None})(), 'qty': qty, 'line_total': line_total})
            continue
        obj = prod_map.get(key) or design_map.get(key)
        if not obj:
            continue
        line_total = obj.price * qty
        total += line_total
        items.append({'product': obj, 'qty': qty, 'line_total': line_total})
    if request.method == 'POST':
        # Here you'd create Order / OrderItems
        request.session.pop('cart', None)
        messages.success(request, 'Order placed successfully!')
        return redirect('store')
    return render(request, 'checkout.html', {'items': items, 'total': total})


# ------------------------- ADVANCE PAYMENT (DONATION) ------------------
def donation_view(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        qty = request.POST.get('qty', '1')
        try:
            qty_int = max(1, int(qty))
        except ValueError:
            qty_int = 1
        try:
            amount_dec = Decimal(amount)
            if amount_dec <= 0:
                raise InvalidOperation
        except (InvalidOperation, TypeError):
            messages.error(request, 'Enter a valid positive amount.')
        else:
            cart = _get_cart(request.session)
            # Store unit price in session and qty in cart
            request.session['donation_price'] = str(amount_dec)
            cart['C:DONATION'] = cart.get('C:DONATION', 0) + qty_int
            _save_cart(request.session, cart)
            messages.success(request, 'Advance payment added to cart.')
            return redirect('cart')
    return render(request, 'donation.html')


# ------------------------- PUBLIC OFFER PAGE ------------------
def public_offer(request):
    """Static public offer / terms of service page."""
    return render(request, 'public_offer.html')


