from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin

from core.models import TGUser, Budget, TelegramText


class ConsultationFilter(admin.SimpleListFilter):
    title = 'Консультация'
    parameter_name = 'consultation_show'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(consultation__isnull=False)
        if self.value() == 'no':
            return queryset.filter(consultation__isnull=True)


@admin.register(TGUser)
class TGUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'phone', 'age', 'height', 'weight', 'budget', 'questionnaire_completed', 'consultation_show')
    readonly_fields = ('questionnaire_completed',)
    list_filter = ('budget', 'questionnaire_completed', ConsultationFilter)

    @admin.display(boolean=True, description='Консультация')
    def consultation_show(self, obj):
        if obj.consultation:
            return True
        return False
    consultation_show.short_description = 'Консультация'


@admin.register(Budget)
class SortableBudgetAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('amount', 'my_order',)


@admin.register(TelegramText)
class TelegramTextAdmin(admin.ModelAdmin):
    list_display = ('slug', 'text',)
    search_fields = ('text',)