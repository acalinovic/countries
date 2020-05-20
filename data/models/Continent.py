from django.db import models


class Continent(models.Model):
    wiki_url = models.URLField(verbose_name='Wiki URL')
    name = models.CharField(max_length=128, blank=False, null=False, verbose_name='Name')

    def __str__(self):
        return self.name
