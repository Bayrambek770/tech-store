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
    """Product listing with optional category + name search filters.

    Fixes:
    - Use stable category primary key instead of translated name for filtering.
    - Query translated product names via parler translation table.
    - Preserve submitted search/category values in the form.
    """
    qs = Product.objects.filter(is_active=True).select_related('category')
    # Category filter (expect primary key in GET)
    category_raw = request.GET.get('category')
    current_category_id = None
    if category_raw:
        try:
            current_category_id = int(category_raw)
        except (TypeError, ValueError):
            current_category_id = None
    if current_category_id:
        qs = qs.filter(category_id=current_category_id)
    # Search across translated names (django-parler)
    search = request.GET.get('q')
    if search:
        qs = qs.filter(translations__name__icontains=search).distinct()
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
        'current_category': current_category_id,
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
    try:
        product_id = request.POST.get('product_id')  # already prefixed key (P:, D:, C:)
        action = request.POST.get('action')  # inc | dec | remove
        cart = _get_cart(request.session)
        key = str(product_id)
        if key not in cart:
            return JsonResponse({'ok': False, 'error': 'not_in_cart'}, status=400)

        if action == 'inc':
            cart[key] += 1
        elif action == 'dec':
            cart[key] = max(1, cart[key] - 1)
        elif action == 'remove':
            del cart[key]
        else:
            return JsonResponse({'ok': False, 'error': 'bad_action'}, status=400)

        _save_cart(request.session, cart)

        # Compute updated subtotal & line total if item still exists
        line_total = 0.0
        if key in cart:
            if key.startswith('P:'):
                obj_id = key.split(':', 1)[1]
                product = Product.objects.filter(pk=obj_id).first()
                if product:
                    price_val = product.safe_translation_getter('price', any_language=True)
                    try:
                        price_num = float(price_val or 0)
                    except (TypeError, ValueError):
                        price_num = 0
                    line_total = price_num * cart[key]
            elif key.startswith('D:'):
                obj_id = key.split(':', 1)[1]
                design = DesignAsset.objects.filter(pk=obj_id).first()
                if design:
                    try:
                        price_num = float(getattr(design, 'price', 0) or 0)
                    except (TypeError, ValueError):
                        price_num = 0
                    line_total = price_num * cart[key]
            elif key.startswith('C:'):
                price = request.session.get('donation_price')
                try:
                    price_val = float(price)
                except (TypeError, ValueError):
                    price_val = 0
                line_total = price_val * cart[key]

        # Subtotal (iterate once over current cart)
        subtotal = 0.0
        if cart:
            product_ids = [k.split(':', 1)[1] for k in cart if k.startswith('P:')]
            design_ids = [k.split(':', 1)[1] for k in cart if k.startswith('D:')]
            products = Product.objects.filter(pk__in=product_ids)
            designs = DesignAsset.objects.filter(pk__in=design_ids)
            price_map = {}
            for p in products:
                val = p.safe_translation_getter('price', any_language=True)
                try:
                    price_map[f"P:{p.pk}"] = float(val or 0)
                except (TypeError, ValueError):
                    price_map[f"P:{p.pk}"] = 0
            for d in designs:
                try:
                    price_map[f"D:{d.pk}"] = float(getattr(d, 'price', 0) or 0)
                except (TypeError, ValueError):
                    price_map[f"D:{d.pk}"] = 0
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
    except Exception as e:
        return JsonResponse({'ok': False, 'error': 'exception', 'detail': str(e)}, status=500)


def cart_view(request):
    """Render the cart page with all current items and a subtotal.

    Uses translation fallback for product name/price so the page never errors
    if a particular translation is missing. Missing prices are treated as 0.
    """
    cart = _get_cart(request.session)
    product_ids = [k.split(':', 1)[1] for k in cart if k.startswith('P:')]
    design_ids = [k.split(':', 1)[1] for k in cart if k.startswith('D:')]
    products = Product.objects.filter(pk__in=product_ids)
    designs = DesignAsset.objects.filter(pk__in=design_ids)
    prod_map = {f"P:{p.pk}": p for p in products}
    design_map = {f"D:{d.pk}": d for d in designs}
    items = []
    subtotal = Decimal('0')

    for key, qty in cart.items():
        if key.startswith('C:'):
            price = request.session.get('donation_price')
            try:
                price_dec = Decimal(str(price))
            except (InvalidOperation, TypeError):
                price_dec = Decimal('0')
            line_total = price_dec * qty
            items.append({
                'key': key,
                'product': type('Tmp', (), {'name': 'Advance Payment', 'price': price_dec, 'image': None})(),
                'qty': qty,
                'line_total': line_total,
                'is_design': False,
                'is_donation': True
            })
            subtotal += line_total
            continue

        obj = prod_map.get(key) or design_map.get(key)
        if not obj:
            continue  # stale entry

        if hasattr(obj, 'safe_translation_getter'):
            price_val = obj.safe_translation_getter('price', any_language=True)
            name_val = obj.safe_translation_getter('name', any_language=True) or str(obj.pk)
            try:
                price_number = Decimal(str(price_val)) if price_val is not None else Decimal('0')
            except (InvalidOperation, TypeError):
                price_number = Decimal('0')
            line_total = price_number * qty
            subtotal += line_total
            temp_obj = obj
            temp_obj.name = name_val
            temp_obj.price = price_number
            items.append({
                'key': key,
                'product': temp_obj,
                'qty': qty,
                'line_total': line_total,
                'is_design': key.startswith('D:'),
                'is_donation': False
            })
            continue

        # Fallback: object without parler translation (e.g. DesignAsset without translated fields)
        try:
            price_number = Decimal(str(getattr(obj, 'price', 0) or 0))
        except (InvalidOperation, TypeError):
            price_number = Decimal('0')
        line_total = price_number * qty
        subtotal += line_total
        items.append({
            'key': key,
            'product': obj,
            'qty': qty,
            'line_total': line_total,
            'is_design': key.startswith('D:'),
            'is_donation': False
        })

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
    total = Decimal('0')
    donation_price = request.session.get('donation_price')

    for key, qty in cart.items():
        # Advance payment entries
        if key.startswith('C:'):
            try:
                price_dec = Decimal(str(donation_price))
            except (InvalidOperation, TypeError):
                price_dec = Decimal('0')
            line_total = price_dec * qty
            total += line_total
            items.append({
                'product': type('Tmp', (), {'name': 'Advance Payment', 'price': price_dec, 'image': None})(),
                'qty': qty,
                'line_total': line_total
            })
            continue

        obj = prod_map.get(key) or design_map.get(key)
        if not obj:
            continue  # stale key

        # Products with translations
        if hasattr(obj, 'safe_translation_getter'):
            price_val = obj.safe_translation_getter('price', any_language=True)
            name_val = obj.safe_translation_getter('name', any_language=True) or str(obj.pk)
            try:
                price_number = Decimal(str(price_val)) if price_val is not None else Decimal('0')
            except (InvalidOperation, TypeError):
                price_number = Decimal('0')
            line_total = price_number * qty
            total += line_total
            # Attach safe fallback values for template rendering
            obj.name = name_val
            obj.price = price_number
            items.append({'product': obj, 'qty': qty, 'line_total': line_total})
            continue

        # Design assets or other objects without translation helper
        try:
            price_number = Decimal(str(getattr(obj, 'price', 0) or 0))
        except (InvalidOperation, TypeError):
            price_number = Decimal('0')
        line_total = price_number * qty
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


