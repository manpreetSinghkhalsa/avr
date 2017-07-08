from django.core.management.base import BaseCommand
from apps.pin_search import (
    models as pin_search_models
)
from django.core.cache import cache
from django.conf import settings
import csv
import os


class Command(BaseCommand):
    office_name = 'officename'
    pincode = 'pincode'
    type = 'officeType'
    delivery_status = 'Deliverystatus'
    division_name = 'divisionname'
    region_name = 'regionname'
    circle_name = 'circlename'
    taluk = 'Taluk'
    district_name = 'Districtname'
    state_name = 'statename'
    required_headers = {'officename', 'pincode', 'officeType', 'Deliverystatus', 'divisionname',
                        'regionname', 'circlename', 'Taluk', 'Districtname', 'statename'}
    location_key = 'location'

    def add_arguments(self, parser):
        parser.add_argument(self.location_key, nargs='+', type=str)

    def _test_headers(self, headers):
        return set(headers) == self.required_headers

    def handle(self, *args, **options):
        file_path = options[self.location_key][0]
        if os.path.exists(file_path):
            with open(file_path) as csvfile:
                reader = csv.DictReader(csvfile)
                # Check headers
                if self._test_headers(reader.fieldnames):
                    count = 0
                    total_count = 0
                    for row in reader:
                        cache_office_str = '{}{}{}'.format(
                            row[self.office_name].strip().lower().replace(' ', ''),
                            row[self.type].strip(),
                            row[self.delivery_status]
                        )
                        if cache.get(cache_office_str):
                            office_obj_id = cache.get(cache_office_str)
                        else:
                            office_obj, is_created = pin_search_models.Office.objects.get_or_create(
                                name=row[self.office_name].strip().lower(),
                                type=row[self.type].strip(),
                                delivery_status=row[self.delivery_status]
                            )
                            office_obj_id = office_obj.id
                            cache.set(cache_office_str, office_obj.id, None)
                        location_data = {
                            'pincode': row[self.pincode].strip().lower(),
                            'state': row[self.state_name].strip().lower(),
                            'division_name': row[self.division_name].strip().lower(),
                            'region_name': row[self.region_name].strip().lower(),
                            'circle_name': row[self.circle_name].strip().lower(),
                            'taluk': row[self.taluk].strip().lower()
                        }
                        cache_location_str = '{}{}{}{}{}{}'.format(
                            row[self.pincode].strip().lower().replace(' ', ''),
                            row[self.state_name].strip().lower().replace(' ', ''),
                            row[self.division_name].strip().lower().replace(' ', ''),
                            row[self.region_name].strip().lower().replace(' ', ''),
                            row[self.circle_name].strip().lower().replace(' ', ''),
                            row[self.taluk].strip().lower().replace(' ', '')
                        )
                        
                        if cache.get(cache_location_str):
                            location_id = cache.get(cache_location_str)
                        else:
                            location, location_created = pin_search_models.Location.objects.get_or_create(**location_data)
                            cache.set(cache_location_str, location.id, None)
                            location_id = location.id

                        pin_search_models.OfficeLocation.objects.get_or_create(
                            location_id=location_id,
                            office_id=office_obj_id
                        )
                        # Can be optimized with using cache, in order to determine whether we have already created such
                        # object or not
                        count += 1
                        if count == 500:
                            # pin_search_models.OfficeLocation.objects.bulk_create(office_location_bulk)
                            office_location_bulk = []
                            count = 0
                            total_count += 500
                            print 'Created: Office objects: {0}, Office Location objects: {0}'.format(
                                total_count
                            )
                    print '**Objects have been created**'
                else:
                    print 'Headers are not correct, required headers are: {}'.format(self.required_headers)
        else:
            print 'File does not exists at: {}'.format(file_path)
