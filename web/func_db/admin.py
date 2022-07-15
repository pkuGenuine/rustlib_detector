from django.contrib import admin

from func_db.models import Bin, Function, Mir

@admin.register(Mir)
class MirAdmin(admin.ModelAdmin):
    pass


admin.site.register(Function)
admin.site.register(Bin)

