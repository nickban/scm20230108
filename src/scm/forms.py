from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from .models import (User, Factory,
                     Merchandiser, Designer, Shipping, Finance,
                     Qc, Office, Admin, Merchandiser_Manager, Post, PostAttachment,
                     Sample, Sample_size_specs, Sample_os_avatar,
                     Sample_os_pics, Sample_swatches,
                     Sample_pics_factory, Sample_quotation_form,
                     Sample_size_spec_factory,
                     Order, Order_color_ratio_qty, Order_size_specs,
                     Order_swatches, Order_shipping_pics, Order_avatar,
                     Order_packing_ctn, Invoice, Order_fitting_sample,
                     Order_bulk_fabric, Order_shipping_sample, Order_packing_status, Order_production,
                     Mainlabel, Maintag, Additiontag, Order_Barcode, Check_record_pics,
                     Qc_report)
from django.db import transaction
from tempus_dominus.widgets import DatePicker
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm


# 登录表单
class MyAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _("用户名和密码不匹配"),
        'inactive': _("该账号已被冻结"),
    }

#修改密码
class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_('旧密码'), error_messages={'required': "此字段必须填写！"})
    new_password1 = forms.CharField(label=_('新密码'), error_messages={'required': "此字段必须填写！"})
    new_password2 = forms.CharField(label=_('重新输入新密码'), error_messages={'required': "此字段必须填写！"})
    error_messages = {
        'password_incorrect': _("旧密码输入不正确，请重新输入！"),
        'password_mismatch': _("两次输入的密码不一致，请重新输入！"),
    }


# 用户注册
class SignUpForm(UserCreationForm):
    USER_ROLE_TYPE = [
        (1, '工厂'),
        (2, '跟单'),
        (3, '设计师'),
        (4, '财务'),
        (5, '船务'),
        (6, '质检'),
        (7, '行政'),
        (8, '管理员'),
        (9, '跟单主管'),
    ]
    username = forms.CharField(label=_('用户名'), error_messages={'required': "此字段必须填写！"})
    password1 = forms.CharField(label=_('密码'), error_messages={'required': "此字段必须填写！"})
    password2 = forms.CharField(label=_('确认密码'), error_messages={'required': "此字段必须填写！"})
    roles = forms.MultipleChoiceField(
        label=_('用户角色'),
        error_messages={'required': "必须选择一个以上用户角色！"},
        widget=forms.CheckboxSelectMultiple,
        choices=USER_ROLE_TYPE,
        required=True,
    )
    error_messages = {
        'password_mismatch': _("两次输入的密码不一致，请重新输入."),
    }

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'roles')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        roles = self.cleaned_data['roles']
        roles = list(map(int, roles))
        if 1 in roles:
            user.is_factory = True
        if 2 in roles:
            user.is_merchandiser = True
        if 3 in roles:
            user.is_designer = True
        if 4 in roles:
            user.is_finance = True
        if 5 in roles:
            user.is_shipping = True
        if 6 in roles:
            user.is_qc = True
        if 7 in roles:
            user.is_office = True
        if 8 in roles:
            user.is_admin = True
        if 9 in roles:
            user.is_merchandiser_manager = True
        user.save()
        if 1 in roles:
            Factory.objects.create(user=user)
        if 2 in roles:
            Merchandiser.objects.create(user=user)
        if 3 in roles:
            Designer.objects.create(user=user)
        if 4 in roles:
            Finance.objects.create(user=user)
        if 5 in roles:
            Shipping.objects.create(user=user)
        if 6 in roles:
            Qc.objects.create(user=user)
        if 7 in roles:
            Office.objects.create(user=user)
        if 8 in roles:
            Admin.objects.create(user=user)
        if 9 in roles:
            Merchandiser_Manager.objects.create(user=user)
        return user


# 新消息表单
class NewpostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewpostForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].empty_label = '请选择'
        self.fields['catagory'].empty_label = '请选择'
        
    class Meta:
        model = Post
        fields = ('title', 'content', 'created_by', 'catagory')


# 上传附件表单
class PostAttachmentForm(forms.ModelForm):
    class Meta:
        model = PostAttachment
        fields = ('file',)


# 新建样板表单
class NewsampleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewsampleForm, self).__init__(*args, **kwargs)
        self.fields['brand'].empty_label = '请选择'
        self.fields['merchandiser'].empty_label = '请选择'
        self.fields['designer'].empty_label = '请选择'

    class Meta:
        model = Sample
        fields = ('has_os_sample', 'sample_no', 'brand',
                  'merchandiser', 'designer')
        error_messages = {
            'sample_no': {
                'required': "必填字段！",
            },
            'brand': {
                'required': "必填字段！",
            },
            'merchandiser': {
                'required': "必填字段！",
            },
            'designer': {
                'required': "必填字段！",
            },
        }


# 样板表单
class SampleForm(forms.ModelForm):
    parcel_date = forms.DateField(widget=DatePicker(), label="寄件日期", required=False)
    estimate_finish_date = forms.DateField(widget=DatePicker(), label="预计完成日期", required=False)
    qutation = forms.DecimalField(label="工厂报价(元)", required=False)

    def __init__(self, *args, **kwargs):
        super(SampleForm, self).__init__(*args, **kwargs)
        self.fields['brand'].empty_label = '请选择'
        self.fields['merchandiser'].empty_label = '请选择'
        self.fields['designer'].empty_label = '请选择'
        self.fields['factory'].empty_label = '请选择'
        self.fields['style'].empty_label = '请选择'

    class Meta:
        model = Sample
        fields = ('has_os_sample', 'sample_no', 'brand',
                  'merchandiser', 'designer', 'factory', 'style', 'qutation',
                  'parcel_date', 'estimate_finish_date','alteration')
        widgets = {
                  'alteration': forms.Textarea(attrs={'rows': 6}),
                  }


# 详情页表单，工厂提交数据
class SampledetailForm(forms.ModelForm):
    qutation = forms.DecimalField(label="工厂报价(元)", required=False)
    estimate_finish_date = forms.DateField(widget=DatePicker(), label="预计完成日期", required=False)

    def __init__(self, *args, **kwargs):
        super(SampledetailForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['has_os_sample'].disabled = True

        def clean_has_os_sample_field(self):
            instance = getattr(self, 'instance', None)
            if instance and instance.id:
                return instance.has_os_sample
            else:
                return self.cleaned_data['has_os_sample']

    class Meta:
        model = Sample
        fields = ('has_os_sample', 'qutation', 'estimate_finish_date')
        widgets = {
                  'alteration': forms.Textarea(attrs={'rows': 6}),
                  }


# 样板尺寸表
class SamplesizespecsForm(forms.ModelForm):
    class Meta:
        model = Sample_size_specs
        fields = ('file',)


# 样板色卡
class SampleswatchForm(forms.ModelForm):
    class Meta:
        model = Sample_swatches
        fields = ('file',)


# 生产办照片
class SamplefpicsForm(forms.ModelForm):
    class Meta:
        model = Sample_pics_factory
        fields = ('file',)


# 样板头像表单
class SampleosavatarForm(forms.ModelForm):
    class Meta:
        model = Sample_os_avatar
        fields = ('file',)


# 样板报价单
class SamplequotationForm(forms.ModelForm):
    class Meta:
        model = Sample_quotation_form
        fields = ('file',)


# 样板尺寸表
class SamplesizespecfForm(forms.ModelForm):
    class Meta:
        model = Sample_size_spec_factory
        fields = ('file',)


# 样板原版照片
class SampleospicsForm(forms.ModelForm):
    class Meta:
        model = Sample_os_pics
        fields = ('file',)


# 订单表
class OrderForm(forms.ModelForm):
    handover_date_f = forms.DateField(widget=DatePicker(), label="工厂交期", required=False)
    handover_date_d = forms.DateField(widget=DatePicker(), label="客人交期", required=False)

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['brand'].empty_label = '请选择'
        self.fields['merchandiser'].empty_label = '请选择'
        self.fields['designer'].empty_label = '请选择'
        self.fields['factory'].empty_label = '请选择'
        self.fields['style'].empty_label = '请选择'
        self.fields['order_type'].empty_label = '请选择'
        self.fields['sample'].empty_label = '请选择'
        self.fields['tran_type'].empty_label = '请选择'
        self.fields['main_label'].empty_label = '请选择'
        self.fields['main_tag'].empty_label = '请选择'
        self.fields['addition_tag'].empty_label = '请选择'
        self.fields['packing_type'].empty_label = '请选择'
        self.fields['PShippingsample'].empty_label = '请选择'
        self.fields['PHangingtape'].empty_label = '请选择'
        self.fields['PSparebutton'].empty_label = '请选择'
        self.fields['PWashinglabel'].empty_label = '请选择'

    class Meta:
        model = Order
        fields = ('status', 'po', 'style_no', 'order_type', 'tran_type',
                  'brand', 'merchandiser', 'designer', 'style',
                  'factory', 'sample', 'factory_price', 'disigner_price',
                  'handover_date_f', 'handover_date_d', 'comments',
                  'parent', 'invoice', 'main_label', 'main_tag', 'addition_tag',
                  'packing_type', 'destination', 'labeltype', 'childorder', 'season_code', 'pgr_code',
                  'itemgroup_code', 'PShippingsample', 'PHangingtape', 'PSparebutton',
                  'PWashinglabel', 'matchcolor','ziliao')
        widgets = {
                  'comments': forms.Textarea(attrs={'rows': 1}),
                  'matchcolor': forms.Textarea(attrs={'rows': 1}),
                  }
        error_messages = {
            'po': {
                'required': "必填字段！",
            },
            'style_no': {
                'required': "必填字段！",
            },
            'brand': {
                'required': "必填字段！",
            },
            'merchandiser': {
                'required': "必填字段！",
            },
            'designer': {
                'required': "必填字段！",
            },
            'packing_type': {
                'required': "必填字段！",
            },
        }


# 订单颜色配比表单
class Order_color_ratio_qty_Form(forms.ModelForm):
    class Meta:
        model = Order_color_ratio_qty
        fields = ('color', 'color_cn', 'color_no', 'ratio', 'size1', 'size2', 'size3', 'size4', 'size5', 'size6','bags', 'qty')


# 订单尺寸表
class OrdersizespecsForm(forms.ModelForm):
    class Meta:
        model = Order_size_specs
        fields = ('file',)


# 订单色卡
class OrderswatchForm(forms.ModelForm):
    class Meta:
        model = Order_swatches
        fields = ('file',)


# 订单条码
class OrderbarcodeForm(forms.ModelForm):
    class Meta:
        model = Order_Barcode
        fields = ('file',)


# 订单船头板
class OrdershippingpicsForm(forms.ModelForm):
    class Meta:
        model = Order_shipping_pics
        fields = ('file',)


# 订单头像
class OrderavatarForm(forms.ModelForm):
    class Meta:
        model = Order_avatar
        fields = ('file',)


# 发票表单
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ('file',)


# 订单装箱单表单
class OrderpackingctnForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order', None)
        super(OrderpackingctnForm, self).__init__(*args, **kwargs)
        self.fields['color'].queryset = Order_color_ratio_qty.objects.filter(order=self.order)
        self.fields['color'].empty_label = '请选择'

    class Meta:
        model = Order_packing_ctn
        fields = ('color', 'ctn_start_no',
                  'ctn_end_no', 'totalboxes', 'sharebox', 'bags', 'size1',
                  'size2', 'size3', 'size4', 'size5', 'size6','totalqty')


# 发票搜索表单
class InvoiceSearchForm(forms.Form):
    start_handover_date_f = forms.DateField(widget=DatePicker(), label="工厂交期", required=False)
    end_handover_date_f = forms.DateField(widget=DatePicker(), label="客人交期", required=False)
    factory = forms.ModelChoiceField(queryset=Factory.objects.all(), empty_label="请选择", required=False)


# 订单生产办进度
class OrderfittingsampleForm(forms.ModelForm):
    class Meta:
        model = Order_fitting_sample
        fields = ('sample', 'status')


# 订单大货布进度
class OrderbulkfabricForm(forms.ModelForm):
    class Meta:
        model = Order_bulk_fabric
        fields = ('bulk_fabric', 'status')


# 订单船头板进度
class OrdershippingsampleForm(forms.ModelForm):
    class Meta:
        model = Order_shipping_sample
        fields = ('shipping_sample', 'status')

# 订单船大货进度
class OrderproductionForm(forms.ModelForm):
    class Meta:
        model = Order_production
        fields = ('production', 'status')

# 修改纸箱规格
class OrderpackingstatusForm(forms.ModelForm):
    class Meta:
        model = Order_packing_status
        fields = ('length', 'width', 'height', 'cube', 'gross_weight')


# 工厂信息表单
class FactoryForm(forms.ModelForm):

    class Meta:
        model = Factory
        fields = ('name', 'contactperson', 'address', 'email', 'phone', 'bank',
                  'bankaccount', 'bankaccountnumber')
        error_messages = {
            'name': {
                'required': "必填字段！",
            },
            'contactperson': {
                'required': "必填字段！",
            },
            'address': {
                'required': "必填字段！",
            },
            'email': {
                'required': "必填字段！",
                'invalid': "邮件格式不正确！"
            },
            'phone': {
                'required': "必填字段！",
            },
            'bank': {
                'required': "必填字段！",
            },
            'bankaccount': {
                'required': "必填字段！",
            },
            'bankaccountnumber': {
                'required': "必填字段！",
            },
        }


# 主唛表单
class MainlabelForm(forms.ModelForm):
    file = forms.FileField(widget=forms.FileInput)

    def __init__(self, *args, **kwargs):
        super(MainlabelForm, self).__init__(*args, **kwargs)
        self.fields['brand'].empty_label = '请选择'

    class Meta:
        model = Mainlabel
        fields = ('name', 'brand', 'file')
        error_messages = {
            'name': {
                'required': "必填字段！",
            },
            'brand': {
                'required': "必填字段！",
            },
        }


# 挂牌
class MaintagForm(forms.ModelForm):
    file = forms.FileField(widget=forms.FileInput)

    def __init__(self, *args, **kwargs):
        super(MaintagForm, self).__init__(*args, **kwargs)
        self.fields['brand'].empty_label = '请选择'

    class Meta:
        model = Maintag
        fields = ('name', 'brand', 'file')
        error_messages = {
            'name': {
                'required': "必填字段！",
            },
            'brand': {
                'required': "必填字段！",
            },
        }


# 附加挂牌
class AdditiontagForm(forms.ModelForm):
    file = forms.FileField(widget=forms.FileInput)

    def __init__(self, *args, **kwargs):
        super(AdditiontagForm, self).__init__(*args, **kwargs)
        self.fields['brand'].empty_label = '请选择'

    class Meta:
        model = Additiontag
        fields = ('name', 'brand', 'file')
        error_messages = {
            'name': {
                'required': "必填字段！",
            },
            'brand': {
                'required': "必填字段！",
            },
        }


#修改密码
class SetPasswordForm(forms.Form):

    error_messages = {
        'password_mismatch': _("两次输入的密码不一致！"),
    }
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='用户', empty_label="请选择", required=False)
    new_password1 = forms.CharField(label=_("新密码"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("重新输入新密码"),
                                    widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)


# 查货照片
class CheckrecordpicsForm(forms.ModelForm):
    class Meta:
        model = Check_record_pics
        fields = ('file',)

# QCREPORT
class QcreportForm(forms.ModelForm):

    class Meta:
        model = Qc_report
        fields = ('product_status', 'color', 'ratio')
        error_messages = {
                    'product_status': {
                        'required': "必填字段！",
                    },
                    'color': {
                        'required': "必填字段！",
                    },
                    'ratio': {
                        'required': "必填字段！",
                    },
                }

