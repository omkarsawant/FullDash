from ipaddress import IPv4Interface, IPv4Network
from interactive import base_system
from interactive.settings import BASE_DIR
from .models import Router

ROUTER_SPECS = {
    'ISR 4331': {
        'WAN_INTR': ['Gig0/0/0'],
        'INTERLINK_INTRS': ['Gig0/1/0', 'Gig0/1/1'],
        'DOWNLINK_INTRS': ['Gig0/0/2'],
    },
    'ISR 4351': {
        'WAN_INTR': ['Gig0/0/0'],
        'INTERLINK_INTRS': ['Gig0/1/0', 'Gig0/1/1'],
        'DOWNLINK_INTRS': ['Gig0/0/1', 'Gig0/0/2'],
    },
    'ISR 4451': {
        'WAN_INTR': ['Gig0/0/0'],
        'INTERLINK_INTRS': ['Gig0/1/0', 'Gig0/1/1'],
        'DOWNLINK_INTRS': ['Gig0/0/1', 'Gig0/0/2'],
    },
    'ASR 1001-X': {
        'WAN_INTR': ['TenGig0/0/0'],
        'INTERLINK_INTRS': ['Gig0/0/3', 'Gig0/0/4'],
        'DOWNLINK_INTRS': ['TenGig0/0/1', 'TenGig0/1/0'],
    },
    'ASR 1001-HX': {
        'WAN_INTR': ['TenGig0/1/0'],
        'INTERLINK_INTRS': ['TenGig0/1/3', 'TenGig0/1/4'],
        'DOWNLINK_INTRS': ['TenGig0/1/1', 'TenGig0/1/2'],
    },
}

DNS_SUFFIX = '.network.aig.net'


class RouterDevice:
    def __init__(self, site_record, router_record, secondary_router):
        self.site_record = site_record
        self.router_model = self.site_record.router
        self.device_record = router_record
        self.wan_intr = ROUTER_SPECS[self.router_model]['WAN_INTR'][0]
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

    def get_dns_base(self):
        return self.device_record.hostname + '$$' + self.device_record.hostname + '-'

    def get_ipam_list(self):
        ip_list = [self.get_dns_base() + 'lo-0' + DNS_SUFFIX + '$$' +
                   self.device_record.loopback_ip]
        ip_list.append(self.get_intr_ipam(
            self.interlink_intrs[0], self.device_record.interlink_1_ip))
        ip_list.append(self.get_intr_ipam(
            self.interlink_intrs[1], self.device_record.interlink_2_ip))
        ip_list.append(self.get_intr_ipam(
            self.downlink_intrs[0], self.device_record.downlink_1_ip))
        if len(self.downlink_intrs) == 2:
            ip_list.append(self.get_intr_ipam(
                self.downlink_intrs[1], self.device_record.downlink_2_ip))
        return ip_list

    def get_intr_ipam(self, intr, ip):
        intr_breakdown = intr.split('/')
        return self.get_dns_base() + intr_breakdown[0][:2].lower() + '-' + intr_breakdown[0][-1] + '-' + intr_breakdown[1] + '-' + intr_breakdown[2] + DNS_SUFFIX + '$$' + ip

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
        if not self.device_record.interlink_1_desc:
            self.device_record.interlink_1_desc = base_system.get_interface_description(
                'l3_p2p', remote_device=router_device.device_record.hostname, remote_port=router_device.interlink_intrs[0])
        if not self.device_record.interlink_2_desc:
            self.device_record.interlink_2_desc = base_system.get_interface_description(
                'l3_p2p', remote_device=router_device.device_record.hostname, remote_port=router_device.interlink_intrs[1])
        if not self.device_record.other_router_loopback_ip:
            self.device_record.other_router_loopback_ip = router_device.device_record.loopback_ip
        if not self.device_record.other_router_hostname:
            self.device_record.other_router_hostname = router_device.device_record.hostname
        if self.secondary_router:
            if not self.device_record.downlink_1_ip:
                self.device_record.downlink_1_ip = str(
                    IPv4Network(downlink_devices[0].device_record.uplink_2_ip + '/31', False))[:-3]
            if not self.device_record.downlink_1_desc:
                self.device_record.downlink_1_desc = base_system.get_interface_description(
                    'l3_p2p', remote_device=downlink_devices[0].device_record.hostname, remote_port=downlink_devices[0].uplink_intrs[0])
            if len(self.downlink_intrs) == 2:
                if not self.device_record.downlink_2_ip:
                    self.device_record.downlink_2_ip = str(
                        IPv4Network(downlink_devices[1].device_record.uplink_2_ip + '/31', False))[:-3]
                if not self.device_record.downlink_2_desc:
                    self.device_record.downlink_2_desc = base_system.get_interface_description(
                        'l3_p2p', remote_device=downlink_devices[1].device_record.hostname, remote_port=downlink_devices[1].uplink_intrs[0])
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
            if not self.device_record.downlink_1_desc:
                self.device_record.downlink_1_desc = base_system.get_interface_description(
                    'l3_p2p', remote_device=downlink_devices[0].device_record.hostname, remote_port=downlink_devices[0].uplink_intrs[1])
            if len(self.downlink_intrs) == 2:
                if not self.device_record.downlink_2_ip:
                    self.device_record.downlink_2_ip = str(
                        IPv4Network(downlink_devices[1].device_record.uplink_1_ip + '/31', False))[:-3]
                if not self.device_record.downlink_2_desc:
                    self.device_record.downlink_2_desc = base_system.get_interface_description(
                        'l3_p2p', remote_device=downlink_devices[1].device_record.hostname, remote_port=downlink_devices[1].uplink_intrs[1])
        self.device_record.save()

    def make_configurations(self, supernets, extra_subnets):
        base_config_dict = {}
        base_config_file = open(
            BASE_DIR + base_system.DIRECTORIES['config'] + 'base_router.txt', 'r')
        base_config_template = base_config_file.read()
        base_config_file.close()
        circuit_id = self.device_record.access_id + ':' + \
            str(self.device_record.access_bw) + ':' + \
            self.device_record.port_id + ':' + str(self.device_record.port_bw)
        wan_link_cidr = IPv4Interface(self.device_record.wan_link_cidr)
        supernets_string = ''
        networks_string = ''
        management_file = open(
            BASE_DIR + base_system.DIRECTORIES['config'] + 'management_router_' + self.site_record.nearest_dc + '.txt', 'r')
        management_template = management_file.read().replace(
            '<SITE_ADDRESS>', self.site_record.address)
        netflow_file = open(
            BASE_DIR + base_system.DIRECTORIES['config'] + 'netflow_' + self.site_record.nearest_dc + '.txt', 'r')
        qos_file = open(
            BASE_DIR + base_system.DIRECTORIES['config'] + 'qos.txt', 'r')
        for supernet in supernets:
            supernet_obj = IPv4Network(supernet)
            supernets_string = supernets_string + \
                f'\nip route {supernet_obj.network_address} {supernet_obj.netmask} Null0 200'
            networks_string = networks_string + \
                f'\n network {supernet_obj.network_address} mask {supernet_obj.netmask}'
        for extra_subnet in extra_subnets:
            extra_subnet_obj = IPv4Network(extra_subnet)
            networks_string = networks_string + \
                f'\n network {extra_subnet_obj.network_address} mask {extra_subnet_obj.netmask}'
        base_config_dict['<HOSTNAME>'] = self.device_record.hostname
        base_config_dict['<LOOPBACK_IP>'] = self.device_record.loopback_ip
        base_config_dict['<LOOPBACK_DESC>'] = base_system.get_interface_description(
            'loop')
        base_config_dict['<NETFLOW>'] = netflow_file.read()
        netflow_file.close()
        base_config_dict['<QoS>'] = qos_file.read()
        qos_file.close()
        base_config_dict['<DN_1_INTR>'] = self.downlink_intrs[0]
        base_config_dict['<DN_1_DESC>'] = self.device_record.downlink_1_desc
        base_config_dict['<DN_1_IP>'] = self.device_record.downlink_1_ip
        if len(self.downlink_intrs) == 2:
            base_config_dict['<DN_2_INTR>'] = self.downlink_intrs[1]
            base_config_dict['<DN_2_DESC>'] = self.device_record.downlink_2_desc
            base_config_dict['<DN_2_IP>'] = self.device_record.downlink_2_ip
        base_config_dict['<QoS_INGRESS>'] = base_system.QOS_POLICIES['WAN Ingress']
        base_config_dict['<IN_1_INTR>'] = self.interlink_intrs[0]
        base_config_dict['<IN_1_DESC>'] = self.device_record.interlink_1_desc
        base_config_dict['<IN_1_IP>'] = self.device_record.interlink_1_ip
        base_config_dict['<IN_2_INTR>'] = self.interlink_intrs[1]
        base_config_dict['<IN_2_DESC>'] = self.device_record.interlink_2_desc
        base_config_dict['<IN_2_IP>'] = self.device_record.interlink_2_ip
        base_config_dict['<WAN_INTR>'] = self.wan_intr
        base_config_dict['<WAN_DESC>'] = base_system.get_interface_description(
            'wan', wan_type=self.device_record.wan_type, wan_provider=self.device_record.wan_provider, circuit_id=circuit_id)
        base_config_dict['<WAN_IP>'] = str(wan_link_cidr.ip)
        base_config_dict['<WAN_MASK>'] = str(wan_link_cidr.network.netmask)
        base_config_dict['<WAN_BW>'] = str(self.device_record.port_bw)
        base_config_dict['<QoS_EGRESS>'] = base_system.QOS_POLICIES['WAN Egress']
        base_config_dict['<SUPERNETS>'] = supernets_string
        base_config_dict['<COMMUNITY>'] = base_system.COMMUNITIES[self.site_record.nearest_dc]
        base_config_dict['<LOCAL_ASN>'] = str(self.device_record.local_asn)
        base_config_dict['<NETWORKS>'] = networks_string
        base_config_dict['<IBGP_PEER_LOOPBACK_IP>'] = self.device_record.other_router_loopback_ip
        base_config_dict['<IBGP_PEER_HOSTNAME>'] = self.device_record.other_router_hostname
        base_config_dict['<ISP_IP>'] = self.device_record.isp_ip
        base_config_dict['<REMOTE_ASN>'] = str(self.device_record.remote_asn)
        base_config_dict['<WAN_TYPE>'] = str(self.device_record.wan_type)
        base_config_dict['<WAN_PROVIDER>'] = str(
            self.device_record.wan_provider)
        base_config_dict['<DEVICE_MANAGEMENT>'] = management_template
        management_file.close()
        for key, value in base_config_dict.items():
            if isinstance(value, str):
                base_config_template = base_config_template.replace(key, value)
            else:
                base_config_template = base_config_template.replace(
                    key, value.decode())
        config_file = open(
            BASE_DIR + base_system.DIRECTORIES['staging'] + self.device_record.hostname + '.txt', 'w')
        config_file.write(base_config_template)
        config_file.close()


def get_device_dict(router_record, secondary_router, key_prefix):
    device_dict = {}
    device_dict[key_prefix + '_HOSTNAME'] = router_record.hostname
    device_dict[key_prefix + '_LOOPBACK'] = router_record.loopback_ip
    device_dict[key_prefix + '_UP'] = '.' + \
        router_record.wan_link_cidr.split('.')[-1].split('/')[0]
    device_dict[key_prefix +
                '_N_UP'] = str(IPv4Network(router_record.wan_link_cidr, False))
    device_dict[key_prefix + '_IN1'] = '.' + \
        router_record.interlink_1_ip.split('.')[-1]
    device_dict[key_prefix + '_IN2'] = '.' + \
        router_record.interlink_2_ip.split('.')[-1]
    device_dict[key_prefix + '_DN1'] = '.' + \
        router_record.downlink_1_ip.split('.')[-1]
    '''device_dict[key_prefix + '_ISP'] = '.' + \
        router_record.isp_ip.split('.')[-1]'''
    device_dict[key_prefix + '_ISP_NAME'] = router_record.wan_provider
    device_dict[key_prefix + '_ISP_CID'] = router_record.access_id + \
        '/' + router_record.port_id
    device_dict[key_prefix + '_ISP_SP'] = str(router_record.access_bw) + \
        'Mbps/' + str(router_record.port_bw) + 'Mbps'
    if router_record.downlink_2_ip:
        device_dict[key_prefix + '_DN2'] = '.' + \
            router_record.downlink_2_ip.split('.')[-1]
    if secondary_router:
        device_dict[key_prefix + '_N_IN1'] = str(
            IPv4Network(router_record.interlink_1_ip + '/31', False))
        device_dict[key_prefix + '_N_IN2'] = str(
            IPv4Network(router_record.interlink_2_ip + '/31', False))
    return device_dict
