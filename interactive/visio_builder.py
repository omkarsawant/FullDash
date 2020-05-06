from . import base_system
from .settings import BASE_DIR

from access import base_access
from access.models import AccessSwitch
from router import base_router
from router.models import Router

from zipfile import ZipFile


def visio_builder(site_record, closet_records):
    router_records = Router.objects.filter(closet__in=closet_records)
    access_switch_records = AccessSwitch.objects.filter(
        closet__in=closet_records)
    visio_template = ZipFile(BASE_DIR + base_system.DIRECTORIES['diagrams'] + get_visio_template_name(
        site_record, router_records, access_switch_records), 'r')
    '''visio_file = ZipFile(BASE_DIR + base_system.DIRECTORIES['staging'] + get_visio_template_name(
        site_record, router_records, access_switch_records), 'w')'''
    visio_file = ZipFile(
        BASE_DIR + base_system.DIRECTORIES['staging'] + base_system.get_filename(site_record.crest, 'visio'), 'w')
    visio_file.comment = visio_template.comment
    diagram_dict = {}
    diagram_dict.update(base_router.get_device_dict(
        router_records[0], False, 'R1'))
    diagram_dict.update(base_router.get_device_dict(
        router_records[1], True, 'R2'))
    if site_record.signal_present_core:
        #TODO: implement
        pass
    else:
        for index, access_switch_record in enumerate(access_switch_records):
            diagram_dict.update(
                base_access.get_device_dict(access_switch_record, 'A' + str(index+1)))
        page_filename = get_zip_filename('page', 2)
        page_file = visio_template.open(page_filename, 'r').read()
        for key, value in diagram_dict.items():
            page_file = page_file.replace(key.encode(), value.encode())
        for zip_file in visio_template.infolist():
            zip_filename = zip_file.filename
            if zip_filename != page_filename:
                visio_file.writestr(
                    zip_file, visio_template.read(zip_filename))
            else:
                visio_file.writestr(page_filename, page_file)
    visio_template.close()
    visio_file.close()


def set_visio_page(page_file, page_dict):
    for key, value in page_dict.items():
        page_file = page_file.replace(key.encode(), value.encode())


def get_zip_filename(filetype, file_number):
    if filetype == 'page':
        return 'visio/pages/page' + str(file_number) + '.xml'


def get_visio_template_name(site_record, router_records, access_switch_records):
    return 'Drawing1.vsdx'
