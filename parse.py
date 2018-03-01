import requests
from bs4 import BeautifulSoup as Soup
from bs4.element import Tag, ResultSet
import simplejson as json

_url_regions = 'https://www.olx.pl/sitemap/regions/'
_url_suggest = 'https://www.olx.pl/ajax/geo6/autosuggest/'

_headers = {
    'user-agent': '',
}


def _url_soup(u: str) -> Soup:
    r = requests.get(u, headers=_headers)
    return Soup(r.content, 'lxml')


def _post_suggest(s: str) -> dict:
    r = requests.post(_url_suggest, data=dict(skipDistricts=0, data=s))
    return json.loads(r.content)['data']


def get_all_regions() -> ResultSet:
    p = _url_soup(_url_regions)
    return p.find_all('div', class_='clr marginbott20')


def parse_region(t: Tag) -> dict:
    p = _url_soup(t.a['href'])
    h2 = p.find('div', class_='clr marginbott10')
    links = h2.find_all('a', class_='tdnone')
    return dict(
        Region=p.find('h2').span.text,
        Cities=[{'name': l.span.text, 'link': l['href']} for l in links])


def get_city_id(u: str):
    r = _url_soup(u)
    n = r.find('input', {'name': 'search[city_id]'})['value']
    return n


def _parse_city(d: dict):
    city_id = get_city_id(d['link'])
    suggest = _post_suggest(d['name'])
    print(suggest)
    for s in suggest:
        if s['id'] == city_id:
            return s


if __name__ == '__main__':
    _suggest = list()
    _output = list()

    region_cities_list = [parse_region(r) for r in get_all_regions()]
    for r in region_cities_list:
        app = dict(region_name=r['Region'], cities=[])
        for city in r['Cities']:
            app['cities'].append(_parse_city(city))
        _output.append(app)

    import json
    json.dump(_output, open('miasta_.json', 'w'))
