from zipfile import ZipFile
import xml.etree.ElementTree as ET

zip_in = ZipFile(
    'C:/Users/Omi/Documents/Projects/FullDash/static/diagrams/Drawing1.vsdx', 'r')
page_file = zip_in.open('visio/pages/page1.xml', 'r').read()
page_file = page_file.replace(b'hostname', b'ghostghost')
zip_out = ZipFile(
    'C:/Users/Omi/Documents/Projects/FullDash/static/diagrams/Drawing2.vsdx', 'w')
excluded_filenames = ['visio/pages/page3.xml']
zip_out.comment = zip_in.comment
for item in zip_in.infolist():
    if item.filename not in excluded_filenames:
        zip_out.writestr(item, zip_in.read(item.filename))
zip_out.writestr(excluded_filenames[0], page_file)
zip_out.close()
zip_in.close()
