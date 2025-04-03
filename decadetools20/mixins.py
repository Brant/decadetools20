from django.urls import path, reverse
from django.http import JsonResponse
from django.utils.html import format_html
from django import forms

class PendingFieldPollingMixin:
    pending_fields = []

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path(
                'poll-field/<int:object_id>/',
                self.admin_site.admin_view(self.poll_field),
                name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_poll_field'
            )
        ]
        return extra + urls

    def poll_field(self, request, object_id):
        obj = self.get_object(request, object_id)
        response_data = {}

        for display_field, source_field in self.pending_fields:
            value = getattr(obj, source_field, None)
            if callable(value):
                value = value()

            ready = value not in [None, "", "-", False]
            html = self.render_pending_field(obj, display_field)

            response_data[display_field] = {
                'ready': ready,
                'html': html,
            }

        return JsonResponse(response_data)

    def render_pending_field(self, obj, field_name):
        render_func = getattr(self, field_name, lambda o: "-")
        return render_func(obj)



    def render_change_form(self, request, context, *args, **kwargs):
        obj = context.get('original')

        if obj and obj.pk:  # Only inject if we're editing an existing object
            polling_map = {
                field_name: self.get_poll_url(obj.pk)
                for field_name, _ in self.pending_fields
            }
            context['media'] += forms.Media(
                js=['decadetools20/js/pending_field.js'],
                css={'all': ['decadetools20/css/admin.css']}
            )


            # Inject dummy hidden fields so the frontend can pick up the polling config
            context['adminform'].form.fields.update({
                f'_polling_{field_name}': forms.CharField(
                    required=False,
                    widget=forms.HiddenInput(attrs={
                        'data-poll-field': field_name,
                        'data-poll-url': self.get_poll_url(obj.pk)
                    })
                ) for field_name, _ in self.pending_fields
            })

        return super().render_change_form(request, context, *args, **kwargs)


    def get_poll_url(self, object_id):
        return reverse(
            f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_poll_field',
            args=[object_id]
        )

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        readonly_field_names = [f[0] for f in self.pending_fields]

        for field_name in readonly_field_names:
            if field_name not in readonly:
                readonly.append(field_name)

            if not hasattr(self, f'_wrapped_{field_name}'):
                original = getattr(self, field_name, lambda o: "-")

                def wrapped(obj, original=original, field_name=field_name):
                    content = original(obj)
                    
                    # Skip spinner for new objects
                    if not obj.pk:
                        return content

                    if content in [None, "", "-", False]:
                        content = format_html('<div class="poll-spinner"><div class="spinner-circle"></div><span class="spinner-text">Loading…</span></div>')

                    return format_html('<div data-poll-target="{}">{}</div>', field_name, content)



                wrapped.short_description = getattr(original, 'short_description', field_name.replace('_', ' ').title())
                wrapped.allow_tags = True

                # Dynamically assign to the instance so Django uses it
                setattr(self, field_name, wrapped)
                setattr(self, f'_wrapped_{field_name}', True)

        return readonly

