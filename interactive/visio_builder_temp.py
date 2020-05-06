from zipfile import ZipFile

base_filename = 'C:/Users/Omi/Documents/Projects/FullDash/static/diagrams/'
visio_template = ZipFile(base_filename + 'Drawing1.vsdx', 'r')
visio_file = ZipFile(base_filename + 'Drawing99.vsdx', 'w')
visio_file.comment = visio_template.comment
diagram_dict = {
    'VLANS': '10.0.0.0/24\n10.0.0.0/26',
}
page_filename = 'visio/pages/page2.xml'
page_file = visio_template.open(page_filename, 'r').read()
for key, value in diagram_dict.items():
    page_file = page_file.replace(key.encode(), value.encode())
for zip_file in visio_template.infolist():
    zip_filename = zip_file.filename
    if zip_filename != page_filename:
        visio_file.writestr(zip_file, visio_template.read(zip_filename))
    else:
        visio_file.writestr(page_filename, page_file)
visio_template.close()
visio_file.close()
