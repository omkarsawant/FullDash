from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from random import randint
from closets.models import Closets
from overview.forms import Navbar
from overview.models import Overview
from router.models import Router

ERROR_IMAGE_COUNT = 1
HOSTNAME = 'r{device}{country}{crest:0>4}-{closet}-{instance:03}'

modals = {
    'NO_CLOSETS': {
        'HEADER': '''Closets Closets Closets Closets''',
        'BODY': '''No closets have been defined for this network''',
    },
    'NO_MDF': {
        'HEADER': '''No MDFs Defined''',
        'BODY': '''The site does not have any MDFs defined.''',
    },
    'NON_STANDARD': {
        'HEADER': '''Non-Standard Network Build''',
        'BODY': '''The options you have selected do not conform to the latest standards. Please click 'Confirm Non-Standard Network'  to confirm network creation''',
    },
    'WAN_GREEN_SUCCESS': {
        'HEADER': '''Build successful''',
        'BODY': '''Done!''',
    },
}

device_types = {
    Router: 'wan',
}


def activate_modal(obj, modal_key):
    obj.modal_display = 'True'  # do something here
    obj.modal_header = modals[modal_key]['HEADER']
    obj.modal_body = modals[modal_key]['BODY']


def generate_error(obj, modal_key):
    activate_modal(obj, modal_key)
    obj.error_file = 'images/error' + \
        str(randint(1, ERROR_IMAGE_COUNT)) + '.jpg'


def get_device_hostname(overview_record, closet, device, instance=None):
    # TODO: define
    hostname_data = {
        'device': device_types[device],
        'country': 'us',
        'crest': str(overview_record.crest)[-4:],
        'closet': '003a',
        'instance': instance,
    }
    if not instance:
        pass
    return HOSTNAME.format(**hostname_data)


def get_device_records(device, mdf_closets):
    device_records = device.objects.none()
    for mdf_closet in mdf_closets:
        device_records = device_records.union(
            device.objects.filter(closet=mdf_closet))
    return device_records


def get_mdf_closets(closets_records):
    mdf_closets = list()
    for closet_record in closets_records:
        if closet_record.category in [Closets.CategoryChoices.MDF, Closets.CategoryChoices.MDF_IDF]:
            mdf_closets.append(closet_record)
    return mdf_closets


def get_mdf_device_hostnames(overview_record, mdf_closets, device):
    mdf_device_hostnames = list()
    if len(mdf_closets) == 1:
        mdf_device_hostnames.append(get_device_hostname(
            overview_record, mdf_closets[0], device, 1))
        mdf_device_hostnames.append(get_device_hostname(
            overview_record, mdf_closets[0], device, 2))
    else:
        mdf_device_hostnames.append(get_device_hostname(
            overview_record, mdf_closets[0], device, 1))
        mdf_device_hostnames.append(get_device_hostname(
            overview_record, mdf_closets[1], device, 2))
    return mdf_device_hostnames


def get_site_details(crest):
    site_details = dict()
    site_details['address'] = 'New York / 80 Pine'
    site_details['capacity'] = 800
    site_details['headcount'] = 600
    site_details['nearest_dc'] = Overview.NearestDcChoices.AM1
    return site_details


def initialize_navbar(obj, overview_id):
    overview_record = get_object_or_404(Overview, id=overview_id)
    obj.navbar = Navbar(initial={'site': overview_record.crest})
    obj.overview_id = overview_id
    return overview_record
