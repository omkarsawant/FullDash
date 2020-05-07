from . import base_system
from .settings import BASE_DIR
from zipfile import ZipFile


def ipam_list_builder(crest, ip_ipam_list, vlan_ipam_list):
    ipam_template = ZipFile(
        BASE_DIR + base_system.DIRECTORIES['ipam'] + 'ipam.xlsx', 'r')
    ipam_file = ZipFile(
        BASE_DIR + base_system.DIRECTORIES['staging'] + base_system.get_filename(crest, 'ipam'), 'w')
    zip_file_dict = {}
    shared_file_eof = '</sst>'
    shared_file_string = ''
    token_dict = {}
    token_number = 5
    for ip_ipam in ip_ipam_list:
        ip_ipam_tokens = ip_ipam.split('$$')
        for ip_ipam_token in ip_ipam_tokens:
            if ip_ipam_token not in token_dict:
                shared_file_string = shared_file_string + \
                    '<si><t>' + ip_ipam_token + '</t></si>'
                token_dict[ip_ipam_token] = str(token_number)
                token_number = token_number + 1
    for vlan_ipam in vlan_ipam_list:
        vlan_ipam_tokens = vlan_ipam.split('$$')
        for vlan_ipam_token in vlan_ipam_tokens:
            if vlan_ipam_token not in token_dict:
                shared_file_string = shared_file_string + \
                    '<si><t>' + vlan_ipam_token + '</t></si>'
                token_dict[vlan_ipam_token] = str(token_number)
                token_number = token_number + 1
    shared_filename = get_zip_filename('shared')
    zip_file_dict[shared_filename] = ipam_template.open(
        shared_filename, 'r').read()
    zip_file_dict[shared_filename] = zip_file_dict[shared_filename].replace(
        shared_file_eof.encode(), (shared_file_string + shared_file_eof).encode())
    ip_ipam_string = ''
    ip_ipam_row_number = 2
    for ip_ipam in ip_ipam_list:
        ip_ipam_tokens = ip_ipam.split('$$')
        ip_ipam_string = ip_ipam_string + '<row r="' + \
            str(ip_ipam_row_number) + '" spans="1:3" x14ac:dyDescent="0.3">'
        ip_ipam_col_number = 1
        for ip_ipam_token in ip_ipam_tokens:
            ip_ipam_string = ip_ipam_string + '<c r="' + \
                chr(64+ip_ipam_col_number) + \
                str(ip_ipam_row_number) + '" t="s"><v>'
            ip_ipam_col_number = ip_ipam_col_number + 1
            ip_ipam_string = ip_ipam_string + \
                token_dict[ip_ipam_token] + '</v></c>'
        ip_ipam_string = ip_ipam_string + '</row>'
        ip_ipam_row_number = ip_ipam_row_number+1
    ip_filename = get_zip_filename('sheet', 1)
    zip_file_dict[ip_filename] = ipam_template.open(
        ip_filename, 'r').read()
    end_of_sheet = '</sheetData>'
    zip_file_dict[ip_filename] = zip_file_dict[ip_filename].replace(
        end_of_sheet.encode(), (ip_ipam_string + end_of_sheet).encode())
    vlan_ipam_string = ''
    vlan_ipam_row_number = 2
    for vlan_ipam in vlan_ipam_list:
        vlan_ipam_tokens = vlan_ipam.split('$$')
        vlan_ipam_string = vlan_ipam_string + '<row r="' + \
            str(vlan_ipam_row_number) + '" spans="1:3" x14ac:dyDescent="0.3">'
        vlan_ipam_col_number = 1
        for vlan_ipam_token in vlan_ipam_tokens:
            vlan_ipam_string = vlan_ipam_string + '<c r="' + \
                chr(64+vlan_ipam_col_number) + \
                str(vlan_ipam_row_number) + '" t="s"><v>'
            vlan_ipam_col_number = vlan_ipam_col_number + 1
            vlan_ipam_string = vlan_ipam_string + \
                token_dict[vlan_ipam_token] + '</v></c>'
        vlan_ipam_string = vlan_ipam_string + '</row>'
        vlan_ipam_row_number = vlan_ipam_row_number+1
    vlan_filename = get_zip_filename('sheet', 2)
    zip_file_dict[vlan_filename] = ipam_template.open(
        vlan_filename, 'r').read()
    zip_file_dict[vlan_filename] = zip_file_dict[vlan_filename].replace(
        end_of_sheet.encode(), (vlan_ipam_string + end_of_sheet).encode())
    for zip_file in ipam_template.infolist():
        zip_filename = zip_file.filename
        if zip_filename not in zip_file_dict:
            ipam_file.writestr(zip_file, ipam_template.read(zip_filename))
        else:
            ipam_file.writestr(zip_filename, zip_file_dict[zip_filename])
    ipam_template.close()
    ipam_file.close()


def get_zip_filename(filetype, file_number=None):
    if filetype == 'shared':
        return 'xl/sharedStrings.xml'
    elif filetype == 'sheet':
        return 'xl/worksheets/sheet' + str(file_number) + '.xml'
