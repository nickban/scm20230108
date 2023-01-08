from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import (TemplateView,
                                  CreateView, ListView, UpdateView, DetailView,
                                  DeleteView)
from scm.models import (User, Post, PostAttachment, Sample, Sample_os_pics,
                     Sample_size_specs, Sample_os_avatar,
                     Sample_swatches, Sample_quotation_form,
                     Sample_pics_factory, Sample_size_spec_factory)
from scm.forms import (SignUpForm, NewpostForm, PostAttachmentForm,
                    NewsampleForm, SampleForm, SamplesizespecsForm,
                    SampleosavatarForm, SampleospicsForm,
                    SampleswatchForm, SamplefpicsForm,
                     SampledetailForm)
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import reverse_lazy
from scm.decorators import office_required, merchandiser_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib import messages


# Post 部分试图定义


@method_decorator([login_required], name='dispatch')
class PostList(ListView):
    model = Post
    ordering = ('-create_time', )
    context_object_name = 'posts'
    template_name = 'post_list.html'
    queryset = Post.objects.all()


@method_decorator([login_required, office_required], name='dispatch')
class PostAdd(CreateView):
    model = Post
    form_class = NewpostForm
    template_name = 'post_add.html'


@login_required
@office_required
def postattach(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                attach = form.save(commit=False)
                attach.post = post
                attach.save()
                data = {"files": [{
                        "name": attach.file.name,
                        "url": attach.file.url, },
                        ]}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)
    else:
        return render(request, 'post_attach.html', {'post': post})


@method_decorator([login_required, office_required], name='dispatch')
class PostEdit(UpdateView):
    model = Post
    fields = ['title', 'content', 'created_by', 'catagory']
    template_name = 'post_edit.html'
    context_object_name = 'post'
    success_url = reverse_lazy('post:postlist')

    def get_context_data(self, **kwargs):
        kwargs['attachments'] = self.get_object().postattachments.all()
        return super().get_context_data(**kwargs)


@method_decorator([login_required], name='dispatch')
class PostDetail(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        kwargs['attachments'] = self.get_object().postattachments.all()
        return super().get_context_data(**kwargs)


@method_decorator([login_required, office_required], name='dispatch')
class PostDelete(DeleteView):
    model = Post
    context_object_name = 'post'
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post:postlist')


@method_decorator([login_required, office_required], name='dispatch')
class PostAttachDelete(DeleteView):
    model = PostAttachment
    pk_url_kwarg = 'postattach_pk'
    context_object_name = 'postattach'
    template_name = 'post_attach_delete.html'

    def get_success_url(self):
        post = self.object.post
        return reverse_lazy('post:postedit', kwargs={'pk': post.pk})

# 附件删除
@login_required
@office_required
def postattachdelete(request, pk, postattach_pk):
    post = get_object_or_404(Post, pk=pk)
    postattach = get_object_or_404(PostAttachment, pk=postattach_pk)
    postattach.delete()
    return redirect('post:postedit', pk=post.pk)