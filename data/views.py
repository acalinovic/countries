import re
import requests
from django.db.models import Model
from django.http import HttpResponse
from django.shortcuts import render
from bs4 import BeautifulSoup
from bs4.element import Tag
from data.models import *
from django.core import files
from io import BytesIO

WIKI_PREFIX = 'https://fr.wikipedia.org'
WIKI_COMMON_PREFIX = 'https://commons.wikimedia.org'


def load_wiki_page(url: str):
    data_source_url = WIKI_PREFIX + url
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    source = requests.get(data_source_url, headers=headers).text
    soup = BeautifulSoup(source, 'html.parser')
    return soup


def load_wiki_file(url: str):
    data_source_url = WIKI_COMMON_PREFIX + re.sub('Fichier', 'File', url) + '?uselang=fr'
    # print('load_wiki_file.data_source_url::' + str(data_source_url))
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    source = requests.get(data_source_url, headers=headers).text
    soup = BeautifulSoup(source, 'html.parser')
    return soup


def load_image(url: str):
    resp = requests.get(url)
    if resp.status_code != requests.codes.ok:
        pass
    fp = BytesIO()
    fp.write(resp.content)
    file_name = url.split("/")[-1]  # There's probably a better way of doing this but this is just a quick example
    file = files.File(fp, name=file_name)
    return {'file_name': file_name, 'file': file}


def load_continent(a: Tag):
    return Continent.objects.get_or_create(wiki_url=WIKI_PREFIX + a['href'], name=a['title'])[0]


def load_flag(a):
    soup = load_wiki_file(a)
    url = soup.find('div', attrs={'id': 'file'}).a.img['src']
    flag_data = load_image(url)
    return Flag.objects.get_or_create(name=flag_data['file_name'], wiki_url=url, image=flag_data['file'], svg=None)[0]


def load_coa(a):
    soup = load_wiki_file(a)
    coa_data = dict()
    url = 'empty'
    # if not a.find('.png'):
    #     return CoatOfArms.objects.get_or_create(name='svg', wiki_url='url/')[0]
    #
    # elif soup.find('div', attrs={'id': 'file'}).a.img['src']:
    #     url = soup.find('div', attrs={'id': 'file'}).a.img['src']
    #     coa_data = load_image(url)
    # else:
    coa_data['file_name'] = 'empty'
    coa_data['file'] = None
    return CoatOfArms.objects.get_or_create(name=coa_data['file_name'], wiki_url=url, image=coa_data['file'], svg=None)[0]


def load_currency(a):
    soup = load_wiki_page(a)
    name = re.sub(r' \(.*\)', '', soup.find('h1', attrs={'id': 'firstHeading'}).text)
    code = soup.find('a', attrs={'title': 'ISO 4217'}).parent.parent.find('code').text
    # rate_soup = load_wiki_page(soup.find('a', attrs={'title', 'Taux de change'}).parent.parent.td.a['href'])
    rate = 1
    return Currency.objects.get_or_create(name=name, wiki_url=a, ISO_4217=code, rate=rate)[0]


def load_land(a):
    soup = load_wiki_page(a['href'])
    '''
    <a href="/wiki/Liste_des_capitales_du_monde" title="Liste des capitales du monde">Capitale</a>
    '''
    name = soup.find('h1', attrs={'id': 'firstHeading'}).text
    capital = soup.find('a', attrs={'href': '/wiki/Liste_des_capitales_du_monde'}).parent.parent.td.a.text
    surface = soup.find('th', string='Superficie totale').parent.td
    surface.a.decompose()
    # surface.br.decompose()
    surface.a.decompose()
    surface = re.sub(r'[^0-9]', '', surface.text)
    population = soup.find('a', attrs={'href': '/wiki/Recensement_de_la_population'}).parent.parent.td
    population.a.decompose()
    population.abbr.decompose()
    population = re.sub(r'[^0-9]', '', population.text)
    demonym = soup.find('a', attrs={'title': 'Gentilé'}).parent.parent.td
    if soup.find('a', attrs={'title': 'Gentilé'}).parent.parent.td.br is None:
        demonym = re.sub(r'[\r\n]', '', soup.find('a', attrs={'title': 'Gentilé'}).parent.parent.td.text)
    else:
        demonym.br.replace_with(', ')
        demonym = demonym.text
    demonym = re.sub(r'\[.*\]', '', demonym)
    # currency_url = soup.find('a', attrs={'title': 'Monnaie'}).parent.parent.td.a['href']
    # currency = load_currency(currency_url)
    # currency_code = soup.find('a', attrs={'title': 'ISO 4217'}).code.text
    flag_url = soup.find('a', attrs={'title': 'Drapeau'})['href']
    flag = load_flag(flag_url)
    coa_url = soup.find('a', attrs={'title': 'Blason'})['href']
    coa = load_coa(coa_url)
    print('name: ' + str(name))
    print('capital: ' + str(capital))
    print('surface: ' + surface)
    print('population: ' + population)
    print('demonym: ' + demonym)
    print('flag: ' + str(flag))
    print('coa: ' + str(coa))
    land = Land(name=str(name), capital=capital, surface=surface, population=population, demonym=demonym)
    return {'land': land, 'flag': flag, 'coa': coa, 'currency': None}


def load_all_data(request):
    data_source_url = '/wiki/Liste_des_%C3%89tats_membres_des_Nations_unies'
    page = load_wiki_page(data_source_url)
    data = page.caption.parent.find_all('a')
    idx = 1
    land_link = None
    for a in data:
        if (idx - 6) % 6 == 1:
            pass
            # flag = load_flag(a['href'])
            # print(str(flag))
        # Land link
        if (idx - 1) % 6 == 1:
            print(a['href'])
            land_link = a
        # Continent link
        elif (idx - 5) % 6 == 1:
            land_data = load_land(land_link)
            land = land_data['land']
            land.continent = load_continent(a)
            land.flag = land_data['flag']
            land.coat_of_arms = land_data['coa']
            land.currency = land_data['currency']
            land.save()
        idx += 1
        land_data = None
    return HttpResponse(data)
