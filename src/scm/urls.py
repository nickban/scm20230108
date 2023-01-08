from django.urls import path, include
from .views import order, sample, post, home, report

urlpatterns = [
    # 可以在这个地方做一个角色入口重定向, 但是本系统没有做，都定位到home
    path('', home.home, name='home'),
    path('setting/', home.setting, name='setting'),

    # 统计导航
    path('report/', include(([
        path('profit/', report.ProfitView.as_view(), name='profit'),
        path('api/profit/data/<int:pk>/', report.ProfitViewData.as_view()),
        path('factory_qty/', report.Factory_Qty_View.as_view(), name='factoryqty'),
        path('api/factory_qty/data/<int:pk>/', report.Factory_Qty_ViewData.as_view()),
        path('money_month/', report.Money_Month_View.as_view(), name='moneymonth'),
        path('api/money_month/data/<int:pk>/', report.Money_Month_ViewData.as_view()),
    ], 'scm'), namespace='report')),


    # 样板地址导航
    path('sample/', include(([
        # 未完成，已完成样板列表
        path('', sample.SampleListNew.as_view(), name='samplelistnew'),
        path('completed/', sample.SampleListCompleted.as_view(), name='samplelistcompleted'),
        # 样板新增
        path('add/step1/', sample.SampleAddStep1.as_view(), name='sampleaddstep1'),
        path('add/<int:pk>/step2/', sample.SampleAddStep2.as_view(), name='sampleaddstep2'),
        # 样板编辑，详情，删除
        path('<int:pk>/', sample.SampleEdit.as_view(), name='sampleedit'),
        path('<int:pk>/detail/', sample.SampleDetail.as_view(), name='sampledetail'),
        path('<int:pk>/delete/', sample.SampleDelete.as_view(), name='sampledelete'),
        # 样板上传资料通用功能
        path('<int:pk>/<str:attachtype>/add/', sample.sampleattachadd, name='sampleattachadd'),
        path('<int:pk>/<str:attachtype>/collection/', sample.sampleattachcollection, name='sampleattachcollection'),
        path('<int:pk>/<str:attachtype>/<int:attach_pk>/delete/', sample.sampleattachdelete, name='sampleattachdelete'),
        # 样板送工厂，通知工厂
        path('<int:pk>/sentfactory/', sample.samplesentfactory, name='samplesentfactory'),
        # 样板已完成
        path('<int:pk>/completed/', sample.samplecompleted, name='samplecompleted'),
        # 样板重置
        path('<int:pk>/reset/', sample.samplereset, name='samplereset'),
        # 测试用
        # path('<int:pk>/copy/', sample.samplecopy, name='samplecopy'),
    ], 'scm'), namespace='sample')),

    # 订单地址导航
    path('order/', include(([
        # 未确认,已确认,已出货订单列表
        path('new/', order.OrderListNew.as_view(), name='orderlistnew'),
        path('confirmed/', order.OrderListConfrimed.as_view(), name='orderlistconfirmed'),
        path('shipped/', order.OrderListShipped.as_view(), name='orderlistshipped'),

        path('shipbyweek/<int:pk>/', order.ordershipbyweek, name='ordershipbyweek'),

        path('shippedthisweek/', order.OrderListShipThisWeek.as_view(), name='orderlistshipthisweek'),
        path('shippednextweek/', order.OrderListShipNextWeek.as_view(), name='orderlistshipnextweek'),
        path('shippednextnextweek/', order.OrderListShipNextNextWeek.as_view(), name='orderlistshipnextnextweek'),


        # 订单信息汇总
        path('listinfo/', order.orderlistinfo, name='orderlistinfo'),

        # 订单新增
        path('add/', order.OrderAdd.as_view(), name='orderadd'),
        # 订单编辑，详情，删除
        path('<int:pk>/', order.OrderEdit.as_view(), name='orderedit'),
        path('<int:pk>/delete/', order.OrderDelete.as_view(), name='orderdelete'),
        path('<int:pk>/detail/', order.orderdetail, name='orderdetail'),
        #订单包装方式选择
        path('<int:pk>/packingway/add/', order.packingwayadd, name='packingwayadd'),
        # 订单颜色数量增删改
        path('<int:pk>/colorqty/add/', order.colorqtyadd, name='colorqtyadd'),
        path('<int:pk>/colorqty/<int:colorqtypk>/', order.colorqtyedit, name='colorqtyedit'),
        path('<int:pk>/colorqty/<int:colorqtypk>/delete/', order.colorqtydelete, name='colorqtydelete'),
        #qc_report
        path('qcreport/add/', order.newqcreport, name='newqcreport'),
        path('qcreport/<int:pk>/update', order.updateqcreport, name='updateqcreport'),
        path('qcreport/api/', order.qcreportapi, name='qcreportapi'),
        path('qcreport/<int:pk>/sum/', order.qcreportsum, name='qcreportsum'),
        path('qcreport/<int:pk>/sum/send', order.sendqcreport, name='sendqcreport'),
        path('qcreport/<int:pk>/finish', order.qcreportfinish, name='qcreportfinish'),
        path('qcreport/<int:pk>/checkitem/<int:checkitem_number>/', order.editqcreport, name='editqcreport'),
        
        path('<int:orderpk>/qcreports/all/', order.qrall, name='qrall'),
        path('<int:orderpk>/qcreports/3/', order.qrthree, name='qrthree'),
        path('qr/<int:pk>/delete/', order.qrdelete, name='qrdelete'),

        path('checkrecord/<int:pk>/picsadd/', order.checkrecordpicsadd, name='checkrecordpicsadd'),
        path('checkrecord/<int:pk>/picscollection/', order.checkrecordpicscollection, name='checkrecordpicscollection'),
        path('checkrecord/pic/<int:pk>/delete/', order.checkrecordpicdelete, name='checkrecordpicdelete'),

        path('qcreport/<int:pk>/picscollection/', order.qcreportpicscollection, name='qcreportpicscollection'),

        path('qcreport/list/', order.qcreportlist, name='qcreportlist'),

        # 订单送工厂，通知工厂
        path('<int:pk>/sentfactory/', order.ordersentfactory, name='ordersentfactory'),
        # 订单确认
        path('<int:pk>/confirm/', order.orderconfirm, name='orderconfirm'),
        # 订单出货
        path('<int:pk>/shipped/', order.ordershipped, name='ordershipped'),
        # 订单重置
        path('<int:pk>/reset/', order.orderreset, name='orderreset'),
        # 测试用-翻单
        path('<int:pk>/copy/', order.ordercopy, name='ordercopy'),

        # 生产板进度增删改
        path('<int:pk>/progress/fs/', order.fittingsample, name='fittingsample'),
        path('<int:pk>/progress/fs/all/', order.fsall, name='fsall'),
        path('<int:pk>/progress/fs/3/', order.fsthree, name='fsthree'),
        path('fs/<int:pk>/delete/', order.fsdelete, name='fsdelete'),
        path('fs/<int:pk>/edit/', order.fsedit, name='fsedit'),
        # 大货布进度增删改
        path('<int:pk>/progress/bf/', order.bulkfabric, name='bulkfabric'),
        path('bf/<int:pk>/delete/', order.bfdelete, name='bfdelete'),
        path('bf/<int:pk>/edit/', order.bfedit, name='bfedit'),
        # 船头板进度增删改
        path('<int:pk>/progress/ss/', order.shippingsample, name='shippingsample'),
        path('ss/<int:pk>/delete/', order.ssdelete, name='ssdelete'),
        path('ss/<int:pk>/edit/', order.ssedit, name='ssedit'),

        # 大货进度增删改
        path('<int:pk>/progress/pr/', order.production, name='production'),
        path('pr/<int:pk>/delete/', order.prdelete, name='prdelete'),
        path('pr/<int:pk>/edit/', order.predit, name='predit'),
        path('<int:pk>/progress/pr/all/', order.prall, name='prall'),
        path('<int:pk>/progress/pr/3/', order.prthree, name='prthree'),
        # 进度有问题的订单试图
        path('progressp/<str:type>/', order.progessplist, name='progessplist'),
        # 创建装箱单
        path('<int:pk>/packinglist/add/', order.packinglistadd, name='packinglistadd'),
        # 修改装箱单纸箱规格
        path('<int:pk>/changeboxsize/', order.Update_packingstatus.as_view(), name='changeboxsize'),
        # 删除装箱单
        path('<int:pk>/packinglist/<int:plpk>/delete/', order.packinglistdelete, name='packinglistdelete'),
        # 装箱单详情
        path('<int:pk>/packinglist/detail/', order.packinglistdetail, name='packinglistdetail'),
        # 装箱单提交
        path('<int:pk>/packinglist/submit/', order.packinglistsubmit, name='packinglistsubmit'),
        # 装箱单关闭，不能更改
        path('<int:pk>/packinglist/close/', order.packinglistclose, name='packinglistclose'),
        # 装箱单重置
        path('<int:pk>/packinglist/reset/', order.packinglistreset, name='packinglistreset'),
        # 查订单颜色的比列
        path('getratio/', order.getratio, name='getratio'),
        # 装箱单查找, 此功能系统暂不使用，代码可以供未来参考
        # path('search/', order.plsearch, name='plsearch'),
        # 订单发票部分
        path('invoice/add/', order.invoiceadd, name='invoiceadd'),
        path('invoice/<int:pk>/detail/', order.invoicedetail, name='invoicedetail'),
        path('invoice/<int:pk>/delete/', order.invoicedelete, name='invoicedelete'),
        path('invoice/<int:pk>/pay/', order.invoicepay, name='invoicepay'),
        path('invoice/<int:pk>/reset/', order.invoicereset, name='invoicereset'),
        path('invoice/list/', order.invoicelist, name='invoicelist'),
        path('invoice/<int:pk>/attachadd/', order.invoiceattachadd, name='invoiceattachadd'),


        # 订单上传资料通用功能
        path('<int:pk>/<str:attachtype>/add/', order.orderattachadd, name='orderattachadd'),
        path('<int:pk>/<str:attachtype>/collection/', order.orderattachcollection, name='orderattachcollection'),
        path('<int:pk>/<str:attachtype>/<int:attach_pk>/delete/', order.orderattachdelete, name='orderattachdelete'),
    ], 'scm'), namespace='order')),

    # admin地址导航
    path('admin/', include(([
        path('', order.FunctionList.as_view(), name='function_list'),
    ], 'scm'), namespace='admin')),

    # systemsetting地址导航 主唛挂牌
    path('syssetting/', include(([
        path('', home.Syssetting.as_view(), name='syssetting'),
        path('mainlabel/', home.MainLabel.as_view(), name='mainlabel'),
        path('mainlabel/add/', home.MainLabelAdd.as_view(), name='mainlabeladd'),
        path('mainlabel/<int:pk>/update/', home.MainLabelUpdate.as_view(), name='mainlabelupdate'),
        path('mainlabel/<int:pk>/delete/', home.mainlabeldelete, name='mainlabeldelete'),
        # 挂牌
        path('maintag/', home.MainTag.as_view(), name='maintag'),
        path('maintag/add/', home.MainTagAdd.as_view(), name='maintagadd'),
        path('maintag/<int:pk>/update/', home.MainTagUpdate.as_view(), name='maintagupdate'),
        path('maintag/<int:pk>/delete/', home.maintagdelete, name='maintagdelete'),
        # 附加挂牌
        path('additiontag/', home.AdditionTag.as_view(), name='additiontag'),
        path('additiontag/add/', home.AdditionTagAdd.as_view(), name='additiontagadd'),
        path('additiontag/<int:pk>/update/', home.AdditionTagUpdate.as_view(), name='additiontagupdate'),
        path('additiontag/<int:pk>/delete/', home.additiontagdelete, name='additiontagdelete'),
    ], 'scm'), namespace='syssetting')),


    # post地址导航
    path('post/', include(([
        path('', post.PostList.as_view(), name='postlist'),
        path('add/', post.PostAdd.as_view(), name='postadd'),
        path('<int:pk>/', post.PostEdit.as_view(), name='postedit'),
        path('<int:pk>/detail/', post.PostDetail.as_view(), name='postdetail'),
        path('<int:pk>/attach/add/', post.postattach, name='postattach'),
        path('<int:pk>/attach/<int:postattach_pk>/delete/', post.postattachdelete, name='postattachdelete'),
        path('<int:pk>/delete/', post.PostDelete.as_view(), name='postdelete'),
    ], 'scm'), namespace='post')),
]
