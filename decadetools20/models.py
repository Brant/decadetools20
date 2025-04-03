from django.db import models
from django.utils.text import slugify
from django.db.models import Q


def find_slug_matches(obj, slug):
    """
    Return a queryset of instances of the same model as `obj` that share the given `slug`.
    Excludes `obj` itself if it has been saved.
    """
    queryset = obj.__class__.objects.filter(slug=slug)
    if obj.pk:
        queryset = queryset.exclude(pk=obj.pk)
    return queryset


def generate_slug(obj, slug_target, persistant_slug=False):
    """
    Generate a unique slug for `obj` based on `slug_target` field.
    If `persistant_slug` is True and a slug already exists, it is not updated.
    Ensures slug uniqueness by appending a number if needed.
    """
    current_slug = obj.slug
    target_value = getattr(obj, slug_target)

    if current_slug and persistant_slug:
        return current_slug

    base_slug = slugify(target_value)
    slug = base_slug
    num = 1

    while find_slug_matches(obj, slug):
        slug = f"{base_slug}-{num}"
        num += 1

    return slug


# Create your models here.
class LittleSlugger(models.Model):
    """
    Abstract mixin for automatically generating slugs
    """
    slug = models.CharField(max_length=300, editable=False, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(getattr(self, self.get_slug_target()[0] if isinstance(self.get_slug_target(), tuple) else self.get_slug_target()))

    def get_slug_target(self):
        """
        Return slug target and optionally a `persist` flag.
        Example:
            return 'title'
            or
            return ('title', True)
        """
        raise NotImplementedError("Classes inheriting from LittleSlugger must implement get_slug_target()")

    def save(self, *args, **kwargs):
        target = self.get_slug_target()
        if isinstance(target, tuple):
            slug_target, persist = target
        else:
            slug_target, persist = target, True

        self.slug = generate_slug(self, slug_target, persist)
        super().save(*args, **kwargs)
