from django.db import models


class Category(models.Model):
    class Meta:
        unique_together = (('name',))

    name = models.CharField(max_length=1024)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='children')
