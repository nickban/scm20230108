from os import name

from rest_framework.views import APIView
from rest_framework.response import Response
from django.views import View
from django.shortcuts import render
from django.db.models import F, Sum, DecimalField, ExpressionWrapper,  Q
from scm.models import Factory, Order
from django.utils.decorators import method_decorator
from scm.decorators import m_mg_or_required
from django.contrib.auth.decorators import login_required
from scm.models import User


@method_decorator([login_required, m_mg_or_required], name='dispatch')
class ProfitView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'chart.html')


@method_decorator([login_required, m_mg_or_required], name='dispatch')
class ProfitViewData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        year = self.kwargs['pk']
        print(year)
        dataall = []
        # dataau = []
        # datanz = []
        # datasg = []
        # datakr = []
        dataally = []
        # datajojo = []
        datavg = []
        for month in range(1,13):
            # 全部订单
            ordersall = Order.objects.filter(~Q(status="NEW"), Q(handover_date_d__month=month), Q(handover_date_d__year=year))
            profit =0
            # print(month)
            # print(len(ordersall))
            for order in ordersall:
                order_qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                order_qty = order_qty['orderqty']
                order_profit = order_qty*(order.disigner_price-order.factory_price)
                # print(order)
                # print(order_profit)
                profit = profit + order_profit
                # print(profit)
            dataall.append(profit)

            # ALLY
            ordersally = Order.objects.filter(~Q(status="NEW"), Q(handover_date_d__month=month), Q(handover_date_d__year=year),
                Q(brand__name='Ally') | Q(brand__name='Ally（minx & moss）') | Q(brand__name='You+All'))
            profit_ally =0
            for order in ordersally:
                order_qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                order_qty = order_qty['orderqty']
                order_profit = order_qty*(order.disigner_price-order.factory_price)
                profit_ally = profit_ally + order_profit
            dataally.append(profit_ally)

            # VG
            ordersvg = Order.objects.filter(~Q(status="NEW"), Q(handover_date_d__month=month), Q(handover_date_d__year=year),
                Q(brand__name='Valleygirl') | Q(brand__name='MIRROU'))
            profit_ally =0
            for order in ordersvg:
                order_qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                order_qty = order_qty['orderqty']
                order_profit = order_qty*(order.disigner_price-order.factory_price)
                profit_ally = profit_ally + order_profit
            datavg.append(profit_ally)
            
            # ordersall = ordersall.annotate(profit=ExpressionWrapper(
            #             (F('disigner_price')-F('factory_price'))*F('actual_ship_qty'), 
            #             output_field=DecimalField()))
            # profit= ordersall.aggregate(profittotal=Sum('profit', output_field=DecimalField()))
            # profit_number = profit['profittotal']
            # dataall.append(profit_number)
            # # 澳洲 订单
            # orderau = Order.objects.filter(Q(status="SHIPPED"), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(brand__name='Valleygirl'), Q(destination='AU'))
            # orderau = orderau.annotate(profit=ExpressionWrapper(
            #            (F('disigner_price')-F('factory_price'))*F('actual_ship_qty'), 
            #            output_field=DecimalField()))
            # profit= orderau.aggregate(profittotal=Sum('profit', output_field=DecimalField()))
            # profit_number = profit['profittotal']
            # dataau.append(profit_number)

            # # NZ 订单
            # ordersnz = Order.objects.filter(Q(status="SHIPPED"), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(brand__name='MIRROU'))
            # ordersnz = ordersnz.annotate(profit=ExpressionWrapper(
            #              (F('disigner_price')-F('factory_price'))*F('actual_ship_qty'), 
            #              output_field=DecimalField()))
            # profit= ordersnz.aggregate(profittotal=Sum('profit', output_field=DecimalField()))
            # profit_number = profit['profittotal']
            # datanz.append(profit_number)

            # # SG 订单
            # orderssg = Order.objects.filter(Q(status="SHIPPED"), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(brand__name='Valleygirl'), Q(destination='SG'))
            # orderssg = orderssg.annotate(profit=ExpressionWrapper(
            #              (F('disigner_price')-F('factory_price'))*F('actual_ship_qty'), 
            #              output_field=DecimalField()))
            # profit= orderssg.aggregate(profittotal=Sum('profit', output_field=DecimalField()))
            # profit_number = profit['profittotal']
            # datasg.append(profit_number)

            # # 韩国 订单
            # orderskr = Order.objects.filter(Q(status="SHIPPED"), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(brand__name='Valleygirl'), Q(destination='KR'))
            # orderskr = orderskr.annotate(profit=ExpressionWrapper(
            #            (F('disigner_price')-F('factory_price'))*F('actual_ship_qty'), 
            #            output_field=DecimalField()))
            # profit= orderskr.aggregate(profittotal=Sum('profit', output_field=DecimalField()))
            # profit_number = profit['profittotal']
            # datakr.append(profit_number)

            # # ALLY
            # ordersally = Order.objects.filter(Q(status="SHIPPED"), Q(handover_date_f__month=month), Q(handover_date_f__year=year),
            #     Q(brand__name='Ally') | Q(brand__name='Ally（minx & moss）') | Q(brand__name='You+All'))
            # ordersally = ordersally .annotate(profit=ExpressionWrapper(
            #            (F('disigner_price')-F('factory_price'))*F('actual_ship_qty'), 
            #            output_field=DecimalField()))
            # profit= ordersally.aggregate(profittotal=Sum('profit', output_field=DecimalField()))
            # profit_number = profit['profittotal']
            # dataally.append(profit_number)

            # # JOJO
            # ordersjojo= Order.objects.filter(Q(status="SHIPPED"), Q(handover_date_f__month=month), Q(handover_date_f__year=year),
            #     Q(brand__name='天使') | Q(brand__name='JoJo') | Q(brand__name='OO') | Q(brand__name='Selfie') | Q(brand__name='Saints Secrets') | Q(brand__name='太阳'))
            # oordersjojo = ordersjojo.annotate(profit=ExpressionWrapper(
            #            (F('disigner_price')-F('factory_price'))*F('actual_ship_qty'), 
            #            output_field=DecimalField()))
            # profit= oordersjojo.aggregate(profittotal=Sum('profit', output_field=DecimalField()))
            # profit_number = profit['profittotal']
            # datajojo.append(profit_number)

        data = {
            "labels": ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"],
            "dataall": dataall,
            # "dataau": dataau,
            # "datanz": datanz,
            # "datasg": datasg,
            # "datakr": datakr,
            "dataally": dataally,
            # "datajojo": datajojo,
            "datavg": datavg,
        }   

        return Response(data)




@method_decorator([login_required, m_mg_or_required], name='dispatch')
class Factory_Qty_View(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'chart_factory_qty.html')


@method_decorator([login_required, m_mg_or_required], name='dispatch')
class Factory_Qty_ViewData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        year = self.kwargs['pk']
        print(year)
        datazp = []
        datasc = []
        dataqx = []
        databz = []
        datajh = []
        datajs = []
        datals = []
        datahy = []
        for month in range(1,13):
            # ZP
            user = User.objects.get(username='卓品服饰')
            factory = user.factory
            ordersall = Order.objects.filter((Q(status="SENT_FACTORY") | Q(status="CONFIRMED")), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(factory=factory))
            totalqtyzp = 0
            for order in ordersall:
                qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                qty_number = qty['orderqty']
                totalqtyzp = totalqtyzp + qty_number
            datazp.append(totalqtyzp)

            # 勋成毛织
            user = User.objects.get(username='勋成毛织')
            factory = user.factory
            ordersall = Order.objects.filter((Q(status="SENT_FACTORY") | Q(status="CONFIRMED")), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(factory=factory))
            totalqtysc = 0
            for order in ordersall:
                qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                qty_number = qty['orderqty']
                totalqtysc = totalqtysc + qty_number
            datasc.append(totalqtysc)
            
            # 启先
            user = User.objects.get(username='启先')
            factory = user.factory
            ordersall = Order.objects.filter((Q(status="SENT_FACTORY") | Q(status="CONFIRMED")), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(factory=factory))
            totalqtyqx = 0
            for order in ordersall:
                qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                qty_number = qty['orderqty']
                totalqtyqx = totalqtyqx + qty_number
            dataqx.append(totalqtyqx)

            # 标准
            user = User.objects.get(username='标准')
            factory = user.factory
            ordersall = Order.objects.filter((Q(status="SENT_FACTORY") | Q(status="CONFIRMED")), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(factory=factory))
            totalqtybz = 0
            for order in ordersall:
                qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                qty_number = qty['orderqty']
                totalqtybz = totalqtybz + qty_number
            databz.append(totalqtybz)

            # 俊和
            user = User.objects.get(username='俊和')
            factory = user.factory
            ordersall = Order.objects.filter((Q(status="SENT_FACTORY") | Q(status="CONFIRMED")), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(factory=factory))
            totalqtyjh = 0
            for order in ordersall:
                qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                qty_number = qty['orderqty']
                totalqtyjh = totalqtyjh + qty_number
            datajh.append(totalqtyjh)

            # 杰森
            user = User.objects.get(username='杰森')
            factory = user.factory
            ordersall = Order.objects.filter((Q(status="SENT_FACTORY") | Q(status="CONFIRMED")), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(factory=factory))
            totalqtyjs = 0
            for order in ordersall:
                qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                qty_number = qty['orderqty']
                totalqtyjs = totalqtyjs + qty_number
            datajs.append(totalqtyjs)

            # 宏业
            user = User.objects.get(username='宏业')
            factory = user.factory
            ordersall = Order.objects.filter((Q(status="SENT_FACTORY") | Q(status="CONFIRMED")), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(factory=factory))
            totalqtyhy = 0
            for order in ordersall:
                qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                qty_number = qty['orderqty']
                totalqtyhy = totalqtyhy + qty_number
            datahy.append(totalqtyhy)   

            # 刘氏
            user = User.objects.get(username='刘氏')
            factory = user.factory
            ordersall = Order.objects.filter((Q(status="SENT_FACTORY") | Q(status="CONFIRMED")), Q(handover_date_f__month=month), Q(handover_date_f__year=year), Q(factory=factory))
            totalqtyls = 0
            for order in ordersall:
                qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                qty_number = qty['orderqty']
                totalqtyls = totalqtyls + qty_number
            datals.append(totalqtyls)       

        data = {
            "labels": ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"],
            "datazp": datazp,
            "datasc": datasc,
            "dataqx": dataqx,
            "databz": databz,
            "datajh": datajh,
            "datajs": datajs,
            "datahy": datahy,
            "datals": datals,

        }   

        return Response(data)



@method_decorator([login_required, m_mg_or_required], name='dispatch')
class Money_Month_View(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'chart_money_month.html')


@method_decorator([login_required, m_mg_or_required], name='dispatch')
class Money_Month_ViewData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        year = self.kwargs['pk']
        data_ally_confirm = []
        data_ally_all = []

        data_vg_confirm = []
        data_vg_all = []
        # print(year)

        for month in range(1,13):

            ordersconfirm_ally = Order.objects.filter((Q(status="SENT_FACTORY") | Q(status="CONFIRMED")), Q(handover_date_d__month=month), Q(handover_date_d__year=year),
            Q(brand__name='Ally') | Q(brand__name='Ally（minx & moss）') | Q(brand__name='You+All'))
            
            total_money_confirm_ally=0


            for order in ordersconfirm_ally:
                order_qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                order_qty = order_qty['orderqty']
                order_money = order_qty*order.disigner_price
                total_money_confirm_ally = total_money_confirm_ally + order_money
            data_ally_confirm.append(total_money_confirm_ally)


            ordersall_ally = Order.objects.filter(~Q(status="NEW"), Q(handover_date_d__month=month), Q(handover_date_d__year=year),
            Q(brand__name='Ally') | Q(brand__name='Ally（minx & moss）') | Q(brand__name='You+All'))
            
            total_money_all_ally=0

            for order in ordersall_ally:
                order_qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                order_qty = order_qty['orderqty']
                order_money = order_qty*order.disigner_price
                total_money_all_ally = total_money_all_ally + order_money
            data_ally_all.append(total_money_all_ally)

            # vg
            ordersconfirm_vg = Order.objects.filter((Q(status="SENT_FACTORY") | Q(status="CONFIRMED")), Q(handover_date_d__month=month), Q(handover_date_d__year=year),
            Q(brand__name='Valleygirl') | Q(brand__name='MIRROU'))
            
            total_money_confirm_vg=0


            for order in ordersconfirm_vg:
                order_qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                order_qty = order_qty['orderqty']
                order_money = order_qty*order.disigner_price
                total_money_confirm_vg = total_money_confirm_vg + order_money
            data_vg_confirm.append(total_money_confirm_vg)


            ordersall_vg = Order.objects.filter(~Q(status="NEW"), Q(handover_date_d__month=month), Q(handover_date_d__year=year),
            Q(brand__name='Valleygirl') | Q(brand__name='MIRROU'))
            
            total_money_all_vg=0

            for order in ordersall_vg:
                order_qty = order.colorqtys.aggregate(orderqty=Sum('qty', output_field=DecimalField()))
                order_qty = order_qty['orderqty']
                order_money = order_qty*order.disigner_price
                total_money_all_vg = total_money_all_vg + order_money
            data_vg_all.append(total_money_all_vg)
    

        data = {
            "labels": ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"],
            "data_ally_confirm": data_ally_confirm,
            "data_ally_all": data_ally_all,
            "data_vg_confirm": data_vg_confirm,
            "data_vg_all": data_vg_all,


        }   

        return Response(data)