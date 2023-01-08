from pickle import NONE
from pydoc import describe
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.conf import settings
import os
from datetime import date


# 系统登录用户模块，用于分配用户角色
class User(AbstractUser):
    is_factory = models.BooleanField(default=False)
    is_merchandiser = models.BooleanField(default=False)
    is_designer = models.BooleanField(default=False)
    is_finance = models.BooleanField(default=False)
    is_shipping = models.BooleanField(default=False)
    is_qc = models.BooleanField(default=False)
    is_office = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_merchandiser_manager = models.BooleanField(default=False)


# 工厂角色
class Factory(models.Model):
    user = models.OneToOneField(User, verbose_name='工厂',
                                on_delete=models.CASCADE, primary_key=True)
    show = models.BooleanField(default=True)
    name = models.CharField('工厂名称', max_length=100)
    contactperson = models.CharField('联系人', max_length=100)
    address = models.CharField('地址', max_length=200)
    email = models.EmailField('邮箱',null=True)
    phone = models.CharField('手机', max_length=100)
    bank = models.CharField('开户银行', null=True, max_length=100)
    bankaccount = models.CharField('银行账户', null=True, max_length=100)
    bankaccountnumber = models.CharField('银行账号', null=True, max_length=100)

    def __str__(self):
        return self.user.username


# 跟单角色
class Merchandiser(models.Model):
    user = models.OneToOneField(User, verbose_name='跟单',
                                on_delete=models.CASCADE, primary_key=True)
    show = models.BooleanField(default=True)


    def __str__(self):
        return self.user.username


# 设计师角色
class Designer(models.Model):
    user = models.OneToOneField(User, verbose_name='设计师',
                                on_delete=models.CASCADE, primary_key=True)
    show = models.BooleanField(default=True)


    def __str__(self):
        return self.user.username


# 财务角色
class Finance(models.Model):
    user = models.OneToOneField(User, verbose_name='财务',
                                on_delete=models.CASCADE, primary_key=True)
    show = models.BooleanField(default=True)


    def __str__(self):
        return self.user.username


# 船务角色
class Shipping(models.Model):
    user = models.OneToOneField(User, verbose_name='船务',
                                on_delete=models.CASCADE, primary_key=True)
    show = models.BooleanField(default=True)


    def __str__(self):
        return self.user.username


# QC角色
class Qc(models.Model):
    user = models.OneToOneField(User, verbose_name='质检',
                                on_delete=models.CASCADE, primary_key=True)
    show = models.BooleanField(default=True)


    def __str__(self):
        return self.user.username


# 管理员角色
class Admin(models.Model):
    user = models.OneToOneField(User, verbose_name='管理员',
                                on_delete=models.CASCADE, primary_key=True)
    show = models.BooleanField(default=True)


    def __str__(self):
        return self.user.username


# 行政角色
class Office(models.Model):
    user = models.OneToOneField(User, verbose_name='行政',
                                on_delete=models.CASCADE, primary_key=True)
    show = models.BooleanField(default=True)


    def __str__(self):
        return self.user.username


# 跟单主管角色
class Merchandiser_Manager(models.Model):
    user = models.OneToOneField(User, verbose_name='跟单主管',
                                on_delete=models.CASCADE, primary_key=True)
    show = models.BooleanField(default=True)


    def __str__(self):
        return self.user.username


# 款式模块
class Style(models.Model):
    name = models.CharField('款式', max_length=50)
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# 品牌模块
class Brand(models.Model):
    name = models.CharField('品牌', max_length=50)
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# 样板部分模块定义


class Sample(models.Model):
    NEW = 'NEW'
    SENT_FACTORY = 'SENT_F'
    COMPLETED = 'COMPLETED'
    SAMPLE_STATUS = [
        (NEW, '新建'),
        (SENT_FACTORY, '送工厂'),
        (COMPLETED, '完成'),
    ]
    created_date = models.DateTimeField('创建日期', auto_now_add=True)
    sample_no = models.CharField('样板号', max_length=100)
    has_os_sample = models.BooleanField('是否有原版?', )
    brand = models.ForeignKey(Brand,
                              verbose_name='品牌',
                              related_name='samples',
                              on_delete=models.SET_NULL,
                              null=True)
    merchandiser = models.ForeignKey(Merchandiser,
                                     verbose_name='跟单',
                                     related_name='samples',
                                     on_delete=models.SET_NULL,
                                     null=True)
    designer = models.ForeignKey(Designer,
                                 verbose_name='买手',
                                 related_name='samples',
                                 on_delete=models.SET_NULL,
                                 null=True)
    style = models.ForeignKey(Style,
                              verbose_name='款式',
                              related_name='samples',
                              blank=True,
                              on_delete=models.SET_NULL,
                              null=True)
    factory = models.ForeignKey(Factory,
                                verbose_name='工厂',
                                related_name='samples',
                                blank=True,
                                on_delete=models.SET_NULL,
                                null=True)
    parcel_date = models.DateField('寄件日期', null=True, blank=True)
    estimate_finish_date = models.DateField('预计完成日期', null=True, blank=True)
    qutation = models.DecimalField('工厂报价',
                                   max_digits=5,
                                   decimal_places=2,
                                   null=True, blank=True)
    alteration = models.TextField('做板评语', blank=True)
    status = models.CharField('样板状态',
                              max_length=50,
                              choices=SAMPLE_STATUS,
                              blank=True,
                              default=NEW)

    def __str__(self):
        return self.sample_no
    
    @property
    def days_till(self):
        today = date.today()
        days_till = today - self.created_date.date()
        days_till_str = str(days_till).split(",",1)[0].split(" ",1)[0]
        return days_till_str





class Sample_size_spec_factory(models.Model):
    file = models.FileField(upload_to='sample/size_spec_factory/', blank=True)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE,
                                  related_name='sizespecf')


@receiver(models.signals.post_delete, sender=Sample_size_spec_factory)
def auto_delete_file_sample_size_spec_factory(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Sample_swatches(models.Model):
    file = models.ImageField(upload_to='sample/swatches/', blank=True)
    sample = models.ForeignKey(Sample,
                               on_delete=models.CASCADE,
                               related_name='swatches')


@receiver(models.signals.post_delete, sender=Sample_swatches)
def auto_delete_file_sample_swatches(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Sample_os_avatar(models.Model):
    file = models.ImageField(upload_to='sample/os_avatar/', blank=True)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE,
                                  related_name='os_avatar')


@receiver(models.signals.post_delete, sender=Sample_os_avatar)
def auto_delete_file_sample_os_avatar(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Sample_quotation_form(models.Model):
    file = models.FileField(upload_to='sample/quotation_form/', blank=True)
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE, related_name='quotation')


@receiver(models.signals.post_delete, sender=Sample_quotation_form)
def auto_delete_file_sample_qutation_form(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Sample_os_pics(models.Model):
    file = models.ImageField(upload_to='sample/os_pics/', blank=True)
    sample = models.ForeignKey(Sample,
                               on_delete=models.CASCADE,
                               related_name='os_pics')


@receiver(models.signals.post_delete, sender=Sample_os_pics)
def auto_delete_file_sample_os_pics(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Sample_pics_factory(models.Model):
    file = models.ImageField(upload_to='sample/pics_factory/', blank=True)
    sample = models.ForeignKey(Sample,
                               on_delete=models.CASCADE,
                               related_name='factory_pics')


@receiver(models.signals.post_delete, sender=Sample_pics_factory)
def auto_delete_file_sample_pics_factory(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Sample_size_specs(models.Model):
    file = models.FileField(upload_to='sample/size_specs/', blank=True)
    sample = models.ForeignKey(Sample,
                               on_delete=models.CASCADE,
                               related_name='size_specs')


@receiver(models.signals.post_delete, sender=Sample_size_specs)
def auto_delete_file_sample_size_specs(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

# 信息部分定义


N = '通知'
M = '手册'
NOTIFICATION_CATAGORY = [
    (None, '请选择'),
    (N, '通知'),
    (M, '手册'),
]


class Post(models.Model):
    title = models.CharField('标题', max_length=100)
    content = models.TextField('内容')
    create_time = models.DateTimeField('发布日期', auto_now_add=True)
    created_by = models.ForeignKey(Office, on_delete=models.CASCADE, verbose_name='发布人')
    catagory = models.CharField('类别', max_length=100, choices=NOTIFICATION_CATAGORY)

    def get_absolute_url(self):
        return reverse('post:postedit', args=[str(self.id)])


class PostAttachment(models.Model):
    file = models.FileField(upload_to='post/', blank=True)
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             verbose_name='关联信息',
                             related_name='postattachments')


@receiver(models.signals.post_delete, sender=PostAttachment)
def auto_delete_file_postattachment(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


# 订单部分
class Invoice(models.Model):
    NEW = 'NEW'
    CONFIRMED = 'CONFIRMED'
    PAID = 'PAID'
    INVOICESTATUS = [
        (NEW, '新建'),
        (CONFIRMED, '财务已确认'),
        (PAID, '已付款')
    ]
    created_date = models.DateTimeField('创建日期', auto_now_add=True)
    invoice_no = models.CharField('发票号', max_length=100)
    status = models.CharField('状态', max_length=50, choices=INVOICESTATUS, default="NEW")
    file = models.FileField(upload_to='order/invoice/', blank=True)
    handoverdate = models.DateTimeField('出货日期', null=True)
    start_of_week = models.DateTimeField(null=True)
    end_of_week = models.DateTimeField(null=True)
    factory = models.ForeignKey(Factory,
                                verbose_name='工厂',
                                related_name='invoices',
                                on_delete=models.SET_NULL,
                                null=True)


@receiver(models.signals.post_delete, sender=Invoice)
def auto_delete_file_invoice(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Mainlabel(models.Model):
    name = models.CharField('主唛编号', max_length=50)
    file = models.FileField('图片', upload_to='order/mainlabel/', blank=True)
    brand = models.ForeignKey(Brand,
                              verbose_name='品牌',
                              related_name='mainlabels',
                              on_delete=models.SET_NULL,
                              null=True)

    def __str__(self):
        return self.name


@receiver(models.signals.post_delete, sender=Mainlabel)
def auto_delete_file_mainlabel(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Maintag(models.Model):
    name = models.CharField('挂牌编号', max_length=50)
    file = models.FileField('图片', upload_to='order/maintag/', blank=True)
    brand = models.ForeignKey(Brand,
                              verbose_name='品牌',
                              related_name='maintags',
                              on_delete=models.SET_NULL,
                              null=True)

    def __str__(self):
        return self.name


@receiver(models.signals.post_delete, sender=Maintag)
def auto_delete_file_maintag(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Additiontag(models.Model):
    name = models.CharField('附加挂牌编号', max_length=50)
    file = models.FileField('图片', upload_to='order/additiontag/', blank=True)
    brand = models.ForeignKey(Brand,
                              verbose_name='品牌',
                              related_name='additiontags',
                              on_delete=models.SET_NULL,
                              null=True)

    def __str__(self):
        return self.name


@receiver(models.signals.post_delete, sender=Additiontag)
def auto_delete_file_additiontag(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

#大货生产包装部分字段定义
class PShippingsample(models.Model):
    description = models.CharField('船头板', max_length=100)

    def __str__(self):
        return self.description


class PSparebutton(models.Model):
    description = models.CharField('备用扣', max_length=100)

    def __str__(self):
        return self.description

class PWashinglabel(models.Model):
    description = models.CharField('洗水唛', max_length=400)

    def __str__(self):
        return self.description

class PPackingway(models.Model):
    description = models.CharField('包装要求', max_length=300)

    def __str__(self):
        return self.description

class Packingtype(models.Model):
    shortname = models.CharField('包装方式', max_length=50)
    description = models.TextField('说明', blank=True)

    def __str__(self):
        return self.shortname


class Order(models.Model):
    NEW = 'NEW'
    SENT_FACTORY = 'SENT_FACTORY'
    CONFIRMED = 'CONFIRMED'
    SHIPPED = 'SHIPPED'
    ORDER_STATUS = [
        (NEW, '新建'),
        (SENT_FACTORY, '送工厂'),
        (CONFIRMED, '已确认'),
        (SHIPPED, '已出货'),
    ]

    NEWORDER = 'NEWORDER'
    REPEATORDER = 'REPEATORDER'
    WEBORDER = 'WEBORDER'
    ORDER_TYPE = [
        (None, '请选择'),
        (NEWORDER, '店铺单'),
        # (REPEATORDER, '翻单'),
        (WEBORDER, '网单'),

    ]

    SEA = 'SEA'
    AIR = 'AIR'
    TRAN_TYPE = [
        (None, '请选择'),
        (SEA, '海运'),
        (AIR, '空运'),
    ]
    AU = 'AU'
    NZ = 'NZ'
    SG = 'SG'
    KR = 'KR'
    US = 'US'
    DESTINATION = [
        (None, '请选择'),
        (AU, '澳洲'),
        (NZ, '新西兰'),
        (SG, '新加坡'),
        (KR, '韩国'),
        (US, '美国'),
    ]

    CNZ = 'CNZ'
    CSG = 'CSG'
    CNZSG = 'CNZSG'
    CHILDORDER = [
        (None, '请选择'),
        (CNZ, 'NZ'),
        (CSG, 'SG'),
        (CNZSG, 'NZ,SG'),
    ]

    QQ = 'QQ'
    WQ = 'WQ'
    ZILIAO = [
        (None, '请选择'),
        (QQ, '齐全'),
    ]

    NUMBER = 'NUMBER'
    ALPHABET = 'ALPHABET'
    LABELTYPE = [
        (None, '请选择'),
        (NUMBER, '数字码'),
        (ALPHABET, '字母码'),
    ]

    created_date = models.DateTimeField('创建日期', auto_now_add=True)
    status = models.CharField('订单状态',
                              max_length=50,
                              choices=ORDER_STATUS,
                              blank=True,
                              default=NEW)
    po = models.CharField('订单号', max_length=100)
    style_no = models.CharField('款号', max_length=100)
    order_type = models.CharField('订单类型', max_length=50,
                                  choices=ORDER_TYPE,
                                  blank=True)
    destination = models.CharField('目的地', max_length=50,
                                   choices=DESTINATION,
                                   blank=True)

    childorder = models.CharField('小单', max_length=50,
                                  choices=CHILDORDER,
                                  blank=True)
    ziliao = models.CharField('资料', max_length=50,
                                  choices=ZILIAO,
                                  blank=True)

    tran_type = models.CharField('运输类型', max_length=50, choices=TRAN_TYPE, blank=True)
    brand = models.ForeignKey(Brand,
                              verbose_name='品牌',
                              related_name='orders',
                              on_delete=models.SET_NULL,
                              null=True)
    merchandiser = models.ForeignKey(Merchandiser,
                                     verbose_name='跟单',
                                     related_name='orders',
                                     on_delete=models.SET_NULL,
                                     null=True)
    designer = models.ForeignKey(Designer,
                                 verbose_name='买手',
                                 related_name='orders',
                                 on_delete=models.SET_NULL,
                                 null=True)
    style = models.ForeignKey(Style,
                              verbose_name='款式',
                              related_name='orders',
                              blank=True,
                              on_delete=models.SET_NULL,
                              null=True)
    factory = models.ForeignKey(Factory,
                                verbose_name='工厂',
                                related_name='orders',
                                blank=True,
                                on_delete=models.SET_NULL,
                                null=True)
    sample = models.ForeignKey(Sample,
                               verbose_name='关联原板',
                               related_name='orders',
                               blank=True,
                               on_delete=models.SET_NULL,
                               null=True)
    factory_price = models.DecimalField('工厂价格',
                                        max_digits=5,
                                        decimal_places=2,
                                        null=True, blank=True)
    disigner_price = models.DecimalField('客人价格',
                                         max_digits=5,
                                         decimal_places=2,
                                         null=True, blank=True)
    handover_date_f = models.DateField('工厂交期', null=True, blank=True)
    handover_date_d = models.DateField('客人交期', null=True, blank=True)
    comments = models.TextField('生产办评语', blank=True)
    matchcolor = models.TextField('配色要求', blank=True)
    parent = models.ForeignKey('self',
                               verbose_name='父订单',
                               related_name='suborders',
                               blank=True,
                               on_delete=models.SET_NULL,
                               null=True)
    invoice = models.ForeignKey(Invoice,
                                verbose_name='发票号',
                                related_name='orders',
                                blank=True,
                                on_delete=models.SET_NULL,
                                null=True)
    main_label = models.ForeignKey(Mainlabel,
                                   verbose_name='主唛',
                                   blank=True,
                                   on_delete=models.SET_NULL,
                                   null=True)
    main_tag = models.ForeignKey(Maintag,
                                 verbose_name='挂牌',
                                 blank=True,
                                 on_delete=models.SET_NULL,
                                 null=True)
    addition_tag = models.ForeignKey(Additiontag,
                                     verbose_name='附加挂牌',
                                     blank=True,
                                     on_delete=models.SET_NULL,
                                     null=True)
    packing_type = models.ForeignKey(Packingtype,
                                     verbose_name='包装方式',
                                     on_delete=models.SET_NULL,
                                     null=True)
    labeltype = models.CharField('码标类型',
                                 max_length=50,
                                 choices=LABELTYPE,
                                 blank=True,
                                 default=NUMBER)
    season_code = models.CharField('SEASON', max_length=100, null=True, blank=True)
    pgr_code = models.CharField('PGR', max_length=100, null=True, blank=True)
    itemgroup_code = models.CharField('ITEM GROUP', max_length=100, null=True, blank=True)
    actual_ship_qty = models.PositiveSmallIntegerField(null=True, blank=True)
    #大货包装部分
    PShippingsample = models.ForeignKey(PShippingsample,
                               verbose_name='船头板',
                               blank=True,
                               on_delete=models.SET_NULL,
                               null=True)
    
    PHangingtape = models.CharField('挂衣绳', max_length=100, null=True, blank=True, default='无')

    PSparebutton = models.ForeignKey(PSparebutton,
                               verbose_name='备用扣',
                               blank=True,
                               on_delete=models.SET_NULL,
                               null=True)

    PWashinglabel = models.ForeignKey(PWashinglabel,
                               verbose_name='洗水唛',
                               blank=True,
                               on_delete=models.SET_NULL,
                               null=True)

    PPackingways = models.ManyToManyField(PPackingway,
                               verbose_name='包装要求',
                               blank=True,
                               null=True)


    def __str__(self):
        ordername = '订单号' + self.po + '/' + '款号' + self.style_no
        return ordername


@receiver(models.signals.post_save, sender=Order)
def create_order_packing_status(sender, instance, created, **kwargs):
    if created:
        Order_packing_status.objects.create(order=instance)


class Order_avatar(models.Model):
    file = models.ImageField(upload_to='order/avatar/', blank=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE,
                                 related_name='avatar')


@receiver(models.signals.post_delete, sender=Order_avatar)
def auto_delete_file_order_avatar(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Order_size_specs(models.Model):
    file = models.FileField(upload_to='order/size_specs/', blank=True)
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='sizespecs')


@receiver(models.signals.post_delete, sender=Order_size_specs)
def auto_delete_file_order_size_specs(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Order_shipping_pics(models.Model):
    file = models.FileField(upload_to='order/shipping_pics/', blank=True)
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='shippingpics')


@receiver(models.signals.post_delete, sender=Order_shipping_pics)
def auto_delete_file_order_shipping_pics(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Order_swatches(models.Model):
    file = models.FileField(upload_to='order/swatches/', blank=True)
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='swatches')


@receiver(models.signals.post_delete, sender=Order_swatches)
def auto_delete_file_order_swatches(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Order_Barcode(models.Model):
    file = models.FileField(upload_to='order/barcodes/', blank=True)
    order = models.OneToOneField(Order,
                                 on_delete=models.CASCADE,
                                 related_name='barcode')


@receiver(models.signals.post_delete, sender=Order_Barcode)
def auto_delete_file_order_barcode(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Order_color_ratio_qty(models.Model):
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='colorqtys')
    created_date = models.DateTimeField(auto_now_add=True)
    color = models.CharField('颜色(英文)', max_length=100)
    color_cn = models.CharField('颜色(中文)', max_length=100)
    color_no = models.CharField('色号', max_length=100)
    ratio = models.CharField('比列', max_length=100, default='', null=True, blank=True)
    size1 = models.PositiveSmallIntegerField()
    size2 = models.PositiveSmallIntegerField()
    size3 = models.PositiveSmallIntegerField()
    size4 = models.PositiveSmallIntegerField()
    size5 = models.PositiveSmallIntegerField()
    size6 = models.PositiveSmallIntegerField()
    bags = models.PositiveSmallIntegerField(null=True, blank=True)
    qty = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.color_cn


class Order_packing_ctn(models.Model):
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='packing_ctns')
    color = models.ForeignKey(Order_color_ratio_qty,
                              on_delete=models.CASCADE,
                              related_name='packing_ctns')
    created_date = models.DateTimeField(auto_now_add=True)
    ctn_start_no = models.PositiveSmallIntegerField()
    ctn_end_no = models.PositiveSmallIntegerField()
    totalboxes = models.PositiveSmallIntegerField()
    sharebox = models.BooleanField(default=False)
    bags = models.PositiveSmallIntegerField(null=True, blank=True)
    size1 = models.PositiveSmallIntegerField()
    size2 = models.PositiveSmallIntegerField()
    size3 = models.PositiveSmallIntegerField()
    size4 = models.PositiveSmallIntegerField()
    size5 = models.PositiveSmallIntegerField()
    size6 = models.PositiveSmallIntegerField(default=0)
    totalqty = models.PositiveSmallIntegerField()


class Order_packing_status(models.Model):
    NEW = 'NEW'
    SUBMIT = 'SUBMIT'
    CLOSED = 'CLOSED'
    PACKINGSTATUS = [
        (NEW, '新建'),
        (SUBMIT, '工厂已提交'),
        (CLOSED, '已确认'),
    ]

    order = models.OneToOneField(Order, verbose_name='订单',
                                 on_delete=models.CASCADE,
                                 related_name='packing_status')
    status = models.CharField('状态',
                              max_length=100,
                              choices=PACKINGSTATUS,
                              default=NEW)

    length = models.DecimalField('长',
                                 max_digits=5,
                                 decimal_places=2,
                                 null=True, blank=True,
                                 default=54)
    width = models.DecimalField('宽',
                                max_digits=5,
                                decimal_places=2,
                                null=True, blank=True,
                                default=40)
    height = models.DecimalField('高',
                                 max_digits=5,
                                 decimal_places=2,
                                 null=True, blank=True,
                                 default=35)
    cube = models.DecimalField('体积',
                               max_digits=5,
                               decimal_places=2,
                               null=True, blank=True,
                               default=0.8)
    gross_weight = models.DecimalField('毛重',
                                       max_digits=5,
                                       decimal_places=2,
                                       null=True,
                                       blank=True,
                                       default=14)
    
    def __str__(self):
        
        return self.order.po


class Order_bulk_fabric(models.Model):
    NORMAL = 'NORMAL'
    WARNING = 'WARNING'
    CHOICES = [
        (NORMAL, '正常'),
        (WARNING, '警告'),
    ]
    created_date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='bulkfabrics')
    bulk_fabric = models.CharField('大货布进度', max_length=200)
    status = models.CharField('状态',
                              max_length=100,
                              choices=CHOICES,
                              default=NORMAL)
    class Meta:
        ordering = ['-created_date']

class Order_fitting_sample(models.Model):
    NORMAL = 'NORMAL'
    WARNING = 'WARNING'
    URGENT = 'URGENT'
    CHOICES = [
        (NORMAL, '正常'),
        (WARNING, '警告'),
    ]
    created_date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='fittingsamples')
    sample = models.CharField('生产办进度', max_length=200)
    status = models.CharField('状态',
                              max_length=100,
                              choices=CHOICES,
                              default=NORMAL)

    class Meta:
        ordering = ['-created_date']


class Order_shipping_sample(models.Model):
    NORMAL = 'NORMAL'
    WARNING = 'WARNING'
    URGENT = 'URGENT'
    CHOICES = [
        (NORMAL, '正常'),
        (WARNING, '警告'),
    ]
    created_date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='shippingsamples')
    shipping_sample = models.CharField('船头板进度', max_length=200)
    status = models.CharField('状态',
                              max_length=100,
                              choices=CHOICES,
                              default=NORMAL)
    class Meta:
        ordering = ['-created_date']

class Order_production(models.Model):
    NORMAL = 'NORMAL'
    WARNING = 'WARNING'
    URGENT = 'URGENT'
    CHOICES = [
        (NORMAL, '正常'),
        (WARNING, '警告'),
    ]
    created_date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='productions')
    production = models.CharField('大货进度', max_length=200)
    status = models.CharField('状态',
                              max_length=100,
                              choices=CHOICES,
                              default=NORMAL)
    
    class Meta:
        ordering = ['-created_date']


class Order_child_order(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='childorders')
    child_order = models.CharField('小单', max_length=200)


# for qc report
class Check_item(models.Model):
    name = models.CharField('检查类别', max_length=100)
    number = models.IntegerField()

    def __str__(self):
        return self.name

class Check_point(models.Model):
    name = models.CharField('检查项目', max_length=100)
    number = models.CharField('序号', max_length=20)
    description = models.CharField('描述', max_length=500,blank=True, null=True)
    check_item = models.ForeignKey(Check_item,
                              on_delete=models.CASCADE,
                              verbose_name='检查类别',
                              related_name='Checkpoints')
    def __str__(self):
        return self.name

class Qc_report(models.Model):
    NEW = 'NEW'
    FINISH = 'FINISH'
    SEND = 'SEND'
    REPORT_STATUS = [
        (NEW, '新建'),
        (FINISH, '完成'),
        (SEND, '已发送'),
    ]

    NEW_P = 'NEW_P'
    FINISH_P = 'FINISH_P'
    PACK_P = 'SEND_P'

    PRODUCT_STATUS = [
        (None, '请选择'),
        (NEW_P, '刚出成品'),
        (FINISH_P, '成品全部完成'),
        (PACK_P, '大货包装完成'),
    ]

    ONE_C = 'ONE_C'
    ALL_C = 'ALL_C'


    COLOR_STATUS = [
        (None, '请选择'),
        (ONE_C, '单色'),
        (ALL_C, '齐色'),
    ]

    created_date = models.DateTimeField('创建日期', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='质检人员')
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='qcreports')
    status = models.CharField('状态',
                              max_length=100,
                              choices=REPORT_STATUS,
                              default=NEW)
    product_status = models.CharField('大货状态',
                            max_length=100,
                            choices=PRODUCT_STATUS)
    color = models.CharField('颜色',
                            max_length=100,
                            choices=COLOR_STATUS)
    ratio = models.CharField('抽查数量/件', max_length=50)

    def get_absolute_url(self):
        host = settings.ALLOWED_HOSTS[0]
        if settings.DEBUG == True:
            host = host + ':8000'
        # print(host)
        return 'http://' + host + "/order/qcreport/%i/sum/" % self.id

    def get_grade_sum(self):

        checkrecords = self.checkrecords.all()
        checkrecords_yz_count = checkrecords.filter(grade='YZ').count()
        checkrecords_cy_count = checkrecords.filter(grade='CY').count()

        return '严重问题:' + str(checkrecords_yz_count) + ';' + '次要问题:' + str(checkrecords_cy_count) + ';'

    class Meta:
        ordering = ['-created_date']


class Check_record(models.Model):
    YZ = 'YZ'
    CY = 'CY'

    GRADE = [
        (None, '请选择'),
        (YZ, '严重'),
        (CY, '次要'),
    ]

    qc_report = models.ForeignKey(Qc_report,
                              on_delete=models.CASCADE,
                              related_name='checkrecords')

    check_point = models.ForeignKey(Check_point,
                              on_delete=models.CASCADE)

    check_item  = models.ForeignKey(Check_item,
                              on_delete=models.CASCADE)

    grade = models.CharField('严重等级',
                              max_length=50,
                              choices=GRADE,
                              blank=True,
                              null=True)

    ratio = models.CharField('比列', max_length=50, null=True)
    comments = models.CharField('QC备注', max_length=500, null=True)

    
# 查货照片
class Check_record_pics(models.Model):
    file = models.FileField(upload_to='order/checkrecordpics/', blank=True)
    checkrecord = models.ForeignKey(Check_record,
                                on_delete=models.CASCADE,
                                related_name='pics')