from distutils.command import check
from this import d
from urllib import request
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, TemplateView, DeleteView
from scm.models import (User, Order, Order_color_ratio_qty, Order_avatar,
                        Order_swatches, Order_size_specs,
                        Order_shipping_pics, Order_packing_ctn, Invoice,
                        Order_fitting_sample, Order_bulk_fabric, Order_shipping_sample, Order_production,
                        Order_packing_status, Order_Barcode, PPackingway, Check_item, Check_point, Qc_report,
                        Check_record, Check_record_pics)
from scm.forms import (
                       OrderForm, Order_color_ratio_qty_Form,
                       OrderavatarForm, OrdersizespecsForm,
                       OrderswatchForm, OrdershippingpicsForm,
                       OrderpackingctnForm, InvoiceSearchForm, InvoiceForm,
                       OrderfittingsampleForm, OrderbulkfabricForm, OrderproductionForm,
                       OrdershippingsampleForm, OrderpackingstatusForm,
                       OrderbarcodeForm, CheckrecordpicsForm, QcreportForm)
from django.contrib.auth.decorators import login_required
from scm.decorators import (m_mg_or_required, factory_required, office_required,
                            order_is_shipped, packinglist_is_sented, o_m_mg_or_required,
                            f_f_mg_or_required, m_mg_qc_or_required, qc_required, merchandiser_manager_required)
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.views import reverse_lazy
from django.db.models import F, Sum, IntegerField
from datetime import timedelta
from django.template.loader import render_to_string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import smtplib
import datetime
from decouple import config
from django.core.files.base import ContentFile
from datetime import date, timedelta
import calendar
import json

import smtplib
from email.mime.text import MIMEText
from email.header import Header


# 订单列表-未确认(新建，已送工厂状态)
@method_decorator([login_required], name='dispatch')
class OrderListNew(ListView):
    model = Order
    ordering = ('-created_date', )
    context_object_name = 'orders'
    template_name = 'order_list.html'

    def get_queryset(self):
        loginuser = self.request.user
        if loginuser.is_merchandiser:
            return Order.objects.filter(Q(merchandiser=loginuser.merchandiser),
                                        Q(status='NEW') | Q(status='SENT_FACTORY')).order_by('-created_date')
        elif loginuser.is_factory:
            return Order.objects.filter(Q(factory=loginuser.factory), Q(status='SENT_FACTORY')).order_by('-created_date')
        else:
            return Order.objects.filter(Q(status='NEW') | Q(status='SENT_FACTORY')).order_by('-created_date')

    def get_context_data(self, **kwargs):
        kwargs['listtype'] = 'new'
        return super().get_context_data(**kwargs)

# 订单列表-已确认(已确认状态)
@method_decorator([login_required], name='dispatch')
class OrderListConfrimed(ListView):
    model = Order
    ordering = ('-created_date', )
    context_object_name = 'orders'
    template_name = 'order_list.html'

    def get_queryset(self):
        loginuser = self.request.user
        if loginuser.is_merchandiser:
            return Order.objects.filter(Q(merchandiser=loginuser.merchandiser),
                                        Q(status='CONFIRMED'))
        elif loginuser.is_factory:
            return Order.objects.filter(Q(factory=loginuser.factory),
                                        Q(status='CONFIRMED'))
        else:
            return Order.objects.filter(status='CONFIRMED')

    def get_context_data(self, **kwargs):
        kwargs['listtype'] = 'confirmed'
        return super().get_context_data(**kwargs)


# 订单列表-已出货(已出货状态)
@method_decorator([login_required], name='dispatch')
class OrderListShipped(ListView):
    model = Order
    ordering = ('-created_date', )
    context_object_name = 'orders'
    template_name = 'order_list.html'

    def get_queryset(self):
        loginuser = self.request.user
        if loginuser.is_merchandiser:
            return Order.objects.filter(Q(merchandiser=loginuser.merchandiser),
                                        Q(status='SHIPPED'))
        elif loginuser.is_factory:
            return Order.objects.filter(Q(factory=loginuser.factory),
                                        Q(status='SHIPPED'))
        else:
            return Order.objects.filter(status='SHIPPED')

    def get_context_data(self, **kwargs):

        kwargs['listtype'] = 'shipped'
        # 待确认，应该type没有用到
        # kwargs['type'] = type
        return super().get_context_data(**kwargs)

# 订单列表-出货按周统计

@login_required
def ordershipbyweek(request, pk):

    loginuser = request.user

    today = date.today()
    day_of_week = today.weekday()
    to_beginning_of_week = datetime.timedelta(days=day_of_week)
    beginning_of_week = today - to_beginning_of_week

    to_end_of_week = datetime.timedelta(days=6 - day_of_week)
    end_of_week = today + to_end_of_week

    if pk==0:
        beginning_of_week = beginning_of_week + timedelta(days=0)
        end_of_week = end_of_week + timedelta(days=0)
    if pk==999:
        beginning_of_week = beginning_of_week + timedelta(days=-300*7)
        end_of_week = end_of_week - timedelta(days=7)
        # print(beginning_of_week)
        # print(end_of_week)
    if pk>0 and pk!=999:
        beginning_of_week = beginning_of_week + timedelta(days=pk*7)
        end_of_week = end_of_week + timedelta(days=pk*7)

    # print(end_of_week)

    if loginuser.is_merchandiser:
        orders = Order.objects.filter(merchandiser=loginuser.merchandiser, handover_date_f__range=(beginning_of_week,end_of_week), status='CONFIRMED')

    elif loginuser.is_factory:
        orders = Order.objects.filter(factory=loginuser.factory, handover_date_f__range=(beginning_of_week, end_of_week), status='CONFIRMED')
    else:
        orders = Order.objects.filter(handover_date_f__range=(beginning_of_week, end_of_week), status='CONFIRMED')
    
    pk_next = pk+1

    if pk>=1:
        pk_before = pk-1
    else:
        pk_before = 0

    return render(request, 'order_list.html', {'orders': orders, 'shipbyweek': 'shipbyweek', 'pk': pk, 'pk_before': pk_before, 'pk_next': pk_next, 'listtype':'confirmed'})


# 订单列表-本周出货
@method_decorator([login_required], name='dispatch')
class OrderListShipThisWeek(ListView):
    model = Order
    ordering = ('-created_date', )
    context_object_name = 'orders'
    template_name = 'order_list.html'

    def get_queryset(self):
        loginuser = self.request.user
        today = date.today()
        day_of_week = today.weekday()
        to_beginning_of_week = datetime.timedelta(days=day_of_week)
        beginning_of_week = today - to_beginning_of_week

        to_end_of_week = datetime.timedelta(days=6 - day_of_week)
        end_of_week = today + to_end_of_week
        # print(end_of_week)

        if loginuser.is_merchandiser:
            qs = Order.objects.filter(merchandiser=loginuser.merchandiser, handover_date_f__range=(beginning_of_week,end_of_week), status='CONFIRMED')
            return qs

        elif loginuser.is_factory:
            qs = Order.objects.filter(factory=loginuser.factory, handover_date_f__range=(beginning_of_week, end_of_week), status='CONFIRMED')
            return qs
        else:
            qs = Order.objects.filter(handover_date_f__range=(beginning_of_week, end_of_week), status='CONFIRMED')
            return qs
        
    def get_context_data(self, **kwargs):
        kwargs['listtype'] = 'confirmed'
        return super().get_context_data(**kwargs)



# 订单列表-下周出货
@method_decorator([login_required], name='dispatch')
class OrderListShipNextWeek(ListView):
    model = Order
    ordering = ('-created_date', )
    context_object_name = 'orders'
    template_name = 'order_list.html'

    def get_queryset(self):
        loginuser = self.request.user
        today = date.today()
        day_of_week = today.weekday()
        to_beginning_of_week = datetime.timedelta(days=day_of_week)
        beginning_of_week = today - to_beginning_of_week
        beginning_of_week = beginning_of_week + timedelta(days=7)
        # print(beginning_of_week)
        to_end_of_week = datetime.timedelta(days=6 - day_of_week)
        end_of_week = today + to_end_of_week
        end_of_week = end_of_week + timedelta(days=7)
        # print(end_of_week)

        if loginuser.is_merchandiser:
            qs = Order.objects.filter(merchandiser=loginuser.merchandiser, handover_date_f__range=(beginning_of_week,end_of_week), status='CONFIRMED')
            return qs

        elif loginuser.is_factory:
            qs = Order.objects.filter(factory=loginuser.factory, handover_date_f__range=(beginning_of_week, end_of_week), status='CONFIRMED')
            return qs
        else:
            qs = Order.objects.filter(handover_date_f__range=(beginning_of_week, end_of_week), status='CONFIRMED')
            return qs
        
    def get_context_data(self, **kwargs):
        kwargs['listtype'] = 'confirmed'
        return super().get_context_data(**kwargs)


# 订单列表-下下周出货
@method_decorator([login_required], name='dispatch')
class OrderListShipNextNextWeek(ListView):
    model = Order
    ordering = ('-created_date', )
    context_object_name = 'orders'
    template_name = 'order_list.html'

    def get_queryset(self):
        loginuser = self.request.user
        today = date.today()
        day_of_week = today.weekday()
        to_beginning_of_week = datetime.timedelta(days=day_of_week)
        beginning_of_week = today - to_beginning_of_week
        beginning_of_week = beginning_of_week + timedelta(days=14)
        # print(beginning_of_week)
        to_end_of_week = datetime.timedelta(days=6 - day_of_week)
        end_of_week = today + to_end_of_week
        end_of_week = end_of_week + timedelta(days=14)
        # print(end_of_week)

        if loginuser.is_merchandiser:
            qs = Order.objects.filter(merchandiser=loginuser.merchandiser, handover_date_f__range=(beginning_of_week,end_of_week), status='CONFIRMED')
            return qs

        elif loginuser.is_factory:
            qs = Order.objects.filter(factory=loginuser.factory, handover_date_f__range=(beginning_of_week, end_of_week), status='CONFIRMED')
            return qs
        else:
            qs = Order.objects.filter(handover_date_f__range=(beginning_of_week, end_of_week), status='CONFIRMED')
            return qs
        
    def get_context_data(self, **kwargs):
        kwargs['listtype'] = 'confirmed'
        return super().get_context_data(**kwargs)



# 订单新建
@method_decorator([login_required, m_mg_or_required], name='dispatch')
class OrderAdd(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'order_edit.html'

    def form_valid(self, form):
        order = form.save()
        messages.success(self.request, '订单创建成功!')
        return redirect('order:orderedit', pk=order.pk)

# 订单编辑
@method_decorator([login_required, order_is_shipped, m_mg_or_required], name='dispatch')
class OrderEdit(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'order_edit.html'
    context_object_name = 'order'

    def form_valid(self, form):
        order = form.save()
        return redirect('order:orderedit', pk=order.pk)

    def get_context_data(self, **kwargs):
        kwargs['date_allysize'] = datetime.datetime(2021, 8, 12)
        kwargs['swatches'] = self.get_object().swatches.all()
        kwargs['shippingpics'] = self.get_object().shippingpics.all()
        kwargs['sizespecs'] = self.get_object().sizespecs.all()
        kwargs['packingways'] = self.get_object().PPackingways.all()
        try:
            kwargs['colorqtys'] = self.get_object().colorqtys.all().order_by('-created_date')
        except ObjectDoesNotExist:
            pass
        try:
            kwargs['barcode'] = self.get_object().barcode
        except ObjectDoesNotExist:
            pass
        return super().get_context_data(**kwargs)


# 订单详情，工厂查看页面
@login_required
def orderdetail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    date_allysize = datetime.datetime(2021, 8, 12)
    swatches = order.swatches.all()
    sizespecs = order.sizespecs.all()
    shippingpics = order.shippingpics.all()
    packingways = order.PPackingways.all()
    colorqtys = order.colorqtys.all().order_by('-created_date')
    try:
        barcode = order.barcode
    except ObjectDoesNotExist:
        barcode = None
    return render(request, 'order_detail.html', {'order': order, 'date_allysize':date_allysize, 'swatches': swatches,
                                                 'sizespecs': sizespecs, 'shippingpics': shippingpics,
                                                 'colorqtys': colorqtys, 'barcode': barcode, 'packingways': packingways})

#订单包装方式增加
@login_required
@m_mg_or_required
def packingwayadd(request, pk):
    packingwayselected = {}
    order = get_object_or_404(Order, pk=pk)
    orderpackingways = order.PPackingways.all()
    orderpackingways = orderpackingways.values_list('pk', flat=True)
    packingways = PPackingway.objects.all()
    if request.method == 'POST':
            packingwayselected = request.POST.getlist('packingwaypk')
            packingwaylist = PPackingway.objects.in_bulk(packingwayselected)
            order.PPackingways.clear()
            for packingway in packingwaylist:
                order.PPackingways.add(packingway)
                order.save()
            return redirect('order:orderedit', pk=order.pk)
    return render(request, 'packingway_add.html', {'packingways': packingways, 'order': order, 'orderpackingways': orderpackingways})


# 订单颜色数量新增
@login_required
@m_mg_or_required
def colorqtyadd(request, pk):
    date_allysize = datetime.datetime(2021, 8, 12)
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = Order_color_ratio_qty_Form(request.POST)
        if form.is_valid():
            colorqty = form.save(commit=False)
            colorqty.order = order
            colorqty.save()
            return redirect('order:colorqtyadd', pk=order.pk)
    else:
        form = Order_color_ratio_qty_Form()
    return render(request, 'colorqty_add.html', {'form': form, 'order': order, 'date_allysize': date_allysize})


# 订单颜色数量更改
@login_required
@m_mg_or_required
def colorqtyedit(request, pk, colorqtypk):
    order = get_object_or_404(Order, pk=pk)
    date_allysize = datetime.datetime(2021, 8, 12)
    colorqty = get_object_or_404(Order_color_ratio_qty, pk=colorqtypk)
    if request.method == 'POST':
        form = Order_color_ratio_qty_Form(request.POST, instance=colorqty)
        if form.is_valid():
            colorqty = form.save(commit=False)
            colorqty.order = order
            colorqty.save()
            return redirect('order:orderedit', pk=order.pk)
    else:
        form = Order_color_ratio_qty_Form(instance=colorqty)
    return render(request, 'colorqty_add.html', {'form': form, 'order': order, 'date_allysize': date_allysize})


# 订单颜色数量删除
@login_required
@m_mg_or_required
def colorqtydelete(request, pk, colorqtypk):
    order = get_object_or_404(Order, pk=pk)
    colorqty = get_object_or_404(Order_color_ratio_qty, pk=colorqtypk)
    colorqty.delete()
    return redirect('order:orderedit', pk=order.pk)


# 删除订单
@method_decorator([login_required, m_mg_or_required], name='dispatch')
class OrderDelete(DeleteView):
    model = Order
    context_object_name = 'order'
    template_name = 'order_delete.html'

    def get_success_url(self):
        order = self.get_object()
        if order.status == 'NEW' or order.status == 'SENT_FACTORY':
            success_url = reverse_lazy('order:orderlistnew')
            return success_url
        elif order.status == 'CONFIRMED':
            success_url = reverse_lazy('order:orderlistconfirmed')
            return success_url
        else:
            success_url = reverse_lazy('order:orderlistshipped')
            return success_url


# 拷贝订单，测试数据用
# @login_required
# @m_mg_or_required
# def ordercopy(request, pk):
#     order = get_object_or_404(Order, pk=pk)
#     order.pk = None
#     order.save()
#     return redirect('order:orderedit', pk=order.pk)


# 改变订单状态到送工厂状态
@login_required
@m_mg_or_required
def ordersentfactory(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.factory is None:
        messages.warning(request, '请选择工厂并保存后，才能通知工厂!')
    else:
        order.status = "SENT_FACTORY"
        order.save()
        messages.success(request, '订单已经安排给工厂!')
        factoryemail = str(order.factory.email)
        try:
            avatar_file = order.avatar.file
            encoded = base64.b64encode(open(avatar_file.path, "rb").read()).decode()
        except ObjectDoesNotExist:
            encoded = ''
        sender_email = 'SCM@monayoung.com.au'
        receiver_email = factoryemail
        message = MIMEMultipart("alternative")
        message["Subject"] = "缘色SCM-新订单通知"
        message["From"] = sender_email
        message["To"] = receiver_email
        orderpo = order.po
        orderstyleno = order.style_no
        brand = order.brand.name
        merchandiser = order.merchandiser.user.username
        html = f"""\
            <html>
            <body>
            <h3>新订单已经安排给工厂,详细信息请看SCM！</h3>
            <h3>订单号:{orderpo}</h3>
            <h3>款号:{orderstyleno}</h3>
            <h3>品牌:{brand}</h3>
            <h3>跟单:{merchandiser}</h3>
            <h3>图片:</h3>
            <img src="data:image/jpg;base64,{encoded}" width=200px height=200px>
            </body>
            </html>
            """
        part = MIMEText(html, "html")
        message.attach(part)
        with smtplib.SMTP(config('EMAIL_HOST'), config('EMAIL_PORT', cast=int)) as server:
            server.login(config('EMAIL_HOST_USER'), config('EMAIL_HOST_PASSWORD'))
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
    return redirect('order:orderedit', pk=order.pk)


# 订单确认
@login_required
@factory_required
def orderconfirm(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = "CONFIRMED"
    order.save()
    messages.success(request, '已确认订单, 请在确认订单列表查找!')
    return redirect('order:orderdetail', pk=order.pk)


# 订单出货
@login_required
@o_m_mg_or_required
def ordershipped(request, pk):
    order = get_object_or_404(Order, pk=pk)
    packing_ctns = order.packing_ctns.annotate(sumtotalqty=F('totalboxes')*F('totalqty'))
    totalqty = packing_ctns.aggregate(totalqty=Sum('sumtotalqty', output_field=IntegerField()))
    totalqty = totalqty.get('totalqty') or 0
    order.actual_ship_qty = totalqty
    order.status = "SHIPPED"
    order.save()
    messages.success(request, '订单已出货, 请在出货订单列表查找!')
    return redirect('order:orderedit', pk=order.pk)

# 订单重置
@login_required
@m_mg_or_required
def orderreset(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = "NEW"
    order.save()
    messages.success(request, '订单已重置到新建状态!')
    return redirect('order:orderedit', pk=order.pk)


# 订单附件通用功能视图
@login_required
def orderattachadd(request, pk, attachtype):
    order = get_object_or_404(Order, pk=pk)
    if attachtype == 'avatar':
        if request.FILES:
            try:
                order.avatar.delete()
            except ObjectDoesNotExist:
                pass
            form = OrderavatarForm(request.POST, request.FILES)
    elif attachtype == 'barcode':
        if request.FILES:
            try:
                order.barcode.delete()
            except ObjectDoesNotExist:
                pass
            form = OrderbarcodeForm(request.POST, request.FILES)
    elif attachtype == 'sizespecs':
        form = OrdersizespecsForm(request.POST, request.FILES)
    elif attachtype == 'swatch':
        form = OrderswatchForm(request.POST, request.FILES)
    else:
        form = OrdershippingpicsForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            with transaction.atomic():
                attach = form.save(commit=False)
                attach.order = order
                attach.save()
                data = {"files": [{
                            "name": attach.file.name,
                            "url": attach.file.url, },
                            ]}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)
    else:
        return render(request, 'order_attach_add.html', {'order': order, 'attachtype': attachtype})

# 上传发票
@login_required
@factory_required
def invoiceattachadd(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES, instance=invoice)
        if request.FILES:
            try:
                invoice.file.delete()
            except ObjectDoesNotExist:
                pass
        if form.is_valid():
            invoice = form.save()
            data = {"files": [{
                        "name": invoice.file.name,
                        "url": invoice.file.url, },
                        ]}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)
    else:
        return render(request, 'invoice_attach_add.html', {'invoice': invoice})

# 订单附件删除
@login_required
def orderattachdelete(request, pk, attachtype, attach_pk):
    order = get_object_or_404(Order, pk=pk)
    attachtype = attachtype
    if attachtype == 'avatar':
        attach = get_object_or_404(Order_avatar, pk=attach_pk)
        attach.delete()
        return redirect('order:orderedit', pk=order.pk)
    elif attachtype == 'barcode':
        attach = get_object_or_404(Order_Barcode, pk=attach_pk)
        attach.delete()
        return redirect('order:orderedit', pk=order.pk)
    elif attachtype == 'swatch':
        attach = get_object_or_404(Order_swatches, pk=attach_pk)
        attach.delete()
        return redirect('order:orderattachcollection', pk=order.pk, attachtype=attachtype)
    elif attachtype == 'sizespecs':
        attach = get_object_or_404(Order_size_specs, pk=attach_pk)
        attach.delete()
        return redirect('order:orderedit', pk=order.pk)
    elif attachtype == 'swatch':
        attach = get_object_or_404(Order_swatches, pk=attach_pk)
        attach.delete()
        return redirect('order:orderattachcollection', pk=order.pk, attachtype=attachtype)
    else:
        attach = get_object_or_404(Order_shipping_pics, pk=attach_pk)
        attach.delete()
        return redirect('order:orderattachcollection', pk=order.pk, attachtype=attachtype)

# 订单附件集
@login_required
def orderattachcollection(request, pk, attachtype):
    order = get_object_or_404(Order, pk=pk)
    attachtype = attachtype
    if attachtype == 'swatch':
        attaches = order.swatches.all()
    else:
        attaches = order.shippingpics.all()
    return render(request, 'order_attach_collection.html', {'order': order,
                  'attachtype': attachtype, 'attaches': attaches})


# 装箱单查找，暂时不用，供今后参考
# def plsearch(request):
#     loginuser = request.user
#     if loginuser.is_factory:
#         factory = loginuser.factory
#         order_list = Order.objects.filter(Q(factory=factory), Q(status='CONFIRMED') | Q(status='SHIPPED'))
#     else:
#         order_list = Order.objects.filter(Q(status='CONFIRMED') | Q(status='SHIPPED'))
#     order_filter = OrderFilter(request.GET, queryset=order_list)
#     return render(request, 'plsearch_list.html', {'filter': order_filter})


# 获取实际出货数量
def getacutalcolorqty(pk):
    actualorderqty = []
    colorobject = {}
    order = get_object_or_404(Order, pk=pk)
    colors = order.colorqtys.all()
    if order.packing_type.shortname == '单件包装':
        for color in colors:
            # 单件包装不用中包,但是可以放到模板里做判断，这样不用写2套模板
            qty = color.packing_ctns.annotate(sumtotalqty=F('totalboxes')*F('totalqty'),
                                              sumsize1=F('totalboxes')*F('size1'),
                                              sumsize2=F('totalboxes')*F('size2'),
                                              sumsize3=F('totalboxes')*F('size3'),
                                              sumsize4=F('totalboxes')*F('size4'),
                                              sumsize5=F('totalboxes')*F('size5'),
                                              sumsize6=F('totalboxes')*F('size6'),
                                              )
            qty = qty.aggregate(totalbags=Sum('bags'), size1=Sum('sumsize1'),
                                               size2=Sum('sumsize2'), size3=Sum('sumsize3'),
                                               size4=Sum('sumsize4'), size5=Sum('sumsize5'),
                                               size6=Sum('sumsize6'),
                                               totalqty=Sum('sumtotalqty'))
            colorobject = {'color': color, 'qty': qty}
            actualorderqty.append(colorobject)
    else:
        for color in colors:
            qty = color.packing_ctns.annotate(sumtotalqty=F('totalboxes')*F('totalqty'),
                                              eachitemtotalbags=F('bags')*F('totalboxes'),
                                              sumsize1=F('totalboxes')*F('size1'),
                                              sumsize2=F('totalboxes')*F('size2'),
                                              sumsize3=F('totalboxes')*F('size3'),
                                              sumsize4=F('totalboxes')*F('size4'),
                                              sumsize5=F('totalboxes')*F('size5'),
                                              sumsize6=F('totalboxes')*F('size6'),
                                              )
            qty = qty.aggregate(totalbags=Sum('eachitemtotalbags'), size1=Sum('sumsize1'),
                                size2=Sum('sumsize2'), size3=Sum('sumsize3'), size4=Sum('sumsize4'), size5=Sum('sumsize5'), size6=Sum('sumsize6'),
                                totalqty=Sum('sumtotalqty'))
            colorobject = {'color': color, 'qty': qty}
            actualorderqty.append(colorobject)
    return actualorderqty


# 创建装箱单----创建前检查状态，如果已经提交回到详情页
@login_required
@packinglist_is_sented
def packinglistadd(request, pk):
    order = get_object_or_404(Order, pk=pk)
    date_allysize = datetime.datetime(2021, 8, 12)
    form = OrderpackingctnForm(request.POST, order=order)
    colorqtys = order.colorqtys.all()
    gross_weight = order.packing_status.gross_weight
    packing_ctns = order.packing_ctns.all()
    packing_ctns = packing_ctns.annotate(gross_weight=F('totalboxes')*gross_weight, sumtotalqty=F('totalboxes')*F('totalqty'))
    orderctnsum = order.packing_ctns.annotate(eachitemtotalbags=F('bags')*F('totalboxes'),
                                              sumtotalqty=F('totalboxes')*F('totalqty'),
                                              gross_weight=F('totalboxes')*gross_weight)
    orderctnsum = orderctnsum.aggregate(totalbags=Sum('eachitemtotalbags'), size1=Sum('size1'),
                                        size2=Sum('size2'), size3=Sum('size3'), size4=Sum('size4'), size5=Sum('size5'), size6=Sum('size6'),
                                        totalqty=Sum('sumtotalqty'))
    # packing_ctns_exclude_share = order.packing_ctns.filter(sharebox=False) ALLY增加尾箱后统计不对，改为全部箱数统计
    # packing_ctns_exclude_share = order.packing_ctns.all()
    packing_ctns_exclude_share = order.packing_ctns.filter(sharebox=False)
    packing_ctns_exclude_share_grossweight = packing_ctns_exclude_share.annotate(gross_weight=F('totalboxes')*gross_weight)
    totalgrossweight = packing_ctns_exclude_share_grossweight.aggregate(totalgrossweight=Sum('gross_weight'))
    totalgrossweight = totalgrossweight['totalgrossweight']
    totalboxes = packing_ctns_exclude_share.aggregate(totalboxes=Sum('totalboxes'))
    totalboxes = totalboxes['totalboxes']
    actualqty = getacutalcolorqty(order.pk)
    if request.method == 'POST':
        if form.is_valid():
            packinglist = form.save(commit=False)
            packinglist.order = order
            packinglist.save()
        return redirect('order:packinglistadd', pk=order.pk)
    else:
        form = OrderpackingctnForm(order=order)
    return render(request, 'packinglist_add.html', {'form': form,
                                                    'colorqtys': colorqtys,
                                                    'order': order,
                                                    'date_allysize': date_allysize,
                                                    'packing_ctns': packing_ctns,
                                                    'orderctnsum': orderctnsum,
                                                    'actualqty': actualqty,
                                                    'totalboxes': totalboxes,
                                                    'totalgrossweight': totalgrossweight})


# 提交装箱单
@login_required
@factory_required
def packinglistsubmit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    packing_status = order.packing_status

    # 获取颜色
    colors = order.colorqtys.all()
    for color in colors:
        # 红色数量
        colorqty = color.qty
        # 红色所有箱对象
        colorboxqs = Order_packing_ctn.objects.filter(color=color)
        if colorboxqs.exists():
            # 每个对象加汇总字段
            colorboxqs = colorboxqs.annotate(sumtotalqty=F('totalboxes')*F('totalqty'))
            # 汇总所有对象总件数等于实际颜色的件数
            actualqty = colorboxqs.aggregate(colortotalpcs=Sum('sumtotalqty', output_field=IntegerField()))
            # 取值
            actualqty = actualqty['colortotalpcs']
            # vg
            if order.brand.name in ['Valleygirl','MIRROU']:
                if colorqty in range(401):
                    accepted = actualqty in range(int(colorqty*0.9), int(colorqty*1.1) + 1)
                    if not accepted:
                        messages.warning(request, '每个颜色的订单数小于400件，只能接受正负10%!')
                        return redirect('order:packinglistadd', pk=order.pk)
                else:
                    accepted = actualqty in range(int(colorqty*0.95), int(colorqty*1.05) + 1)
                    if not accepted:
                        messages.warning(request, '每个颜色的订单数大于400件，只能接受正负5%，最多接受50件!')
                        return redirect('order:packinglistadd', pk=order.pk)
                    else:
                        if (actualqty > colorqty + 50):
                            messages.warning(request, '每个颜色的订单数大于400件，只能接受正负5%，最多接受50件!')
                            return redirect('order:packinglistadd', pk=order.pk)
            # ally
            if order.brand.name in ['Ally（minx & moss）','Ally']:
                if order.order_type == 'WEBORDER':
                    accepted = actualqty in range(int(colorqty*0.9), int(colorqty*1.1) + 1)
                    if not accepted:
                        messages.warning(request, 'ALLY网单出货数，只接受正负10%!')
                        return redirect('order:packinglistadd', pk=order.pk)
                else:
                    accepted = actualqty in range(int(colorqty*0.95), int(colorqty*1.05) + 1)
                    if not accepted:
                        messages.warning(request, 'ALLY店铺单出货数，只接受正负5%!')
                        return redirect('order:packinglistadd', pk=order.pk)
            # you+all
            if order.brand.name in ['You+All']:
                if order.order_type == 'WEBORDER':
                    accepted = actualqty in range(int(colorqty*0.9), int(colorqty*1.1) + 1)
                    if not accepted:
                        messages.warning(request, 'You+All网单出货数，只接受正负10%!')
                        return redirect('order:packinglistadd', pk=order.pk)
                else:
                    accepted = actualqty in range(int(colorqty*0.9), int(colorqty*1.1) + 1)
                    if not accepted:
                        messages.warning(request, 'You+All店铺单出货数，只接受正负10%!')
                        return redirect('order:packinglistadd', pk=order.pk)
            # 其他订单，暂时不做限制
            # else:
            #     accepted = actualqty in range(int(colorqty*0.95), int(colorqty*1.05) + 1)
            #     if not accepted:
            #         messages.warning(request, '订单出货数，只接受正负5%!')
            #         return redirect('order:packinglistadd', pk=order.pk)
        else:
            messages.warning(request, "{}没有添加装箱单.".format(color.color_cn))
            return redirect('order:packinglistadd', pk=order.pk)
    packing_status.status = 'SUBMIT'
    packing_status.save()
    # 发邮件，发跟单和行政
    office_emails = User.objects.filter(is_office=True).values_list('email', flat=True)
    office_emails = list(office_emails)

    try:
        avatar_file = order.avatar.file
        encoded = base64.b64encode(open(avatar_file.path, "rb").read()).decode()
    except ObjectDoesNotExist:
        encoded = ''
    sender_email = 'SCM@monayoung.com.au'
    message = MIMEMultipart("alternative")
    message["Subject"] = "缘色SCM-装箱单提交！"
    message["From"] = sender_email
    orderpo =  order.po
    orderstyleno =  order.style_no
    brand = order.brand.name
    factory = order.factory.user.username
    html = f"""\
        <html>
        <body>
        <h3>订单装箱单已提交！</h3>
        <h3>订单号:{orderpo}</h3>
        <h3>款号:{orderstyleno}</h3>
        <h3>品牌:{brand}</h3>
        <h3>工厂:{factory}</h3>
        <h3>图片:</h3>
        <img src="data:image/jpg;base64,{encoded}" width=200px height=200px>
        </body>
        </html>
        """
    part = MIMEText(html, "html")
    message.attach(part)
    with smtplib.SMTP(config('EMAIL_HOST'), config('EMAIL_PORT', cast=int)) as server:
        server.login(config('EMAIL_HOST_USER'), config('EMAIL_HOST_PASSWORD'))
        for email in office_emails:
            message["To"] = email
            server.sendmail(
                sender_email, email, message.as_string()
            )

    return redirect('order:packinglistdetail', pk=order.pk)


# 删除装箱单
@login_required
@factory_required
def packinglistdelete(request, pk, plpk):
    order = get_object_or_404(Order, pk=pk)
    plctn = get_object_or_404(Order_packing_ctn, pk=plpk)
    plctn.delete()
    return redirect('order:packinglistadd', pk=order.pk)


# 装箱单详情
@login_required
def packinglistdetail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    date_allysize = datetime.datetime(2021, 8, 12)
    colorqtys = order.colorqtys.all()
    gross_weight = order.packing_status.gross_weight
    packing_ctns = order.packing_ctns.all()
    packing_ctns = packing_ctns.annotate(gross_weight=F('totalboxes')*gross_weight, sumtotalqty=F('totalboxes')*F('totalqty'))
    orderctnsum = order.packing_ctns.annotate(eachitemtotalbags=F('bags')*F('totalboxes'),
                                              sumtotalqty=F('totalboxes')*F('totalqty'),
                                              gross_weight=F('totalboxes')*gross_weight)
    orderctnsum = orderctnsum.aggregate(totalbags=Sum('eachitemtotalbags'), size1=Sum('size1'),
                                        size2=Sum('size2'), size3=Sum('size3'), size4=Sum('size4'), size5=Sum('size5'), size6=Sum('size6'),
                                        totalqty=Sum('sumtotalqty'))
    # packing_ctns_exclude_share = order.packing_ctns.filter(sharebox=False) ALLY增加尾箱后统计不对，改为全部箱数统计
    packing_ctns_exclude_share = order.packing_ctns.filter(sharebox=False)
    # packing_ctns_exclude_share = order.packing_ctns.all()
    packing_ctns_exclude_share_grossweight = packing_ctns_exclude_share.annotate(gross_weight=F('totalboxes')*gross_weight)
    totalgrossweight = packing_ctns_exclude_share_grossweight.aggregate(totalgrossweight=Sum('gross_weight'))
    totalgrossweight = totalgrossweight['totalgrossweight']
    totalboxes = packing_ctns_exclude_share.aggregate(totalboxes=Sum('totalboxes'))
    totalboxes = totalboxes['totalboxes']
    actualqty = getacutalcolorqty(order.pk)

    return render(request, 'packinglist_detail.html', {'order': order,
                                                       'date_allysize': date_allysize,
                                                       'colorqtys': colorqtys,
                                                       'packing_ctns': packing_ctns,
                                                       'actualqty': actualqty,
                                                       'orderctnsum': orderctnsum,
                                                       'totalboxes': totalboxes,
                                                       'totalgrossweight': totalgrossweight})

# 确认装箱单
@login_required
@o_m_mg_or_required
def packinglistclose(request, pk):
    order = get_object_or_404(Order, pk=pk)
    packing_status = order.packing_status
    packing_status.status = 'CLOSED'
    packing_status.save()
    return redirect('order:packinglistdetail', pk=order.pk)


# 重置装箱单
@login_required
@o_m_mg_or_required

def packinglistreset(request, pk):
    order = get_object_or_404(Order, pk=pk)
    packing_status = order.packing_status
    packing_status.status = 'NEW'
    packing_status.save()
    return redirect('order:packinglistadd', pk=order.pk)


# 修改纸箱规格
@method_decorator([login_required, factory_required], name='dispatch')
class Update_packingstatus(UpdateView):
    model = Order_packing_status
    form_class = OrderpackingstatusForm
    template_name = 'order_update_packingstatus.html'
    context_object_name = 'packingstatus'

    def form_valid(self, form):
        packingstatus = form.save()
        return redirect('order:packinglistadd', pk=packingstatus.pk)

    def get_context_data(self, **kwargs):
        kwargs['order'] = self.get_object().order
        return super().get_context_data(**kwargs)


# 查订单比列
def getratio(request):
    date_allysize = datetime.datetime(2021, 8, 12)
    colorratio_pk = request.GET.get('color', None)
    colorratio = get_object_or_404(Order_color_ratio_qty, pk=colorratio_pk)
    order = colorratio.order
    if order.packing_type.shortname == '单件包装':
        packing_type = 1
        ratiolist = []
    else:
        packing_type = 2
        ratio = colorratio.ratio
        ratiolist = ratio.split(":")
        ratiolist = list(map(int, ratiolist))
        if (order.created_date.replace(tzinfo=None)  -  date_allysize.replace(tzinfo=None)).days < 1:
            ratiolist = ratiolist + [0]
    data = {
        'ratio': ratiolist
    }
    data['packing_type'] = packing_type
    return JsonResponse(data)


# 发票号递增规则
def increment_invoice_number():
    last_invoice = Invoice.objects.all().order_by('id').last()
    if not last_invoice:
        return '000001'
    invoice_no = last_invoice.invoice_no
    invoice_no_new = invoice_no[9:]
    new_invoice_no = str(int(invoice_no_new) + 1)
    new_invoice_no = invoice_no_new[0:-(len(new_invoice_no))] + new_invoice_no
    return new_invoice_no

# 创建发票
@login_required
@factory_required
def invoiceadd(request):
    qs = []
    orderlist = {}
    totalpaidamount = 0
    orderpklist = request.POST.getlist('orderpk')
    if not orderpklist:
        return redirect('order:invoicelist')
    else:
        orderlist = Order.objects.in_bulk(orderpklist)
        orderlist = orderlist.values()
        datelist = [order.handover_date_f for order in orderlist]
        mindate = min(datelist)
        maxdate = max(datelist)
        start_of_week = mindate - timedelta(days=mindate.weekday())   # 周一
        end_of_week = start_of_week + timedelta(days=6)   # 周日

        # start_of_week  = mindate.replace(day=1)
        # end_of_week = mindate.replace(day=calendar.monthrange(mindate.year, mindate.month)[1])


        new_invoiceno = increment_invoice_number()
        if maxdate >= start_of_week and maxdate <= end_of_week:
            invoiceno = mindate.strftime("%Y%m%d") + '_' + new_invoiceno
            factory = request.user.factory
            invoice = Invoice.objects.create(invoice_no=invoiceno, factory=factory,
                                             handoverdate=mindate, start_of_week=start_of_week,
                                             end_of_week=end_of_week)
            for order in orderlist:
                # totalqty = order.packing_ctns.aggregate(totalqty=Sum('totalqty', output_field=IntegerField()))
                # totalqty = totalqty.get('totalqty') or 0
                factory_price = order.factory_price or 0
                paidamount = order.actual_ship_qty * factory_price
                totalpaidamount = totalpaidamount + paidamount
                orderobject = {'order': order, 'paidamount': paidamount}
                qs.append(orderobject)
                order.invoice = invoice
                order.save()
        else:
            messages.warning(request, '请把同一周出货的订单创建在一张发票里！')
            return redirect('order:invoicelist')

    return render(request, 'invoice_detail.html', {'qs': qs, 'invoice': invoice, 'factory': factory, 'totalpaidamount': totalpaidamount})


# 删除发票
@login_required
@factory_required
def invoicedelete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    Order.objects.filter(invoice=invoice).update(invoice=None)
    return redirect('order:invoicelist')


# 发票详情页
@login_required
@f_f_mg_or_required
def invoicedetail(request, pk):
    qs = []
    totalpaidamount = 0
    invoice = get_object_or_404(Invoice, pk=pk)
    orderqs = Order.objects.filter(invoice=invoice)
    factory = invoice.factory
    for order in orderqs:
        # totalqty = order.packing_ctns.aggregate(totalqty=Sum('totalqty', output_field=IntegerField()))
        # totalqty = totalqty.get('totalqty') or 0
        factory_price = order.factory_price or 0
        paidamount = order.actual_ship_qty * factory_price
        totalpaidamount = totalpaidamount + paidamount
        orderobject = {'order': order, 'paidamount': paidamount}
        qs.append(orderobject)
    return render(request, 'invoice_detail.html', {'qs': qs, 'invoice': invoice, 'factory': factory, 'totalpaidamount': totalpaidamount})


# 发票列表
@login_required
@f_f_mg_or_required
def invoicelist(request):
    loginuser = request.user
    if loginuser.is_factory:
        invoiceqs = Invoice.objects.filter(factory=loginuser.factory)
        orderqs = Order.objects.filter(Q(factory=loginuser.factory), Q(status='SHIPPED'), Q(invoice=None))
        return render(request, 'invoice_list.html',  {'invoiceqs': invoiceqs, 'orderqs': orderqs})
    else:
        if request.method == 'POST':
            if request.POST.get('start_handover_date_f') and request.POST.get('end_handover_date_f') and request.POST.get('factory'):
                form = InvoiceSearchForm(request.POST)
                if form.is_valid():
                    factory = form.cleaned_data['factory']
                    start_handover_date_f = form.cleaned_data['start_handover_date_f']
                    end_handover_date_f = form.cleaned_data['end_handover_date_f']
                    invoiceqs = Invoice.objects.filter(factory=factory, handoverdate__range=(start_handover_date_f, end_handover_date_f))
            elif request.POST.get('start_handover_date_f') and request.POST.get('end_handover_date_f'):
                form = InvoiceSearchForm(request.POST)
                if form.is_valid():
                    start_handover_date_f = form.cleaned_data['start_handover_date_f']
                    end_handover_date_f = form.cleaned_data['end_handover_date_f']
                    invoiceqs = Invoice.objects.filter(handoverdate__range=(start_handover_date_f, end_handover_date_f))
            elif request.POST.get('factory'):
                form = InvoiceSearchForm(request.POST)
                if form.is_valid():
                    factory = form.cleaned_data['factory']
                    invoiceqs = Invoice.objects.filter(factory=factory)
            else:
                messages.warning(request, '请选择开始和结束工厂入仓日期！')
                return redirect('order:invoicelist')
            orderqs = Order.objects.filter(Q(status='SHIPPED'), Q(invoice=None))
        else:
            form = InvoiceSearchForm()
            invoiceqs = Invoice.objects.filter()
            orderqs = Order.objects.filter(Q(status='SHIPPED'), Q(invoice=None))
        return render(request, 'invoice_list.html',  {'invoiceqs': invoiceqs, 'orderqs': orderqs, 'form': form})


# 发票已付款
def invoicepay(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status = 'PAID'
    invoice.save()
    return redirect('order:invoicelist')


# 发票重置
def invoicereset(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status = 'NEW'
    invoice.save()
    return redirect('order:invoicelist')

# 生产板进度增加
def fittingsample(request, pk):
    pk = pk
    data = dict()
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderfittingsampleForm(request.POST)
        if form.is_valid():
            fittingsample = form.save(commit=False)
            fittingsample.order = order
            fittingsample.save()
            data['form_is_valid'] = True
            qs = order.fittingsamples.all().order_by('-created_date')
            data['html_fs_list'] = render_to_string('fs_list.html', {'qs': qs})
        else:
            data['form_is_valid'] = False
    else:
        form = OrderfittingsampleForm()
    context = {'form': form, 'pk': pk}
    data['html_form'] = render_to_string('fs_create_form.html',
                                         context,
                                         request=request)
    data['pk'] = pk
    return JsonResponse(data)


# 生产板进度删除
def fsdelete(request, pk):
    data = dict()
    fs = get_object_or_404(Order_fitting_sample, pk=pk)
    order = fs.order
    pk = order.pk
    fs.delete()
    qs = order.fittingsamples.all().order_by('-created_date')
    data['form_is_valid'] = True
    data['html_fs_list'] = render_to_string('fs_list.html', {'qs': qs})
    data['pk'] = pk
    return JsonResponse(data)


# 显示全部生产办进度
def fsall(request, pk):
    data = dict()
    order = get_object_or_404(Order, pk=pk)
    qs = order.fittingsamples.all().order_by('-created_date')
    data['form_is_valid'] = True
    data['html_fs_list'] = render_to_string('fs_list_all.html', {'qs': qs})
    data['pk'] = pk
    return JsonResponse(data)


# 只显示最近3个生产办进度
def fsthree(request, pk):
    data = dict()
    order = get_object_or_404(Order, pk=pk)
    qs = order.fittingsamples.all().order_by('-created_date')
    data['form_is_valid'] = True
    data['html_fs_list'] = render_to_string('fs_list.html', {'qs': qs})
    data['pk'] = pk
    return JsonResponse(data)

# 显示全部pr进度
def prall(request, pk):
    data = dict()
    order = get_object_or_404(Order, pk=pk)
    qs = order.productions.all().order_by('-created_date')
    data['form_is_valid'] = True
    data['html_pr_list'] = render_to_string('pr_list_all.html', {'qs': qs})
    data['pk'] = pk
    return JsonResponse(data)


# 只显示最近3个pr进度
def prthree(request, pk):
    data = dict()
    order = get_object_or_404(Order, pk=pk)
    qs = order.productions.all().order_by('-created_date')
    data['form_is_valid'] = True
    data['html_pr_list'] = render_to_string('pr_list.html', {'qs': qs})
    data['pk'] = pk
    return JsonResponse(data)

# 生产板进度修改
def fsedit(request, pk):
    data = dict()
    fs = get_object_or_404(Order_fitting_sample, pk=pk)
    order = fs.order
    pk = order.pk
    if request.method == 'POST':
        form = OrderfittingsampleForm(request.POST, instance=fs)
        if form.is_valid():
            form.save()
            qs = order.fittingsamples.all().order_by('-created_date')
            data['form_is_valid'] = True
            data['html_fs_list'] = render_to_string('fs_list.html', {'qs': qs})
        else:
            data['form_is_valid'] = False
    else:
        form = OrderfittingsampleForm(instance=fs)
    context = {'form': form, 'pk': fs.pk}
    data['html_form'] = render_to_string('fs_edit_form.html',
                                         context,
                                         request=request)
    data['pk'] = pk
    return JsonResponse(data)


# 大货布进度增加
def bulkfabric(request, pk):
    pk = pk
    data = dict()
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderbulkfabricForm(request.POST)
        if form.is_valid():
            bulkfabric = form.save(commit=False)
            bulkfabric.order = order
            bulkfabric.save()
            data['form_is_valid'] = True
            qs = order.bulkfabrics.all().order_by('-created_date')
            data['html_bf_list'] = render_to_string('bf_list.html', {'qs': qs})
        else:
            data['form_is_valid'] = False
    else:
        form = OrderbulkfabricForm()
    context = {'form': form, 'pk': pk}
    data['html_form'] = render_to_string('bf_create_form.html',
                                         context,
                                         request=request)
    data['pk'] = pk
    return JsonResponse(data)


# 大货布进度删除
def bfdelete(request, pk):
    data = dict()
    bf = get_object_or_404(Order_bulk_fabric, pk=pk)
    order = bf.order
    pk = order.pk
    bf.delete()
    qs = order.bulkfabrics.all().order_by('-created_date')
    data['form_is_valid'] = True
    data['html_bf_list'] = render_to_string('bf_list.html', {'qs': qs})
    data['pk'] = pk
    return JsonResponse(data)


# 大货布进度修改
def bfedit(request, pk):
    data = dict()
    bf = get_object_or_404(Order_bulk_fabric, pk=pk)
    order = bf.order
    pk = order.pk
    if request.method == 'POST':
        form = OrderbulkfabricForm(request.POST, instance=bf)
        if form.is_valid():
            form.save()
            qs = order.bulkfabrics.all().order_by('-created_date')
            data['form_is_valid'] = True
            data['html_bf_list'] = render_to_string('bf_list.html', {'qs': qs})
        else:
            data['form_is_valid'] = False
    else:
        form = OrderbulkfabricForm(instance=bf)
    context = {'form': form, 'pk': bf.pk}
    data['html_form'] = render_to_string('bf_edit_form.html',
                                         context,
                                         request=request)
    data['pk'] = pk
    return JsonResponse(data)


# 船头板进度增加
def shippingsample(request, pk):
    pk = pk
    data = dict()
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrdershippingsampleForm(request.POST)
        if form.is_valid():
            shippingsample = form.save(commit=False)
            shippingsample.order = order
            shippingsample.save()
            data['form_is_valid'] = True
            qs = order.shippingsamples.all().order_by('-created_date')
            data['html_ss_list'] = render_to_string('ss_list.html', {'qs': qs})
        else:
            data['form_is_valid'] = False
    else:
        form = OrdershippingsampleForm()
    context = {'form': form, 'pk': pk}
    data['html_form'] = render_to_string('ss_create_form.html',
                                         context,
                                         request=request)
    data['pk'] = pk
    return JsonResponse(data)




# 大货进度增加
def production(request, pk):
    pk = pk
    data = dict()
    order = get_object_or_404(Order, pk=pk)
    print(order)
    if request.method == 'POST':
        form = OrderproductionForm(request.POST)
        if form.is_valid():
            production = form.save(commit=False)
            production.order = order
            production.save()
            data['form_is_valid'] = True
            qs = order.productions.all().order_by('-created_date')
            data['html_pr_list'] = render_to_string('pr_list.html', {'qs': qs})
        else:
            data['form_is_valid'] = False
    else:
        form = OrderproductionForm()
    context = {'form': form, 'pk': pk}
    data['html_form'] = render_to_string('pr_create_form.html',
                                         context,
                                         request=request)
    data['pk'] = pk
    return JsonResponse(data)

# 船头板进度删除
def ssdelete(request, pk):
    data = dict()
    ss = get_object_or_404(Order_shipping_sample, pk=pk)
    order = ss.order
    pk = order.pk
    ss.delete()
    qs = order.shippingsamples.all().order_by('-created_date')
    data['form_is_valid'] = True
    data['html_ss_list'] = render_to_string('ss_list.html', {'qs': qs})
    data['pk'] = pk
    return JsonResponse(data)

# 大货进度删除
def prdelete(request, pk):
    data = dict()
    pr = get_object_or_404(Order_production, pk=pk)
    order = pr.order
    pk = order.pk
    pr.delete()
    qs = order.productions.all().order_by('-created_date')
    data['form_is_valid'] = True
    data['html_pr_list'] = render_to_string('pr_list.html', {'qs': qs})
    data['pk'] = pk
    return JsonResponse(data)


# 船头板进度修改
def ssedit(request, pk):
    data = dict()
    ss = get_object_or_404(Order_shipping_sample, pk=pk)
    order = ss.order
    pk = order.pk
    if request.method == 'POST':
        form = OrdershippingsampleForm(request.POST, instance=ss)
        if form.is_valid():
            form.save()
            qs = order.shippingsamples.all().order_by('-created_date')
            data['form_is_valid'] = True
            data['html_ss_list'] = render_to_string('ss_list.html', {'qs': qs})
        else:
            data['form_is_valid'] = False
    else:
        form = OrdershippingsampleForm(instance=ss)
    context = {'form': form, 'pk': ss.pk}
    data['html_form'] = render_to_string('ss_edit_form.html',
                                         context,
                                         request=request)
    data['pk'] = pk
    return JsonResponse(data)

# 大货进度修改
def predit(request, pk):
    data = dict()
    pr = get_object_or_404(Order_production, pk=pk)
    order = pr.order
    pk = order.pk
    if request.method == 'POST':
        form = OrderproductionForm(request.POST, instance=pr)
        if form.is_valid():
            form.save()
            qs = order.productions.all().order_by('-created_date')
            data['form_is_valid'] = True
            data['html_pr_list'] = render_to_string('pr_list.html', {'qs': qs})
        else:
            data['form_is_valid'] = False
    else:
        form = OrderproductionForm(instance=pr)
    context = {'form': form, 'pk': pr.pk}
    data['html_form'] = render_to_string('pr_edit_form.html',
                                         context,
                                         request=request)
    data['pk'] = pk
    return JsonResponse(data)


def progessplist(request, type):
    loginuser = request.user
    # 有问题的大货布进度记录对应的订单列表['orderid']
    bulk_fabric_p = Order_bulk_fabric.objects.filter(status="WARNING").values_list('order', flat=True)
    # 有大货布问题的订单
    orders_bulk_fabric_p = Order.objects.filter(pk__in=bulk_fabric_p)
    # 有问题的生产办进度记录对应的订单列表['orderid']
    fitting_p = Order_fitting_sample.objects.filter(status="WARNING").values_list('order', flat=True)
    # 有生产板问题的订单
    orders_fitting_p = Order.objects.filter(pk__in=fitting_p)
    # 有问题的船头板进度记录对应的订单列表['orderid']
    shipping_p = Order_shipping_sample.objects.filter(status="WARNING").values_list('order', flat=True)
    # 有船头板问题的订单
    orders_shipping_p = Order.objects.filter(pk__in=shipping_p)

    # 有问题的大货进度记录对应的订单列表['orderid']
    production_p = Order_production.objects.filter(status="WARNING").values_list('order', flat=True)
    # 有大货问题的订单
    orders_production_p = Order.objects.filter(pk__in=production_p)

    if type == 'fitting':
        if loginuser.is_factory:
            orders = orders_fitting_p.filter(factory=loginuser.factory)
        elif loginuser.is_merchandiser:
            orders = orders_fitting_p.filter(merchandiser=loginuser.merchandiser)
        else:
            orders = orders_fitting_p
        return render(request, 'order_list.html', {'orders': orders})

    elif type == 'bulkfabric':
        if loginuser.is_factory:
            orders = orders_bulk_fabric_p.filter(factory=loginuser.factory)
        elif loginuser.is_merchandiser:
            orders = orders_bulk_fabric_p.filter(merchandiser=loginuser.merchandiser)
        else:
            orders = orders_bulk_fabric_p
        return render(request, 'order_list.html', {'orders': orders})

    elif type == 'shipingsample':
        if loginuser.is_factory:
            orders = orders_shipping_p.filter(factory=loginuser.factory)
        elif loginuser.is_merchandiser:
            orders = orders_shipping_p.filter(merchandiser=loginuser.merchandiser)
        else:
            orders = orders_shipping_p
        return render(request, 'order_list.html', {'orders': orders})
    
    else:
        if loginuser.is_factory:
            orders = orders_production_p.filter(factory=loginuser.factory)
        elif loginuser.is_merchandiser:
            orders = orders_production_p.filter(merchandiser=loginuser.merchandiser)
        else:
            orders = orders_production_p
        return render(request, 'order_list.html', {'orders': orders})


class FunctionList(TemplateView):
    template_name = 'function_list.html'



# 翻单
@login_required
@m_mg_or_required
def ordercopy(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order_avatar =  order.avatar
    order_size_specs = order.sizespecs.all()
    order_swatches = order.swatches.all()
    order_packingways = order.PPackingways.all()

    order.pk = None
    order.status = "NEW"
    order.save()

    new_file = ContentFile(order_avatar.file.read())
    new_file_name = order_avatar.file.name.split(".")[0] + str(order_avatar.pk) + '.' + order_avatar.file.name.split(".")[1]
    order_avatar.pk = None
    order_avatar.order = order
    order_avatar.file.save(new_file_name, new_file) 
    order_avatar.save()

    for sizespec in order_size_specs:
        sizespec.pk = None
        sizespec.order = order
        sizespec.save()

    for swatch in order_swatches:
        swatch.pk = None
        swatch.order = order
        swatch.save()

    for packingway in order_packingways:
        order.PPackingways.add(packingway)

    return redirect('order:orderlistnew')



# 创建ALLY订单资料汇总
@login_required
@m_mg_qc_or_required
def orderlistinfo(request):
    packingway_dict = {}
    colorqtys_dict={}

    orderpklist = request.POST.getlist('orderpk')

    if not orderpklist:
        return redirect('order:orderlistconfirmed')
    else:
        orderlist = Order.objects.in_bulk(orderpklist)
        orderlist = orderlist.values()

    for i in range(len(orderpklist)):
        order = get_object_or_404(Order, pk=orderpklist[i])
        packingways = order.PPackingways.all()
        colorqtys = order.colorqtys.all().order_by('-created_date')
        packingway_dict[orderpklist[i]]=packingways
        colorqtys_dict[orderpklist[i]]=colorqtys


    return render(request, 'order_info_list.html', {'orderlist': orderlist, 'packingway_dict':packingway_dict, 'colorqtys_dict':colorqtys_dict})


# new qc report
@login_required
def newqcreport(request):
    user = request.user
    orderpklist = request.POST.getlist('orderpk')

    if len(orderpklist)==0:
        return redirect('order:orderlistconfirmed')
    else:
        orderpk = int(orderpklist[0])
        order = Order.objects.get(pk=orderpk)
    
    new_reports = Qc_report.objects.all().filter(status='NEW', order=order)

    if len(new_reports)==0:
        new_report = Qc_report.objects.create(created_by=user, order=order)
        form = QcreportForm()
        template_name = 'qc_report_new.html'
        
        return render(request, template_name, {'new_report':new_report, 'form':form, 'order':order})
        # return redirect('order:editqcreport', pk=new_report.pk, checkitem_number=0)
    else:
        template_name = 'qc_report_alert.html'
        
        return render(request, template_name, {'new_reports':new_reports})


@login_required
def updateqcreport(request,pk):
    
    new_report = Qc_report.objects.get(pk=pk)
    if request.method == 'POST':
        form = QcreportForm(request.POST)
        if form.is_valid():
            new_report.product_status = form.cleaned_data['product_status']
            new_report.color = form.cleaned_data['color']
            new_report.ratio = form.cleaned_data['ratio']
            new_report.save()
            
            return redirect('order:editqcreport', pk=new_report.pk, checkitem_number=0)
        else:
            messages.warning(request, '请填写带*的字段信息!')
            template_name = 'qc_report_new.html'
            form = QcreportForm()
            order = new_report.order
            return render(request, template_name, {'new_report':new_report, 'form':form, 'order':order})

    else:

        template_name = 'qc_report_new.html'
        form = QcreportForm(instance=new_report)
        order = new_report.order
        
        return render(request, template_name, {'new_report':new_report, 'form':form, 'order':order})




@login_required
def editqcreport(request,pk,checkitem_number):

    qc_report = Qc_report.objects.get(pk=pk)
    order = qc_report.order

    check_items = Check_item.objects.all()
    check_items_len = len(check_items)

    if checkitem_number==0:
        check_item = ''
        check_points  = ''
        check_item_before = ''
        check_item_after = ''
        selected_check_point_id_list = ''
        selected_check_point_grade_list = ''
        selected_check_point_ratio_list = ''
        selected_check_point_commennts_list = ''
        
        
    else:
        check_items =''
        # for new page
        check_item = Check_item.objects.get(number=checkitem_number)
        check_points = Check_point.objects.filter(check_item=check_item)

        selected_check_point_id_list = []
        selected_check_point_grade_list = []
        selected_check_point_ratio_list = []
        selected_check_point_commennts_list = []

        check_records = Check_record.objects.filter(qc_report=qc_report, check_item=check_item)

        for i in range(len(check_records)):
            check_record = check_records[i]
            check_point_id = check_record.check_point.pk
            check_point_grade = check_record.get_grade_display()
            check_point_ratio = check_record.ratio
            check_point_comments= check_record.comments
            selected_check_point_id_list.append(check_point_id)
            selected_check_point_grade_list.append(check_point_grade)
            selected_check_point_ratio_list.append(check_point_ratio)
            selected_check_point_commennts_list.append(check_point_comments)

        if checkitem_number!=check_items_len:
            check_item_before = check_item.number - 1
            check_item_after = check_item.number + 1
        else:
            check_item_before = check_item.number - 1
            check_item_after = check_items_len


    template_name = 'qc_report_edit.html'

    return render(request, template_name, context = {'qc_report':qc_report, 'order':order, 
                  'check_item':check_item, 'check_points': check_points ,
                  'check_items':check_items, 'check_item_before':check_item_before,
                  'check_item_after':check_item_after, 'check_items_len':check_items_len,
                  'selected_check_point_id_list': selected_check_point_id_list, 'selected_check_point_grade_list':selected_check_point_grade_list,
                  'selected_check_point_ratio_list': selected_check_point_ratio_list,
                  'selected_check_point_commennts_list':selected_check_point_commennts_list})

@login_required
def qcreportapi(request):
    checkitem_pk = request.GET.get('checkitem_pk',None)
    table_data = request.GET.get('query', None)
    qcreport_pk = request.GET.get('qcreport_pk', None)
    qc_report = Qc_report.objects.get(pk=qcreport_pk)
    check_item_table = Check_item.objects.get(pk=checkitem_pk)
    if table_data!='[]':
        table_data = json.loads(table_data)
        check_points_table = Check_point.objects.filter(check_item=check_item_table)
        check_points_table_ids = check_points_table.values_list('pk', flat=True)
        selected_check_points_ids = [int(item[1]) for item in table_data]
        diff_ids = list(set(check_points_table_ids) - set(selected_check_points_ids))

        if len(diff_ids)>0:
            for i in range(len(diff_ids)):
                pk=diff_ids[i]
                check_point_unselect = Check_point.objects.get(pk=pk)
                Check_record.objects.filter(qc_report=qc_report, check_point=check_point_unselect).delete()

        for i in range(len(table_data)):
            grade = table_data[i][2]
            if grade=='严重':
                grade_value='YZ'
            if grade=='次要':
                grade_value='CY'
            if grade=='请选择':
                grade_value=None

            ratio = table_data[i][3]
            comments = table_data[i][4]

            check_point = Check_point.objects.get(pk=table_data[i][1])

            query_checkpoint = Check_record.objects.filter(qc_report=qc_report, check_point=check_point)
            
            if len(query_checkpoint)>0:
                Check_record.objects.filter(qc_report=qc_report, check_point=check_point).update(
                    qc_report=qc_report, check_point=check_point,  check_item=check_item_table,
                    grade=grade_value, ratio=ratio,comments=comments)
            else:
                Check_record.objects.create(qc_report=qc_report, check_point=check_point,  check_item=check_item_table,
                    grade=grade_value, ratio=ratio,comments=comments)
    
    else:
        Check_record.objects.filter(qc_report=qc_report, check_item=check_item_table).delete()
    data = {'status': 1}

    return JsonResponse(data)

@login_required
def qcreportfinish(request,pk):

    qc_report = Qc_report.objects.get(pk=pk)
    order = qc_report.order

    if qc_report.status != 'SEND':
        qc_report.status = 'FINISH'
        qc_report.save()
    
        return redirect('order:qcreportsum', pk=qc_report.pk)


@login_required
def qcreportsum(request,pk):

    qc_report = Qc_report.objects.get(pk=pk)
    order = qc_report.order

    # if qc_report.status != 'SEND':
    #     qc_report.status = 'FINISH'
    #     qc_report.save()

    check_records = Check_record.objects.filter(qc_report=qc_report).order_by('check_item__number')
    template_name = 'qc_report_sum.html'

    return render(request, template_name, context = {'check_records':check_records, 'order':order, 'qc_report':qc_report})



# 发送QC报告
@login_required
def sendqcreport(request, pk):
    qc_report = Qc_report.objects.get(pk=pk)
    order = qc_report.order

    qc_report.status = 'SEND'
    qc_report.save()

    try:
        avatar_file = order.avatar.file
        encoded = base64.b64encode(open(avatar_file.path, "rb").read()).decode()
    except ObjectDoesNotExist:
        encoded = ''


    factoryemail = str(order.factory.email)
    merchandiseremail = str(order.merchandiser.user.email)
    merchandiser_m_email = User.objects.filter(is_merchandiser_manager=True).values_list('email', flat=True)
    merchandiser_m_email = list(merchandiser_m_email)
    
    merchandiser_m_email.append(factoryemail)
    merchandiser_m_email.append(merchandiseremail)

    sender_email = 'SCM@monayoung.com.au'
    receiver_email = merchandiser_m_email

    message = MIMEMultipart("alternative")
    message["Subject"] = "缘色SCM-新查货报告通知"
    message["From"] = sender_email
    message["To"] = ','.join(receiver_email)  
    orderpo = order.po
    orderstyleno = order.style_no
    brand = order.brand.name
    created_date = qc_report.created_date.strftime("%Y-%m-%d %H:%M:%S")
    created_by = qc_report.created_by
    report_link = qc_report.get_absolute_url()
    picscollection_link = report_link.replace("sum", "picscollection")
    html = f"""\
        <html>
        <body>
        <h3>新查货报告！</h3>
        
        <h3>订单号:{orderpo}</h3>
        <h3>款号:{orderstyleno}</h3>
        <h3>品牌:{brand}</h3>

        <h3>查货日期:{created_date}</h3>
        <h3>查货人员:{created_by}</h3>

        <h3>报告链接:<a href="{report_link}">查看</a></h3>
        <h3>图片汇总链接:<a href="{picscollection_link}">查看</a></h3>
        <h3>图片:</h3>
        <img src="data:image/jpg;base64,{encoded}" width=200px height=200px>
        </body>
        </html>
        """
    part = MIMEText(html, "html")
    message.attach(part)
    with smtplib.SMTP(config('EMAIL_HOST'), config('EMAIL_PORT', cast=int)) as server:
        server.login(config('EMAIL_HOST_USER'), config('EMAIL_HOST_PASSWORD')) 
        server.sendmail(sender_email, receiver_email, message.as_string()
            )
    messages.success(request, '邮件发送成功!')
    return redirect('order:qcreportsum', pk=pk)

# 显示全部QCREPORT
def qrall(request, orderpk):
    data = dict()
    order = get_object_or_404(Order, pk=orderpk)
    qs = order.qcreports.all().order_by('-created_date')
    data['html_qr_list'] = render_to_string('qr_list_all.html', {'qs': qs})
    data['pk'] = orderpk
    return JsonResponse(data)


# 只显示最近3个QCREPORT
def qrthree(request, orderpk):
    data = dict()
    order = get_object_or_404(Order, pk=orderpk)
    qs = order.qcreports.all().order_by('-created_date')[0:3]
    qs_showlist = []
    for i in range(len(qs)):
        qr = qs[i]
        if request.user == qr.created_by:
            qs_showlist.append(1)
        else:
            qs_showlist.append(0)
    data['html_qr_list'] = render_to_string('qr_list.html', {'qs': qs})
    data['qs_showlist'] = qs_showlist
    data['pk'] = orderpk
    return JsonResponse(data)

# qr删除
def qrdelete(request, pk):
    qr = get_object_or_404(Qc_report, pk=pk)
    qr.delete()

    return redirect('order:orderlistconfirmed')


# 查货照片上传
@login_required
def checkrecordpicsadd(request, pk):
    checkrecord = get_object_or_404(Check_record, pk=pk)
    form = CheckrecordpicsForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            with transaction.atomic():
                attach = form.save(commit=False)
                attach.checkrecord = checkrecord
                attach.save()
                data = {"files": [{
                            "name": attach.file.name,
                            "url": attach.file.url, },
                            ]}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)
    else:
        return render(request, 'checkrecordpicsadd.html', {'checkrecord': checkrecord})



@login_required
def checkrecordpicscollection(request, pk):
    checkrecord = get_object_or_404(Check_record, pk=pk)
    qcreport = checkrecord.qc_report
    pics = checkrecord.pics.all()
    if request.user == qcreport.created_by:
        show = 1
    else:
        show = 0
    return render(request, 'checkrecord_pics_collection.html', {'checkrecord': checkrecord,
                  'pics': pics, 'show':show})

@login_required
def checkrecordpicdelete(request, pk):
    pic = get_object_or_404(Check_record_pics, pk=pk)
    check_record = pic.checkrecord
    pic.delete()
    return redirect('order:checkrecordpicscollection', pk=check_record.pk)
    
@login_required
def qcreportpicscollection(request, pk):
    qr = get_object_or_404(Qc_report, pk=pk)
    order = qr.order
    checkrecords = Check_record.objects.filter(qc_report=qr).order_by('check_item__number')
    if request.user == qr.created_by:
        show = 1
    else:
        show = 0

    return render(request, 'qcreport_pics_collection.html', {'qr': qr,
                  'order': order, 'checkrecords': checkrecords, 'show':show})

# QCREPORT LIST
@login_required
def qcreportlist(request):
    loginuser = request.user
    if loginuser.is_merchandiser:
        qcreports = Qc_report.objects.filter(Q(order__merchandiser=loginuser.merchandiser)).order_by('-created_date')

    elif loginuser.is_factory:
        qcreports =  Qc_report.objects.filter(Q(order__factory=loginuser.factory)).order_by('-created_date')

    else:
        qcreports =  Qc_report.objects.all().order_by('-created_date')

    gradesum = [] 

    for i in range(len(qcreports)):
        grade = []
        qcreport = qcreports[i]
        checkrecords = qcreport.checkrecords

        checkrecords_yz_count = checkrecords.filter(grade='YZ').count()
        checkrecords_cy_count = checkrecords.filter(grade='CY').count()
        grade.append(checkrecords_yz_count)
        grade.append(checkrecords_cy_count)
        gradesum.append(grade)

    template_name = 'qcreport_list.html'
    
    return render(request, template_name, {'qcreports': qcreports, 'gradesum':gradesum}) 
