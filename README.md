# Decade Tools '20's
Useful, miscellaneous django stuff for the 2020's


## Wait for load Admin Mixin
This is useful for fields that may need to be filled in after pushing the save out to a queue.

For example, let's say you have a model that generates an image when saved. That image generation may be better off in a queue (e.g. celery), but if you do a "save and continue editing" on the model, it wouldn't be there right away.

Usage:
```
@admin.register(SomeModel)
class SomeModelAdmin(PendingFieldPollingMixin, admin.ModelAdmin):
    readonly_fields = ['field_name_in_admin', ]
    pending_fields = [
        ('field_name_in_admin', 'field_name_on_model'),
    ]
```
The above allows you to use it for custom fields and readonly fields. Field_name_in_admin may match field_name_on_model if they are the same.

Note: Currently only readonly fields are supported