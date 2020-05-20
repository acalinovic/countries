from django.db import models


class CoatOfArms(models.Model):
    wiki_url = models.URLField(verbose_name='Wiki URL')
    name = models.CharField(max_length=128, blank=False, null=False, verbose_name='Name')
    image = models.ImageField(upload_to='coas', verbose_name='Image')
    svg = models.TextField(verbose_name='SVG', blank=True, null=True)

    def __str__(self):
        return self.name
