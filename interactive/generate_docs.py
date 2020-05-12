from access import base_access
from access.models import AccessSwitch
from closet.models import Closet
from interactive import base_system
from overview.models import ExcludedSubnet, Supernet
from router import base_router
from router.models import Router
from .settings import BASE_DIR

from os import listdir, remove
from zipfile import ZipFile

from .ipam_list_builder import ipam_list_builder
from .subnet_planner import SubnetPlanner
from .visio_builder import visio_builder


def generate_docs(site_record, build_type, diagram_author=None):
    # get site information
    closet_records = Closet.objects.filter(site=site_record)
    if not closet_records:
        return base_system.MESSAGES['NO_CLOSET']
    router_records = Router.objects.filter(closet__in=closet_records)
    if not router_records:
        return base_system.MESSAGES['NO_ROUTER']
    router_devices = [base_router.RouterDevice(
        site_record, router_records[0], False), base_router.RouterDevice(site_record, router_records[1], True)]
    access_uplink_devices = router_devices
    # TODO: get core records
    # TODO: get server records
    access_switch_records = AccessSwitch.objects.filter(
        closet__in=closet_records)
    if not access_switch_records:
        return base_system.MESSAGES['NO_ACCESS_STACK']
    # get IP requirements
    required_prefixes = []
    preconfigured_subnets = []
    try:
        combine_ip_requirements(
            router_devices[0].get_ip_requirements(), required_prefixes, preconfigured_subnets)
        combine_ip_requirements(
            router_devices[1].get_ip_requirements(router_devices[0]), required_prefixes, preconfigured_subnets)
    except AttributeError as error:
        return error
    access_devices = []
    for access_switch_record in access_switch_records:
        access_device = base_access.AccessSwitchDevice(
            site_record, access_switch_record, access_uplink_devices)
        try:
            combine_ip_requirements(access_device.get_ip_requirements(
            ), required_prefixes, preconfigured_subnets)
        except AttributeError as error:
            return error
        access_devices.append(access_device)
    required_prefixes.sort(reverse=True)
    # TODO: check overlapping of preconfigured
    # get supernets
    supernets = Supernet.objects.filter(
        site=site_record).values_list('supernet_cidr', flat=True)
    if not supernets:
        return base_system.MESSAGES['NO_SUPERNET']
    if build_type in ['subnet', 'all']:
        # get excluded subnets
        excluded_subnets = preconfigured_subnets.copy()
        excluded_subnets.extend(ExcludedSubnet.objects.filter(
            site=site_record).values_list('subnet_cidr'))
        # get assigned IPs
        subnet_planner = SubnetPlanner(supernets)
        extra_subnets = subnet_planner.exclude_subnets(excluded_subnets)
        assigned_subnets = {}
        for required_prefix in required_prefixes:
            assigned_subnet = subnet_planner.assign_subnet(required_prefix)
            if not assigned_subnet:
                return base_system.MESSAGES['NO_SUBNET']
            assigned_subnets.setdefault(
                required_prefix, []).append(assigned_subnet)
        # set IPs
        router_devices[0].set_ips(assigned_subnets)
        router_devices[1].set_ips(assigned_subnets)
        # TODO: set core IPs
        # TODO: set server IPs
        for access_device in access_devices:
            access_device.set_ips(assigned_subnets)
        # TODO: make core connections
        # TODO: make server connections
        router_devices[1].make_connections(router_devices[0], access_devices)
        router_devices[0].make_connections(router_devices[1], access_devices)
        # get IPAM list
        site_ip_list = router_devices[0].get_ipam_list()
        site_ip_list.extend(router_devices[1].get_ipam_list())
        site_vlan_list = []
        for access_device in access_devices:
            ip_list, vlan_list = access_device.get_ipam_list()
            site_ip_list.extend(ip_list)
            site_vlan_list.extend(vlan_list)
        site_ip_list.sort()
        site_vlan_list.sort()
        ipam_list_builder(site_record.crest, site_ip_list, site_vlan_list)
    if build_type in ['config', 'all']:
        # TODO: generate other fields
        router_devices[0].make_configuration(supernets, extra_subnets)
        router_devices[1].make_configuration(supernets, extra_subnets)
        for access_device in access_devices:
            access_device.make_configuration()
    if build_type in ['diagram', 'all']:
        visio_builder(site_record, closet_records, diagram_author)
    # generate GDA 2 documents zip file
    staging_path = BASE_DIR + base_system.DIRECTORIES['staging']
    crest_str = str(site_record.crest)[-4:]
    gda_zip_file = ZipFile(
        staging_path + base_system.get_filename(site_record.crest, 'zip'), 'w')
    for filename in listdir(staging_path):
        filepath = staging_path + filename
        if crest_str in filename and 'GDA2' not in filename:
            gda_zip_file.write(filepath, filename)
            remove(filepath)
    gda_zip_file.close()
    return base_system.MESSAGES['SUCCESS']


def combine_ip_requirements(ip_requirements, required_prefixes, preconfigured_subnets):
    required_prefixes.extend(ip_requirements[0])
    preconfigured_subnets.extend(ip_requirements[1])
