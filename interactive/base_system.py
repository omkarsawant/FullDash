from django.contrib import messages
from django.db import models
from random import randint
from access.models import AccessSwitch
from closet.models import Closet
from onboard.models import Site
from overview.forms import NavbarForm
from router.models import Router
from .settings import BASE_DIR
from csv import DictReader

ERROR_IMAGE_COUNT = 1

HOSTNAME = 'r{device}{country}{crest:0>4}-{closet}-{instance:03}'
INTERFACE_DESCRIPTION = '{mode}|{type}|{carrier}|{circuit_id}|{remote_device}|{remote_port}|{user_note}'

COMMUNITIES = {
    'AM1': '1900:1',
    'AM2': '1900:1',
}

DIRECTORIES = {
    'config': '/static/config/',
    'diagrams': '/static/diagrams/',
    'ipam': '/static/ipam/',
    'site': '/static/site/',
    'staging': '/static/staging/',
}

ERRORS = {
    'no_site': {
        'type': 'error',
        'message': 'Site was not found for the given CREST. Please try again.'
    },
    'illegal_site': {
        'type': 'error',
        'message': 'EMPTY_MESSAGE'
    },
    'mdf_limit_exceeded': {
        'type': 'error',
        'message': 'A site cannot have more than 2 MDFs.'
    },
    '4331_idf_limit_exceeded': {
        'type': 'error',
        'message': 'A site with ISR 4331s cannot have more than 1 IDF.'
    },
    '4351_idf_limit_exceeded': {
        'type': 'error',
        'message': 'A site with ISR 4351s cannot have more than 2 IDF'
    },
}

MESSAGES = {
    'ACCESS_CREATED': 'New access switch stack was initialized. Please specify the details below.',
    'ACCESS_UPDATED': '',
    'CORE_UPDATED': '',
    'DUPLICATE_VLAN': 'Only one security and voice server VLAN permitted.',
    'NO_ACCESS_STACK': 'No access stacks have been defined for this site.',
    'NO_CLOSET': 'No closets have been defined for this site.',
    'NO_SUBNET': 'The subnets requested for the site cannot be accommodated by the supernets.',
    'NO_SUPERNET': 'The site does not have any supernets assigned to it.',
    'NO_ROUTER': 'No routers have been defined for this site.',
    'OVERLAPPING_ACCESS': 'Warning: Access Switch has overlapping port assingments',
    'SERVER_UPDATED': '',
    'SITE_ONBOARDED': 'Site was successfully onboarded. Please create network closets below.',
    'SUCCESS': 'Site built successfully.',
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
        'BODY': 'The options you have selected do not conform to the latest standards.\nPlease click "Confirm Non-Standard Network" to confirm network creation',
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

QOS_POLICIES = {
    'WAN Ingress': 'CLASSIFY',
    'WAN Egress': 'WAN_Shape',
    'LAN Ingress': 'Egress_Buffers'
}


def activate_modal(obj, modal_key):
    obj.modal_display = 'True'  # do something here
    obj.modal_header = MODALS[modal_key]['HEADER']
    obj.modal_body = MODALS[modal_key]['BODY']


def adjust_hostnames(device, closet_record):
    device_records = device.objects.filter(closet=closet_record)
    for device_record in device_records:
        device_hostname_parts = device_record.hostname.split('-')
        device_record.hostname = device_hostname_parts[0] + '-' + \
            closet_record.closet + '-' + device_hostname_parts[2]
        device_record.save()


def check_hardware_standards(request, crest):
    site_details = get_site_details(crest)
    meeting_standards = True
    for site_detail in site_details:
        if str(request.POST[site_detail]) != str(site_details[site_detail]):
            meeting_standards = False
            break
    return meeting_standards


def check_illegal_configuration(request):
    illegal_scan_result = ''
    if request.POST['router'] == Site.RouterChoices.ISR_4331:
        if request.POST['core'] != Site.CoreChoices.NO_CORE or request.POST['server'] != Site.ServerChoices.NO_SERVER:
            illegal_scan_result = 'A site with ISR 4331 cannot have core or server switches'
    if request.POST['server'] != Site.ServerChoices.NO_SERVER and request.POST['core'] == Site.CoreChoices.NO_CORE:
        illegal_scan_result = 'Server switch layer cannot be present without a core switch layer'
    return illegal_scan_result


def delete_extra_devices(device, closet_records):
    extra_device_records = device.objects.filter(closet__in=closet_records)
    for extra_device_record in extra_device_records:
        extra_device_record.delete()


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


def get_filename(crest, filetype):
    if filetype == 'visio':
        return str(crest) + '-Network Diagram.vsdx'
    elif filetype == 'ipam':
        return str(crest) + '-IPAM Request.xlsx'
    elif filetype == 'zip':
        return str(crest) + '-GDA2 Documents.zip'


def get_interface_description(intr_type, **tokens):
    interface_description_data = {
        'mode': '-',
        'type': '-',
        'carrier': '-',
        'circuit_id': '-',
        'remote_device': '-',
        'remote_port': '-',
        'user_note': '-',
    }
    if intr_type == 'access':
        interface_description_data['mode'] = 'l2'
        interface_description_data['type'] = 'acc'
        if tokens['access_vlan'] > 299 and tokens['access_vlan'] < 399:
            if tokens['voice_vlan']:
                interface_description_data['user_note'] = 'user port'
            else:
                interface_description_data['user_note'] = 'data port'
        elif tokens['access_vlan'] == 399:
            interface_description_data['user_note'] = 'security port'
        elif tokens['access_vlan'] > 399 and tokens['access_vlan'] < 499:
            interface_description_data['user_note'] = 'voice device port'
        elif tokens['access_vlan'] == 499:
            interface_description_data['user_note'] = 'voice infrastructure port'
        elif tokens['access_vlan'] > 699 and tokens['access_vlan'] < 800:
            interface_description_data['user_note'] = 'server port'
    elif intr_type == 'l3_p2p':
        interface_description_data['mode'] = 'l3'
        interface_description_data['type'] = 'p2p'
        interface_description_data['remote_device'] = tokens['remote_device'].lower(
        )
        interface_description_data['remote_port'] = tokens['remote_port'].lower(
        )
    elif intr_type == 'loop':
        interface_description_data['mode'] = 'l3'
        interface_description_data['type'] = 'rtid'
        interface_description_data['user_note'] = 'inband-mgt'
    elif intr_type == 'vlan':
        interface_description_data['mode'] = 'l3'
        interface_description_data['type'] = 'vlan'
        interface_description_data['user_note'] = tokens['vlan_note'].lower()
    elif intr_type == 'wan':
        interface_description_data['mode'] = 'l3'
        interface_description_data['type'] = tokens['wan_type'].lower()
        interface_description_data['carrier'] = tokens['wan_provider'].lower()
        interface_description_data['circuit_id'] = tokens['circuit_id'].lower(
        )
    return INTERFACE_DESCRIPTION.format(**interface_description_data)


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
            site_record, mdf_closets[1], device, 1))
    return mdf_device_hostnames


def get_site_details(crest):
    site_details = {}
    site_database_file = open(
        BASE_DIR + DIRECTORIES['site'] + 'sites_database.csv', encoding='cp1252')
    sites_database = DictReader(site_database_file)
    for record in sites_database:
        if int(record['crest']) == crest:
            capacity = int(record['capacity'])
            floors = int(record['floors'])
            site_details['address'] = record['address']
            site_details['capacity'] = capacity
            site_details['headcount'] = int(record['headcount'])
            site_details['nearest_dc'] = record['nearest_dc']
            if capacity < 11:
                site_details['network_type'] = Site.NetworkTypeChoices.MICRO_BRANCH
                site_details['router'] = Site.RouterChoices.ISR_4331
                site_details['core'] = Site.CoreChoices.NO_CORE
                site_details['server'] = Site.ServerChoices.NO_SERVER
            elif capacity < 31:
                site_details['network_type'] = Site.NetworkTypeChoices.MINI_BRANCH
                site_details['router'] = Site.RouterChoices.ISR_4331
                site_details['core'] = Site.CoreChoices.NO_CORE
                site_details['server'] = Site.ServerChoices.NO_SERVER
            elif capacity < 101:
                site_details['network_type'] = Site.NetworkTypeChoices.SMALL_BRANCH
                site_details['router'] = Site.RouterChoices.ISR_4331
                site_details['core'] = Site.CoreChoices.NO_CORE
                site_details['server'] = Site.ServerChoices.NO_SERVER
            elif capacity < 151 and floors < 2:
                site_details['network_type'] = Site.NetworkTypeChoices.SMALL_BRANCH
                site_details['router'] = Site.RouterChoices.ISR_4331
                site_details['core'] = Site.CoreChoices.NO_CORE
                site_details['server'] = Site.ServerChoices.NO_SERVER
            elif capacity < 301 and floors < 3:
                site_details['network_type'] = Site.NetworkTypeChoices.MEDIUM_BRANCH_1
                site_details['router'] = Site.RouterChoices.ISR_4351
                site_details['core'] = Site.CoreChoices.NO_CORE
                site_details['server'] = Site.ServerChoices.NO_SERVER
            elif capacity < 301 and floors < 11:
                site_details['network_type'] = Site.NetworkTypeChoices.MEDIUM_BRANCH_2
                site_details['router'] = Site.RouterChoices.ISR_4351
                site_details['core'] = Site.CoreChoices.CATALYST_9500
                site_details['server'] = Site.ServerChoices.CATALYST_9500
            elif capacity < 1201:
                site_details['network_type'] = Site.NetworkTypeChoices.LARGE_BRANCH
                site_details['router'] = Site.RouterChoices.ISR_4451
                site_details['core'] = Site.CoreChoices.CATALYST_9500
                site_details['server'] = Site.ServerChoices.CATALYST_9500
            elif capacity < 2001:
                site_details['network_type'] = Site.NetworkTypeChoices.MEDIUM_CAMPUS
                site_details['router'] = Site.RouterChoices.ASR_1001_X
                site_details['core'] = Site.CoreChoices.CATALYST_9500
                site_details['server'] = Site.ServerChoices.CATALYST_9500
            else:
                site_details['network_type'] = Site.NetworkTypeChoices.LARGE_CAMPUS
                site_details['router'] = Site.RouterChoices.ASR_1001_HX
                site_details['core'] = Site.CoreChoices.CATALYST_9500
                site_details['server'] = Site.ServerChoices.CATALYST_9500
    site_database_file.close()
    return site_details


def initialize_navbar(obj, request, site_id=None):
    if site_id:
        site_record = Site.objects.get(id=site_id)
        obj.navbar = NavbarForm(initial={'site': site_record.network_name})
        if site_record.signal_created_access:
            messages.success(request, MESSAGES['ACCESS_CREATED'])
        if site_record.signal_duplicate_vlan:
            messages.error(request, MESSAGES['DUPLICATE_VLAN'])
            site_record.signal_duplicate_vlan = False
        if site_record.signal_exception_site:
            pass
        if site_record.signal_onboarded_site:
            messages.success(request, MESSAGES['SITE_ONBOARDED'])
            site_record.signal_onboarded_site = False
        if site_record.signal_overlapping_access:
            messages.warning(request, MESSAGES['OVERLAPPING_ACCESS'])
            site_record.signal_overlapping_access = False
        obj.signal_present_core = True if site_record.signal_present_core else False
        obj.signal_present_server = True if site_record.signal_present_server else False
        if site_record.signal_updated_access:
            messages.success(request, MESSAGES['ACCESS_UPDATED'])
            site_record.signal_updated_access = False
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


def set_error(request, error_type, error_message=None):
    if not error_message:
        error_message = ERRORS[error_type]['message']
    exec('messages.' + ERRORS[error_type]['type'] +
         '(request, "' + error_message + '")')


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
    # TODO: define
    pass
