from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from scm.models import (Sample, Sample_os_pics,
                        Sample_size_specs, Sample_os_avatar,
                        Sample_swatches, Sample_quotation_form,
                        Sample_pics_factory, Sample_size_spec_factory)
from scm.forms import (NewsampleForm, SampleForm, SamplesizespecsForm,
                       SampleosavatarForm, SampleospicsForm,
                       SampleswatchForm, SamplefpicsForm, SamplequotationForm,
                       SamplesizespecfForm, SampledetailForm)
from django.contrib.auth.decorators import login_required
from scm.decorators import o_m_mg_or_required, sample_is_completed
from django.utils.decorators import method_decorator
from django.contrib.auth.views import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import smtplib
from decouple import config


# 样板列表-未完成(新建，已送工厂状态)
@method_decorator([login_required], name='dispatch')
class SampleListNew(ListView):
    model = Sample
    ordering = ('-created_date', )
    context_object_name = 'samples'
    template_name = 'sample_list.html'

    def get_queryset(self):
        loginuser = self.request.user
        if loginuser.is_merchandiser:
            return Sample.objects.filter(Q(merchandiser=loginuser.merchandiser),
                                         Q(status='NEW') | Q(status='SENT_F')).order_by('-created_date')
        elif loginuser.is_factory:
            return Sample.objects.filter(factory=loginuser.factory, status='SENT_F').order_by('-created_date')
        else:
            return Sample.objects.filter(Q(status='NEW') | Q(status='SENT_F')).order_by('-created_date')

    def get_context_data(self, **kwargs):
        kwargs['type'] = 'NEW'
        return super().get_context_data(**kwargs)

# 样板列表-已完成(已完成状态)
@method_decorator([login_required], name='dispatch')
class SampleListCompleted(ListView):
    model = Sample
    ordering = ('-created_date', )
    context_object_name = 'samples'
    template_name = 'sample_list.html'

    def get_queryset(self):
        loginuser = self.request.user
        if loginuser.is_merchandiser:
            return Sample.objects.filter(Q(merchandiser=loginuser.merchandiser),
                                         Q(status='COMPLETED'))
        elif loginuser.is_factory:
            return Sample.objects.filter(Q(factory=loginuser.factory),
                                         Q(status='COMPLETED'))
        else:
            return Sample.objects.filter(status='COMPLETED')

    def get_context_data(self, **kwargs):
        kwargs['type'] = 'COMPLETED'
        return super().get_context_data(**kwargs)

# 样板新建第一步
@method_decorator([login_required, o_m_mg_or_required], name='dispatch')
class SampleAddStep1(CreateView):
    model = Sample
    form_class = NewsampleForm
    template_name = 'sample_add.html'

    def form_valid(self, form):
        sample = form.save()
        messages.success(self.request, '样板创建成功, 请上传资料!')
        return redirect('sample:sampleaddstep2', pk=sample.pk)

# 样板新建第二步
@method_decorator([login_required, o_m_mg_or_required], name='dispatch')
class SampleAddStep2(UpdateView):
    model = Sample
    form_class = NewsampleForm
    template_name = 'sample_add.html'

    def form_valid(self, form):
        sample = form.save()
        return redirect('sample:sampleaddstep2', pk=sample.pk)

    def get_context_data(self, **kwargs):
        try:
            kwargs['os_avatar'] = self.get_object().os_avatar
        except ObjectDoesNotExist:
            pass
        kwargs['os_pics'] = self.get_object().os_pics.all()
        kwargs['size_specs'] = self.get_object().size_specs.all()
        return super().get_context_data(**kwargs)

# 样板更新
@method_decorator([login_required, sample_is_completed, o_m_mg_or_required], name='dispatch')
class SampleEdit(UpdateView):
    model = Sample
    form_class = SampleForm
    template_name = 'sample_edit.html'
    context_object_name = 'sample'

    def get_context_data(self, **kwargs):
        kwargs['os_pics'] = self.get_object().os_pics.all()
        kwargs['size_specs'] = self.get_object().size_specs.all()
        kwargs['swatches'] = self.get_object().swatches.all()
        kwargs['fpics'] = self.get_object().factory_pics.all()
        try:
            kwargs['os_avatar'] = self.get_object().os_avatar
        except ObjectDoesNotExist:
            kwargs['os_avatar'] = ''
        try:
            kwargs['quotation'] = self.get_object().quotation
        except ObjectDoesNotExist:
            kwargs['quotation'] = ''
        try:
            kwargs['sizespecf'] = self.get_object().sizespecf
        except ObjectDoesNotExist:
            kwargs['sizespecf'] = ''
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        sample = form.save()
        return redirect('sample:sampleedit', pk=sample.pk)


# 改变样板状态到送工厂状态
@o_m_mg_or_required
def samplesentfactory(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    if sample.factory is None:
        messages.warning(request, '请选择工厂并保存后，才能通知工厂!')
    else:
        sample.status = "SENT_F"
        sample.save()
        messages.success(request, '样板已经安排给工厂!')
        factoryemail = str(sample.factory.email)
        try:
            os_avatar_file = sample.os_avatar.file
            encoded = base64.b64encode(open(os_avatar_file.path, "rb").read()).decode()
        except ObjectDoesNotExist:
            encoded = ''
        sender_email = 'SCM<scm@monayoung.com.au>'
        receiver_email = factoryemail
        message = MIMEMultipart("alternative")
        message["Subject"] = "缘色SCM-新样板通知"
        message["From"] = sender_email
        message["To"] = receiver_email
        sampleno =  sample.sample_no
        brand = sample.brand.name
        merchandiser = sample.merchandiser.user.username
        html = f"""\
            <html>
            <body>
            <h3>新样板已安排给工厂,详细信息请看SCM, 尽快联系公司拿原版！</h3>
            <h3>样板号:{sampleno}</h3>
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

 
    return redirect('sample:sampleedit', pk=sample.pk)


# 改变样板状态到已完成状态
@o_m_mg_or_required
def samplecompleted(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    sample.status = "COMPLETED"
    sample.save()
    messages.success(request, '样板已完成!')
    return redirect('sample:sampledetail', pk=sample.pk)

# 重置样板状态到新建状态
@o_m_mg_or_required
def samplereset(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    sample.status = "NEW"
    sample.save()
    messages.success(request, '样板已重置到新建状态!')
    return redirect('sample:sampleedit', pk=sample.pk)

# 样板详情页
@method_decorator([login_required], name='dispatch')
class SampleDetail(UpdateView):
    template_name = 'sample_detail.html'
    model = Sample
    form_class = SampledetailForm
    context_object_name = 'sample'

    def form_valid(self, form):
        sample = form.save()
        return redirect('sample:sampledetail', pk=sample.pk)

    def get_context_data(self, **kwargs):
        kwargs['os_pics'] = self.get_object().os_pics.all()
        kwargs['size_specs'] = self.get_object().size_specs.all()
        kwargs['swatches'] = self.get_object().swatches.all()
        kwargs['fpics'] = self.get_object().factory_pics.all()
        try:
            kwargs['quotation'] = self.get_object().quotation
        except ObjectDoesNotExist:
            pass
        try:
            kwargs['sizespecf'] = self.get_object().sizespecf
        except ObjectDoesNotExist:
            pass
        return super().get_context_data(**kwargs)


# 拷贝样板，测试数据用
@o_m_mg_or_required
def samplecopy(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    sample.pk = None
    sample.save()
    return redirect('sample:sampleedit', pk=sample.pk)


# 删除样板
@method_decorator([login_required, o_m_mg_or_required], name='dispatch')
class SampleDelete(DeleteView):
    model = Sample
    context_object_name = 'sample'
    template_name = 'sample_delete.html'
    success_url = reverse_lazy('sample:samplelistnew')


# 样板附件通用功能视图
@login_required
def sampleattachadd(request, pk, attachtype):
    sample = get_object_or_404(Sample, pk=pk)
    previous_url = request.META.get('HTTP_REFERER')
    if attachtype == 'osavatar':
        if request.FILES:
            try:
                sample.os_avatar.delete()
            except ObjectDoesNotExist:
                pass
            form = SampleosavatarForm(request.POST, request.FILES)
    elif attachtype == 'os_pics':
        form = SampleospicsForm(request.POST, request.FILES)
    elif attachtype == 'sizespecs':
        form = SamplesizespecsForm(request.POST, request.FILES)
    elif attachtype == 'swatch':
        form = SampleswatchForm(request.POST, request.FILES)
    elif attachtype == 'fpics':
        form = SamplefpicsForm(request.POST, request.FILES)
    elif attachtype == 'quotation':
        if request.FILES:
            try:
                sample.quotation.delete()
            except ObjectDoesNotExist:
                pass
            form = SamplequotationForm(request.POST, request.FILES)
    else:
        if request.FILES:
            try:
                sample.sizespecf.delete()
            except ObjectDoesNotExist:
                pass
            form = SamplesizespecfForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            with transaction.atomic():
                attach = form.save(commit=False)
                attach.sample = sample
                attach.save()
                data = {"files": [{
                            "name": attach.file.name,
                            "url": attach.file.url, },
                            ]}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)
    else:
        return render(request, 'sample_attach_add.html', {'sample': sample, 'previous_url': previous_url, 'attachtype': attachtype})


@login_required
def sampleattachdelete(request, pk, attachtype, attach_pk):
    sample = get_object_or_404(Sample, pk=pk)
    previous_url = request.META.get('HTTP_REFERER')
    attachtype = attachtype
    if attachtype == 'osavatar':
        attach = get_object_or_404(Sample_os_avatar, pk=attach_pk)
        attach.delete()
        if 'step2' in previous_url:
            return redirect('sample:sampleaddstep2', pk=sample.pk)
        else:
            return redirect('sample:sampleedit', pk=sample.pk)
    elif attachtype == 'os_pics':
        attach = get_object_or_404(Sample_os_pics, pk=attach_pk)
        attach.delete()
        return redirect('sample:sampleattachcollection', pk=sample.pk, attachtype=attachtype)
    elif attachtype == 'sizespecs':
        attach = get_object_or_404(Sample_size_specs, pk=attach_pk)
        attach.delete()
        if 'step2' in previous_url:
            return redirect('sample:sampleaddstep2', pk=sample.pk)
        else:
            return redirect('sample:sampleedit', pk=sample.pk)
    elif attachtype == 'swatch':
        attach = get_object_or_404(Sample_swatches, pk=attach_pk)
        attach.delete()
        return redirect('sample:sampleattachcollection', pk=sample.pk, attachtype=attachtype)

        return redirect('sample:sampleattachcollection', pk=sample.pk, attachtype=attachtype)
    elif attachtype == 'fpics':
        attach = get_object_or_404(Sample_pics_factory, pk=attach_pk)
        attach.delete()
        return redirect('sample:sampleattachcollection', pk=sample.pk, attachtype=attachtype)

    elif attachtype == 'quotation':
        attach = get_object_or_404(Sample_quotation_form, pk=attach_pk)
        attach.delete()
        if request.user.is_factory:
            return redirect('sample:sampledetail', pk=sample.pk)
        else:
            return redirect('sample:sampleedit', pk=sample.pk)
    else:
        attach = get_object_or_404(Sample_size_spec_factory, pk=attach_pk)
        attach.delete()
        if request.user.is_factory:
            return redirect('sample:sampledetail', pk=sample.pk)
        else:
            return redirect('sample:sampleedit', pk=sample.pk)


@login_required
def sampleattachcollection(request, pk, attachtype):
    sample = get_object_or_404(Sample, pk=pk)
    previous_url = request.META.get('HTTP_REFERER')
    attachtype = attachtype
    if attachtype == 'os_pics':
        attaches = sample.os_pics.all()
    elif attachtype == 'swatch':
        attaches = sample.swatches.all()
    elif attachtype == 'fpics':
        attaches = sample.factory_pics.all()
    else:
        attaches = sample.size_specs.all()
    return render(request, 'sample_attach_collection.html', {'sample': sample,
                  'attachtype': attachtype, 'attaches': attaches, 'previous_url': previous_url})
