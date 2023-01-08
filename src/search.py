from scm.models import Order

orders = Order.objects.all()

for order in orders:
    try:
        packingstatus = order.packing_status
    except packingstatus.DoesNotExist:
        # print(order.po)


