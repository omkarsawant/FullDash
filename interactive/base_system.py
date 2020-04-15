from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from closets.models import Closets
from overview.forms import Navbar
from overview.models import Overview


def activate_modal(obj, modal_header, modal_body):
    obj.modal_display = 'True'  # do something here
    obj.modal_header = modal_header
    obj.modal_body = modal_body


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


def show_error_page(request, modal_header, modal_body):
    obj = type('', (object,), {})()
    activate_modal(obj, modal_header, modal_body)
    render(request, 'error.html', {'obj': obj})
