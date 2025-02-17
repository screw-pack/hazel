from django.contrib import admin
from django.http import HttpResponse
from django.template.defaultfilters import date as _date
import csv
from .models import Period, Booking, Slot, Activity
from registration.models import Child, Category


class ActivityInLine(admin.TabularInline):
    model = Activity
    extra = 1


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'slot')
    ordering = ('-slot',)
    date_hierarchy = 'slot__day'


class BookingInLine(admin.TabularInline):
    model = Booking
    extra = 0


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    date_hierarchy = 'day'
    readonly_fields = ('is_full',)
    inlines = [BookingInLine, ]
    list_filter = ('day',)


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')


class CategoryListFilter(admin.SimpleListFilter):
    """ Custom filter to choose children's category """

    title = ('Groupe')
    parameter_name = 'groupe'

    def lookups(self, request, model_admin):
        categories = Category.objects.all()
        tuples_list = []
        for category in categories:
            tuples_list.append((category.name, (category.name)))

        return tuples_list

    def queryset(self, request, queryset):
        if self.value():
            category = Category.objects.get(name=self.value())
            children = Child.objects.exclude(category=category)
            for child in children:
                queryset = queryset.exclude(child=child)

            return queryset


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('child', 'categorie', 'slot', 'whole', 'validated')
    list_editable = ('whole', 'validated')
    list_filter = ('validated', CategoryListFilter,)
    date_hierarchy = 'slot__day'
    ordering = ('slot__day',)
    actions = ["export_as_csv"]

    def categorie(self, obj):
        """ Custom admin field to display children's categories """

        return obj.child.category

    def save_model(self, request, obj, form, change):
        """ overrided to perform a slot update when added """
        super().save_model(request, obj, form, change)
        slot = Slot.objects.get(booking=obj)
        slot.update_slot()

    def delete_model(self, request, obj):
        """ overrided to perform a slot update when removed one """
        slot = Slot.objects.get(booking=obj)
        super().delete_model(request, obj)
        slot.update_slot()

    def delete_queryset(self, request, queryset):
        """ overrided to perform a slot update when removed several """
        slots = []
        for booking in queryset:
            slot = Slot.objects.get(booking=booking)
            slots.append(slot)
        super().delete_queryset(request, queryset)
        for slot in set(slots):
            slot.update_slot()

    def export_as_csv(self, request, queryset):
        """ Adds the action to export a queryset as a csv file """

        queryset = queryset.exclude(validated=False)

        month = [_date(query.slot.day, 'F') for query in queryset]
        month = '-'.join(set(month))
        year = [_date(query.slot.day, 'Y') for query in queryset]
        year = '-'.join(set(year))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename=fact_{}_{}.csv'.format(month, year)
        )
        writer = csv.writer(response)

        writer.writerow([month, year])
        writer.writerow([])
        writer.writerow(['Redevable', 'Consommateur', 'QF', 'Journée',
                         'Demi-journée'])

        mydict = {}
        for obj in queryset:
            if obj.child not in mydict:
                child = Child.objects.get(id=obj.child.id)
                querychild = queryset.filter(child=child)
                if child.family:
                    quotient = child.family.quotient
                else:
                    quotient = None
                mydict[obj.child] = [
                    child.legal_guardian_1.__str__(),
                    child.__str__(),
                    quotient,
                    querychild.filter(whole=True).count(),
                    querychild.filter(whole=False).count()
                ]

        for key, value in mydict.items():
            writer.writerow(value)

        return response

    description = "Exporter les Réservations sélectionnées au format CSV"
    export_as_csv.short_description = description
