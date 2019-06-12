import inspect
import json
import sys

from base import settings
from django import forms
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import TO_FIELD_VAR, IS_POPUP_VAR, get_content_type_for_model
from django.contrib.admin.utils import unquote, flatten_fieldsets
from django.core.exceptions import PermissionDenied
from django.db.models.fields import related_descriptors
from django.forms import all_valid
from django.template.response import TemplateResponse
from django.utils.text import capfirst
from django.utils.translation import gettext as _


def get_classes(_name):
    return [obj for name, obj in inspect.getmembers(sys.modules[_name], inspect.isclass)
            if obj.__module__ is _name]


RELATED_FIELD_CLASS = get_classes(related_descriptors.__name__)


class CustomForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CustomForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if hasattr(field, 'queryset'):
                for field_name, _type in field.queryset.model.__dict__.items():
                    if type(_type) in RELATED_FIELD_CLASS:
                        if '_set' not in field_name:
                            field.queryset = field.queryset.select_related(field_name)


class CustomAdmin(admin.ModelAdmin):
    form = CustomForm

    def get_queryset(self, request):
        qs = super(CustomAdmin, self).get_queryset(request)
        qs = qs.select_related(*self.related_fields)
        return qs

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        js = ['bootstrap/jquery.min.js']
        if self.filter_vertical or self.filter_horizontal:
            js.extend(['SelectBox.js', 'SelectFilter2.js'])
        if self.classes and 'collapse' in self.classes:
            js.append('collapse%s.js' % extra)
        return forms.Media(js=['admin/js/%s' % url for url in js])

    # override this to enable tracking old and new value
    def _changeform_view(self, request, object_id, form_url, extra_context):
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

        model = self.model
        opts = model._meta

        if request.method == 'POST' and '_saveasnew' in request.POST:
            object_id = None

        add = object_id is None

        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None

        else:
            obj = self.get_object(request, unquote(object_id), to_field)

            if not self.has_view_or_change_permission(request, obj):
                raise PermissionDenied

            if obj is None:
                return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        ModelForm = self.get_form(request, obj, change=not add)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            form_validated = form.is_valid()
            # on save
            if form_validated:
                new_object = self.save_form(request, form, change=not add)
            else:
                new_object = form.instance
            formsets, inline_instances = self._create_formsets(request, new_object, change=not add)
            # on update
            if all_valid(formsets) and form_validated:
                try:
                    # must not fail when there's an error getting the old object
                    old_object = new_object.__class__.objects.get(pk=new_object.pk)
                except Exception:
                    pass
                self.save_model(request, new_object, form, not add)
                self.save_related(request, form, formsets, not add)
                change_message = self.construct_change_message(request, form, formsets, add)

                if len(change_message) > 0:
                    changes = change_message[0].get('changed')
                    if changes:
                        changes['old_values'] = []
                        changes['new_values'] = []
                        changed_fields = changes['fields']
                        for changed_field in changed_fields:
                            try:
                                # when we failed to get the old object or there's an error, silently continue
                                old = getattr(old_object, changed_field)
                                new = getattr(new_object, changed_field)
                                changes['old_values'].append(str(old))
                                changes['new_values'].append(str(new))
                            except Exception:
                                pass

                if add:
                    self.log_addition(request, new_object, change_message)
                    return self.response_add(request, new_object)
                else:
                    self.log_change(request, new_object, change_message)
                    return self.response_change(request, new_object)
            else:
                form_validated = False
        else:
            if add:
                initial = self.get_changeform_initial_data(request)
                form = ModelForm(initial=initial)
                formsets, inline_instances = self._create_formsets(request, form.instance, change=False)
            else:
                form = ModelForm(instance=obj)
                formsets, inline_instances = self._create_formsets(request, obj, change=True)

        if not add and not self.has_change_permission(request, obj):
            readonly_fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        else:
            readonly_fields = self.get_readonly_fields(request, obj)
        adminForm = helpers.AdminForm(
            form,
            list(self.get_fieldsets(request, obj)),
            # Clear prepopulated fields on a view-only form to avoid a crash.
            self.get_prepopulated_fields(request, obj) if add or self.has_change_permission(request, obj) else {},
            readonly_fields,
            model_admin=self)
        media = self.media + adminForm.media

        inline_formsets = self.get_inline_formsets(request, formsets, inline_instances, obj)
        for inline_formset in inline_formsets:
            media = media + inline_formset.media

        if add:
            title = _('Add %s')
        elif self.has_change_permission(request, obj):
            title = _('Change %s')
        else:
            title = _('View %s')
        context = {
            **self.admin_site.each_context(request),
            'title': title % opts.verbose_name,
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            'to_field': to_field,
            'media': media,
            'inline_admin_formsets': inline_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'preserved_filters': self.get_preserved_filters(request),
        }

        # Hide the "Save" and "Save and continue" buttons if "Save as New" was
        # previously chosen to prevent the interface from getting confusing.
        if request.method == 'POST' and not form_validated and "_saveasnew" in request.POST:
            context['show_save'] = False
            context['show_save_and_continue'] = False
            # Use the change template instead of the add template.
            add = False

        context.update(extra_context or {})

        return self.render_change_form(request, context, add=add, change=not add, obj=obj, form_url=form_url)

    # override this to display changed value information
    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
        # First check if the user can see this history.
        model = self.model
        obj = self.get_object(request, unquote(object_id))
        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, model._meta, object_id)

        if not self.has_view_or_change_permission(request, obj):
            raise PermissionDenied

        # Then get the history for this object.
        opts = model._meta
        app_label = opts.app_label
        _action_list = LogEntry.objects.filter(
            object_id=unquote(object_id),
            content_type=get_content_type_for_model(model)
        ).select_related().order_by('action_time')
        action_list = []
        for item in _action_list:
            msg = json.loads(item.change_message)
            if len(msg) > 0 and msg[0].get('changed'):
                changes = msg[0]['changed']
                item.changed_fields = \
                    f"{changes['old_values']} to {changes['new_values']}" if changes.get('old_values') else '-'
            else:
                item.changed_fields = '-'
            action_list.append(item)

        context = {
            **self.admin_site.each_context(request),
            'title': _('Change history: %s') % obj,
            'action_list': action_list,
            'module_name': str(capfirst(opts.verbose_name_plural)),
            'object': obj,
            'opts': opts,
            'preserved_filters': self.get_preserved_filters(request),
            **(extra_context or {}),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(request, self.object_history_template or [
            "admin/%s/%s/object_history.html" % (app_label, opts.model_name),
            "admin/%s/object_history.html" % app_label,
            "admin/object_history.html"
        ], context)
