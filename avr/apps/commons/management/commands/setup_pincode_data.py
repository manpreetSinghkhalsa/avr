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
    required_headers = {office_name, pincode, type, delivery_status, division_name,
                        region_name, circle_name, taluk, district_name, state_name}
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
                    for row in reader:
                        office_obj, is_created = pin_search_models.Office.objects.get_or_create(
                            name=row[self.office_name].strip().lower(),
                            type=row[self.type].strip(),
                            delivery_status=row[self.delivery_status]
                        )
                        location_data = {
                            'pincode': row[self.pincode].strip(),
                            'state': row[self.state_name].strip().lower(),
                            'division_name': row[self.division_name].strip().lower(),
                            'region_name': row[self.region_name].strip().lower(),
                            'circle_name': row[self.circle_name].strip().lower(),
                            'taluk': row[self.taluk].strip().lower()
                        }
                        location, location_created = pin_search_models.Location.objects.get_or_create(**location_data)

                        pin_search_models.OfficeLocation.objects.get_or_create(
                            location=location,
                            office=office_obj
                        )
                        count += 1
                        print 'rows parsed: {}'.format(count)
                    print '**Objects have been created**'
                else:
                    print 'Headers are not correct, required headers are: {}'.format(self.required_headers)
        else:
            print 'File does not exists at: {}'.format(file_path)
