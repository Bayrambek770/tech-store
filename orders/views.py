from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.utils.translation import gettext as _

from payment.models import Transaction
from payment.provider import InterforumClient
from products.models import Product
from designs.models import DesignAsset
from .models import Order, OrderItem
from payment.models import TransactionStatus
from django.views.decorators.http import require_GET


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'orders/order_success.html', {'order': order})


def _get_cart(session):
    return session.get('cart', {})


@require_POST
def create_order(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.info(request, _('Your cart is empty.'))
        return redirect('store')

    posted_currency = (request.POST.get('currency') or '').upper()
    currency = 'USD' if posted_currency == 'USD' else 'UZS'
    order = Order.objects.create(
        currency=currency,
        first_name=request.POST.get('first_name') or '',
        last_name=request.POST.get('last_name') or '',
        email=request.POST.get('email') or '',
        phone=request.POST.get('phone') or '',
        address1=request.POST.get('address1') or '',
        address2=request.POST.get('address2') or '',
        country=request.POST.get('country') or '',
        state=request.POST.get('state') or '',
        zip=request.POST.get('zip') or '',
    )

    product_ids = [k.split(':', 1)[1] for k in cart if k.startswith('P:')]
    design_ids = [k.split(':', 1)[1] for k in cart if k.startswith('D:')]
    products = {str(p.pk): p for p in Product.objects.filter(pk__in=product_ids)}
    designs = {str(d.pk): d for d in DesignAsset.objects.filter(pk__in=design_ids)}
    donation_price = request.session.get('donation_price')

    for key, qty in cart.items():
        try:
            qty_int = int(qty)
        except (TypeError, ValueError):
            qty_int = 1
        if qty_int < 1:
            qty_int = 1

        if key.startswith('P:'):
            pid = key.split(':', 1)[1]
            product = products.get(pid)
            if not product:
                continue
            price_val = product.safe_translation_getter('price', any_language=True)
            try:
                unit_price = Decimal(str(price_val))
            except (InvalidOperation, TypeError):
                unit_price = Decimal('0')
            OrderItem.objects.create(
                order=order,
                kind='product',
                product=product,
                name=product.safe_translation_getter('name', any_language=True) or str(product.pk),
                quantity=qty_int,
                unit_price=unit_price,
            )
            continue

        if key.startswith('D:'):
            did = key.split(':', 1)[1]
            design = designs.get(did)
            if not design:
                continue
            price_val = design.safe_translation_getter('price', any_language=True)
            try:
                unit_price = Decimal(str(price_val))
            except (InvalidOperation, TypeError):
                unit_price = Decimal('0')
            OrderItem.objects.create(
                order=order,
                kind='design',
                design_asset=design,
                name=design.safe_translation_getter('name', any_language=True) or str(design.pk),
                quantity=qty_int,
                unit_price=unit_price,
            )
            continue

        if key.startswith('C:') and donation_price is not None:
            try:
                unit_price = Decimal(str(donation_price))
            except (InvalidOperation, TypeError):
                unit_price = Decimal('0')
            OrderItem.objects.create(
                order=order,
                kind='donation',
                name=_('Advance Payment'),
                quantity=qty_int,
                unit_price=unit_price,
            )


    order.recalc_total(commit=True)
    transaction = Transaction.objects.create(
        order=order,
        amount=order.total_price*100,
        currency=order.currency
    )

    payment_link = InterforumClient.create_payment_link(transaction)

    request.session.pop('cart', None)
    request.session.pop('donation_price', None)
    request.session.modified = True
    messages.success(request, _('Order created successfully.'))
    return redirect(payment_link)


@require_GET
def payment_return(request):
    # Simple logic: if transaction exists and is SUCCESS show order success, else go home
    tx_id = request.GET.get('tx')
    if not tx_id:
        return redirect('home')
    tx = Transaction.objects.filter(id=tx_id).select_related('order').first()
    if not tx or tx.status != TransactionStatus.SUCCESS:
        return redirect('home')
    return render(request, 'orders/order_success.html', {'order': tx.order})
