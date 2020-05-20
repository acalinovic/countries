from django.db import models
from data.models import Flag, Continent, Currency, CoatOfArms


class Land(models.Model):
    wiki_url = models.URLField(verbose_name='Wiki URL')
    flag = models.ForeignKey('Flag', on_delete=models.CASCADE, verbose_name='Flag')
    coat_of_arms = models.ForeignKey('CoatOfArms', on_delete=models.CASCADE, verbose_name='Coat of Arms', null=True, blank=True)
    continent = models.ForeignKey('Continent', on_delete=models.DO_NOTHING, verbose_name='Continent')
    currency = models.ForeignKey('Currency', on_delete=models.DO_NOTHING, verbose_name='Currency', null=True, blank=True)
    name = models.CharField(max_length=128, blank=False, null=False, verbose_name='Name')
    capital = models.CharField(max_length=128, blank=False, null=False, verbose_name='Capital')
    demonym = models.CharField(max_length=128, blank=False, null=False, verbose_name='Demonym')
    surface = models.BigIntegerField(blank=False, null=False, verbose_name='Surface')
    population = models.BigIntegerField(blank=False, null=False, verbose_name='Population')

    def __str__(self):
        return self.name
