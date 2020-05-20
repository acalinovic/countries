from django.db import models


class Currency(models.Model):
    wiki_url = models.URLField(verbose_name='Wiki URL')
    name = models.CharField(max_length=128, blank=False, null=False, verbose_name='Name')
    symbol = models.CharField(max_length=8, verbose_name='Symbol')
    ISO_4217 = models.CharField(max_length=8, blank=False, null=False, verbose_name='International Code')
    rate = models.FloatField(blank=False, verbose_name='Rate')

    def __str__(self):
        return self.name
