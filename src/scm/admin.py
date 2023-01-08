from re import search
from django.contrib import admin
from .models import (Sample, User, Style, Brand, Merchandiser, Designer,
                     Factory, Shipping, Qc, Finance, Office, Admin,
                     Merchandiser_Manager, Post, PostAttachment,
                     Sample_os_avatar, Order, Order_color_ratio_qty,
                     Order_size_specs, Invoice, Order_fitting_sample,
                     Mainlabel, Maintag, Additiontag, Packingtype, Order_packing_ctn,
                     Order_packing_status, PShippingsample, PSparebutton,
                     PWashinglabel, PPackingway, Check_item, Check_point, Qc_report,
                    Check_record, Check_record_pics)


admin.site.register(User)
admin.site.register(Sample)
admin.site.register(Style)
admin.site.register(Brand)
admin.site.register(Merchandiser)
admin.site.register(Designer)
admin.site.register(Factory)
admin.site.register(Finance)
admin.site.register(Office)
admin.site.register(Admin)
admin.site.register(Shipping)
admin.site.register(Qc)
admin.site.register(Merchandiser_Manager)
admin.site.register(Post)
admin.site.register(PostAttachment)
admin.site.register(Sample_os_avatar)
admin.site.register(Order)
admin.site.register(Order_color_ratio_qty)
admin.site.register(Order_size_specs)
admin.site.register(Invoice)
admin.site.register(Order_fitting_sample)
admin.site.register(Mainlabel)
admin.site.register(Maintag)
admin.site.register(Additiontag)
admin.site.register(Packingtype)


class Order_packing_ctnAdmin(admin.ModelAdmin):
    list_display = ('order','created_date','ctn_start_no','ctn_end_no')
    search_fields = ('order__po',)

admin.site.register(Order_packing_ctn,Order_packing_ctnAdmin)

class Order_packing_statusAdmin(admin.ModelAdmin):
    list_display = ('order','status',)
    search_fields = ('order__po',)

admin.site.register(Order_packing_status, Order_packing_statusAdmin)
admin.site.register(PShippingsample)
admin.site.register(PSparebutton)
admin.site.register(PWashinglabel)
admin.site.register(PPackingway)
admin.site.register(Check_item)
admin.site.register(Qc_report)
admin.site.register(Check_record)
admin.site.register(Check_record_pics)


class Check_pointAdmin(admin.ModelAdmin):
    # a list of displayed columns name.
    list_display = ['check_item', 'number', 'name', 'description']
admin.site.register(Check_point, Check_pointAdmin)