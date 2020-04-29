from django.contrib import messages
from django.db import models
from random import randint
from access.models import AccessSwitch
from closet.models import Closet
from onboard.models import Site
from overview.forms import NavbarForm
from router.models import Router

ERROR_IMAGE_COUNT = 1
HOSTNAME = 'r{device}{country}{crest:0>4}-{closet}-{instance:03}'

MESSAGES = {
    'ACCESS_CREATED': 'New access switch stack was initialized. Please specify the details below.',
    'ACCESS_UPDATED': '',
    'CORE_UPDATED': '',
    'DUPLICATE_VLAN': 'Only one security and voice server VLAN permitted.',
    'SERVER_UPDATED': '',
    'SITE_ONBOARDED': 'Site was successfully onboarded. Please create network closets below.',
    'WAN_UPDATED': '',
}

MODALS = {
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

PLACEHOLDERS = {
    'IP': 'A.B.C.D/n',
    'BW': 'Bandwidth in Mbps'  # TODO: other placeholders
}

DEVICE_TYPES = {
    Router: 'wan',
    AccessSwitch: 'acc',
}


def activate_modal(obj, modal_key):
    obj.modal_display = 'True'  # do something here
    obj.modal_header = MODALS[modal_key]['HEADER']
    obj.modal_body = MODALS[modal_key]['BODY']


def check_hardware_standards(request, crest):
    site_details = get_site_details(crest)
    meeting_standards = True
    for site_detail in site_details:
        if str(request.POST[site_detail]) != str(site_details[site_detail]):
            meeting_standards = False
            break
    return meeting_standards


def generate_error(obj, modal_key):
    activate_modal(obj, modal_key)
    obj.error_file = 'images/error' + \
        str(randint(1, ERROR_IMAGE_COUNT)) + '.jpg'


def get_device_hostname(site_record, closet_record, device, instance=None):
    # TODO: define
    hostname_data = {
        'device': DEVICE_TYPES[device],
        'country': 'us',
        'crest': str(site_record.crest)[-4:],
        'closet': closet_record.closet,
        'instance': instance,
    }
    if not instance:
        hostname_data['instance'] = len(
            device.objects.filter(closet=closet_record)) + 1
    return HOSTNAME.format(**hostname_data)


def get_device_records(device, mdf_closets):
    # TODO: make efficient
    device_records = device.objects.none()
    for mdf_closet in mdf_closets:
        device_records = device_records.union(
            device.objects.filter(closet=mdf_closet))
    return device_records


def get_mdf_closets(closet_records):
    # TODO: make efficient
    mdf_closets = list()
    for closet_record in closet_records:
        if closet_record.category in [Closet.CategoryChoices.MDF, Closet.CategoryChoices.MDF_IDF]:
            mdf_closets.append(closet_record)
    return mdf_closets


def get_mdf_device_hostnames(site_record, mdf_closets, device):
    mdf_device_hostnames = list()
    if len(mdf_closets) == 1:
        mdf_device_hostnames.append(get_device_hostname(
            site_record, mdf_closets[0], device, 1))
        mdf_device_hostnames.append(get_device_hostname(
            site_record, mdf_closets[0], device, 2))
    else:
        mdf_device_hostnames.append(get_device_hostname(
            site_record, mdf_closets[0], device, 1))
        mdf_device_hostnames.append(get_device_hostname(
            site_record, mdf_closets[1], device, 2))
    return mdf_device_hostnames


def get_site_details(crest):
    #TODO: define
    site_details = dict()
    site_details['address'] = 'New York/80 Pine'
    site_details['capacity'] = 800
    site_details['headcount'] = 600
    site_details['network_type'] = Site.NetworkTypeChoices.MICRO_BRANCH
    site_details['nearest_dc'] = Site.NearestDcChoices.AM1
    return site_details


def initialize_navbar(obj, request, site_id=None):
    if site_id:
        site_record = Site.objects.get(id=site_id)
        obj.navbar = NavbarForm(initial={'site': site_record.network_name})
        if site_record.signal_duplicate_vlan:
            messages.error(request, MESSAGES['DUPLICATE_VLAN'])
            site_record.signal_duplicate_vlan = False
        if site_record.signal_updated_access:
            messages.success(request, MESSAGES['ACCESS_CREATED'])
            site_record.signal_updated_access = False
        if site_record.signal_onboarded_site:
            messages.success(request, MESSAGES['SITE_ONBOARDED'])
            site_record.signal_onboarded_site = False
        if site_record.signal_updated_access:
            messages.success(request, MESSAGES['ACCESS_UPDATED'])
        if site_record.signal_updated_core:
            messages.success(request, MESSAGES['CORE_UPDATED'])
        if site_record.signal_updated_server:
            messages.success(request, MESSAGES['SERVER_UPDATED'])
        if site_record.signal_updated_wan:
            messages.success(request, MESSAGES['WAN_UPDATED'])
        site_record.save()
        # TODO: get caller name and display messages
    else:
        site_record = None
        obj.navbar = NavbarForm()
    obj.site_id = site_id
    return site_record


def set_form_errors(request, *forms):
    # TODO: remove duplicates
    for form in forms:
        for error in form.errors.values():
            messages.error(request, error)


def set_formset_errors(request, *formsets):
    # TODO: remove duplicates
    for formset in formsets:
        for form in formset:
            for error in form.errors.values():
                messages.error(request, error)


def set_widget_attributes(fields):
    #TODO: define
    pass
