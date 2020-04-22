from .models import Router


def make_model(closet):
    # TODO: finish the code!
    router_parameters = {
        'hostname': 'lolihentai',
        'loopback_ip': '1.1.1.1'
    }
    Router.objects.create(**router_parameters, closet=closet)
