import re
import requests

from django.core.management.base import BaseCommand

from ...models import KLADRRegion, KLADRCity, KLADRDistrict


class Command(BaseCommand):
    help = 'Common Report command'

    def handle(self, *args, **options):
        parsed_data = self.fetch_data()
        self.update_data_in_db(parsed_data)
        print(parsed_data)

    def update_data_in_db(self, parsed_data):
        for region_data in parsed_data:
            region = KLADRRegion.objects.update_or_create(
                name=region_data['name'], defaults={
                    'region_code': region_data['region_code'],
                    'post_index': region_data['post_index'],
                    'code_okato': region_data['code_okato'],
                    'tax_code': region_data['tax_code'],
                    'code_kladr': region_data['code_kladr'],
                }
            )
            cities_list = region_data.get('cities')
            if cities_list:
                self.update_cities_in_db(cities_list, region)
            districts_list = region_data.get('districts')
            if districts_list:
                self.update_districts_in_db(districts_list, region)

    @staticmethod
    def update_cities_in_db(cities_list, region):
        for city_data in cities_list:
            KLADRCity.objects.update_or_create(
                name=city_data['name'], region=region, defaults={
                    'post_index': city_data['post_index'],
                    'code_okato': city_data['code_okato'],
                    'tax_code': city_data['tax_code'],
                    'code_kladr': city_data['code_kladr'],
                }
            )

    @staticmethod
    def update_districts_in_db(districts_list, region):
        for district_data in districts_list:
            KLADRDistrict.objects.update_or_create(
                name=district_data['name'], region=region, defaults={
                    'post_index': district_data['post_index'],
                    'code_okato': district_data['code_okato'],
                    'tax_code': district_data['tax_code'],
                    'code_kladr': district_data['code_kladr'],
                }
            )

    # Возвращает список регионов и городовы
    def fetch_data(self):
        page_content = self.fetch_content_from_url('https://kladr-rf.ru/')
        regions_raw_list = re.findall(
            r'<a href="https://kladr-rf.ru/\d+/">.*?</a>', page_content
        )

        regions_list = []
        for raw_link in regions_raw_list:
            url, name = raw_link.replace('<a href="', '').replace('</a>', '').split('">')
            region_data = self.fetch_region_info(url, name)
            regions_list.append(region_data)
            print(region_data)
        return regions_list

    # получение информации о регионе и списка городов
    def fetch_region_info(self, region_url, region_name):
        page_content = self.fetch_content_from_url(region_url)

        parse_districts = ' Город' in region_name

        # получение общей информации
        region_data = self.parse_common_info(page_content)
        region_data['name'] = self.replace_prefix(region_name)

        if parse_districts:
            # получение списка районов
            search_pattern = r'<a href="{}\d+/">.*?</a>'.format(region_url)
        else:
            # получение списка городов
            search_pattern = r'<a href="{}000/\d+/">.*?</a>'.format(region_url)

        cities_raw_list = re.findall(search_pattern, page_content)
        cities_list = []
        for raw_link in cities_raw_list:
            url, name = raw_link.replace('<a href="', '').replace('</a>', '').split('">')
            city_data = self.fetch_city_info(url, name)
            cities_list.append(city_data)

        if parse_districts:
            region_data['districts'] = cities_list
        else:
            region_data['cities'] = cities_list
        return region_data

    # получение информации о городе
    def fetch_city_info(self, url, name):
        page_content = self.fetch_content_from_url(url)
        city_data = self.parse_common_info(page_content)
        city_data['name'] = self.replace_prefix(name)
        return city_data

    @staticmethod
    def fetch_content_from_url(url):
        response = requests.get(url)
        if not response.status_code == 200:
            raise RuntimeError('Unexpected status code: {}, for url: '.format(
                response.status_code, url
            ))
        return response.content.decode('utf-8')

    # получение общей информации
    # код кладр, код региона, почтовый индекс, код окато, код налоговой
    def parse_common_info(self, page_content):
        code_kladr = self.parse_code_kladr(page_content)

        table_string = re.search('<tbody>.*?</tbody>', page_content).group(0)
        table_string = table_string.replace(
            '<tbody><tr><td>', ''
        ).replace(
            '</td></tr></tbody>', ''
        )
        table_columns = table_string.split('</td><td>')
        return {
            'region_code': table_columns[0],
            'post_index': table_columns[1],
            'code_okato': table_columns[2],
            'tax_code': table_columns[3],
            'code_kladr': code_kladr
        }

    @staticmethod
    def parse_code_kladr(page_content):
        return re.search(
            r'Код КЛАДР: <strong><em>\d+</em>', page_content
        ).group(0).replace('Код КЛАДР: <strong><em>', '').replace('</em>', '')

    # удаление префиксов из имени субъектов
    @staticmethod
    def replace_prefix(name):
        prefix_list = [' Город', ' Поселение', ' Деревня', ' Поселок', ' Село']
        for prefix in prefix_list:
            name = name.replace(prefix, '')
        return name
