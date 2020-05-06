from ipaddress import IPv4Interface, IPv4Network

from .models import Router

ROUTER_SPECS = {
    'isr_4451': {
        'WAN_INTR': [],
        'INTERLINK_INTRS': [],
        'DOWNLINK_INTRS': [],
    },
}


class RouterDevice:
    def __init__(self, site_record, router_record, secondary_router):
        self.site_record = site_record
        self.router_model = self.site_record.router
        self.device_record = router_record
        self.wan_intr = ROUTER_SPECS[self.router_model]['WAN_INTR']
        self.wan_link_cidr = self.device_record.wan_link_cidr
        self.interlink_intrs = ROUTER_SPECS[self.router_model]['INTERLINK_INTRS']
        self.downlink_intrs = ROUTER_SPECS[self.router_model]['DOWNLINK_INTRS']
        self.required_prefixes = []
        self.preconfigured_subnets = []
        self.secondary_router = secondary_router
        if self.secondary_router:
            self.downlink_intrs.reverse()

    def check_connection(self, local_ip, remote_ip, prefix_length):
        if local_ip:
            if remote_ip:
                local_interface = IPv4Interface(f'{local_ip}/{prefix_length}')
                local_network = local_interface.network
                remote_interface = IPv4Interface(
                    f'{remote_ip}/{prefix_length}')
                if local_network == remote_interface.network and local_interface > remote_interface:
                    self.preconfigured_subnets.append(local_network)
                    return True
                else:
                    return False
            else:
                return False
        else:
            if remote_ip:
                return False
            else:
                self.required_prefixes.append(prefix_length)
                return True

    def get_ip_requirements(self, router_device=None):
        self.preconfigured_subnets = []
        self.required_prefixes = [] if self.device_record.loopback_ip else [32]
        '''if self.device_record.isp_ip:
            try:
                IPv4Network(self.device_record.isp_ip + '/' +
                            self.device_record.wan_link_cidr.split('/')[-1])
            except:
                raise AttributeError('')  # TODO: get error from base_system
        else:
            raise AttributeError('')  # TODO: get error from base_system'''
        if self.secondary_router:
            if not self.check_connection(self.device_record.interlink_1_ip, router_device.device_record.interlink_1_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
            if not self.check_connection(self.device_record.interlink_2_ip, router_device.device_record.interlink_2_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
        return self.required_prefixes, self.preconfigured_subnets

    def get_ipam_list(self):
        pass

    def set_ips(self, assigned_subnets):
        if not self.device_record.loopback_ip:
            self.device_record.loopback_ip = str(
                assigned_subnets[32].pop(0))[:-3]
        if self.secondary_router:
            if not self.device_record.interlink_1_ip:
                self.device_record.interlink_1_ip = str(
                    assigned_subnets[31].pop(0)[1])
            if not self.device_record.interlink_2_ip:
                self.device_record.interlink_2_ip = str(
                    assigned_subnets[31].pop(0)[1])
        self.device_record.save()

    def make_connections(self, router_device, downlink_devices):
        self.other_router_loopback_ip = router_device.device_record.loopback_ip
        if self.secondary_router:
            if not self.device_record.downlink_1_ip:
                self.device_record.downlink_1_ip = str(
                    IPv4Network(downlink_devices[0].device_record.uplink_2_ip + '/31', False))[:-3]
            if len(self.downlink_intrs) == 2:
                if not self.device_record.downlink_2_ip:
                    self.device_record.downlink_2_ip = str(
                        IPv4Network(downlink_devices[1].device_record.uplink_2_ip + '/31', False))[:-3]
        else:
            if not self.device_record.interlink_1_ip:
                self.device_record.interlink_1_ip = str(
                    IPv4Network(router_device.device_record.interlink_1_ip + '/31', False))[:-3]
            if not self.device_record.interlink_2_ip:
                self.device_record.interlink_2_ip = str(
                    IPv4Network(router_device.device_record.interlink_2_ip + '/31', False))[:-3]
            if not self.device_record.downlink_1_ip:
                self.device_record.downlink_1_ip = str(
                    IPv4Network(downlink_devices[0].device_record.uplink_1_ip + '/31', False))[:-3]
            if len(self.downlink_intrs) == 2:
                if not self.device_record.downlink_2_ip:
                    self.device_record.downlink_2_ip = str(
                        IPv4Network(downlink_devices[1].device_record.uplink_1_ip + '/31', False))[:-3]
        self.device_record.save()


def get_device_dict(router_record, key_prefix):
    device_dict = {}
    device_dict[key_prefix + '_HOSTNAME'] = router_record.hostname
    device_dict[key_prefix + '_LOOPBACK'] = router_record.loopback_ip
    device_dict[key_prefix + '_UP'] = '.' + \
        router_record.wan_link_cidr.split('.')[-1].split('/')[0]
    device_dict[key_prefix + '_IN1'] = '.' + \
        router_record.interlink_1_ip.split('.')[-1]
    device_dict[key_prefix + '_IN2'] = '.' + \
        router_record.interlink_2_ip.split('.')[-1]
    device_dict[key_prefix + '_DN1'] = '.' + \
        router_record.downlink_1_ip.split('.')[-1]
    if router_record.downlink_2_ip:
        device_dict[key_prefix + '_DN2'] = '.' + \
            router_record.downlink_2_ip.split('.')[-1]
    '''device_dict[key_prefix + '_ISP'] = '.' + \
        router_record.isp_ip.split('.')[-1]'''
    device_dict[key_prefix + '_ISP_NAME'] = router_record.wan_provider
    device_dict[key_prefix + '_ISP_CID'] = router_record.access_id + \
        '/' + router_record.port_id
    device_dict[key_prefix + '_ISP_SP'] = str(router_record.access_bw) + \
        'Mbps/' + str(router_record.port_bw) + 'Mbps'
    return device_dict
