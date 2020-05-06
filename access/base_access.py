from ipaddress import IPv4Interface, IPv4Network

from .models import AccessSwitch, Vlan

ACCESS_SWITCH_SPECS = {
    'MGIG_STACK': {
        'BASE_INTR': {
            'Catalyst 3850': 'Gig',
            'Catalyst 9300': 'TwoGig',
        },
        'MGIG_INTR': {
            'Catalyst 3850': 'TenGig',
            'Catalyst 9300': 'TenGig',
        },
        'UPLINK_INTRS': {
            'SINGLE_SWITCH': ['TenGig1/1/3', 'TenGig1/1/4'],
            'MULTIPLE_SWITCHES': ['TenGig1/1/4', 'TenGig2/1/4'],
        },
    },
    'NMGIG_STACK': {
        'BASE_INTR': {
            'Catalyst 3850': 'Gig',
            'Catalyst 9300': 'Gig',
        },
        'UPLINK_INTRS': {
            'SINGLE_SWITCH': ['Gig1/1/3', 'Gig1/1/4'],
            'MULTIPLE_SWITCHES': ['Gig1/1/4', 'Gig2/1/4'],
        },
    },
}


class AccessSwitchDevice:
    def __init__(self, site_record, access_switch_record):
        self.site_record = site_record
        self.device_record = access_switch_record
        self.access_switch_model = self.device_record.stack_model
        self.vlan_records = Vlan.objects.filter(
            access_switch=self.device_record)
        self.required_prefixes = []
        self.preconfigured_subnets = []
        if self.device_record.mgig_count == 0:
            self.mgig_stack = False
            self.base_intr = ACCESS_SWITCH_SPECS['NMGIG_STACK']['BASE_INTR'][self.access_switch_model]
            if self.device_record.switch_count == 1:
                self.uplink_intrs = ACCESS_SWITCH_SPECS['NMGIG_STACK']['UPLINK_INTRS']['SINGLE_SWITCH']
            else:
                self.uplink_intrs = ACCESS_SWITCH_SPECS['NMGIG_STACK']['UPLINK_INTRS']['MULTIPLE_SWITCHES']
        else:
            self.mgig_stack = True
            self.base_intr = ACCESS_SWITCH_SPECS['MGIG_STACK']['BASE_INTR'][self.access_switch_model]
            self.mgig_intr = ACCESS_SWITCH_SPECS['MGIG_STACK']['MGIG_INTR'][self.access_switch_model]
            if self.device_record.switch_count == 1:
                self.uplink_intrs = ACCESS_SWITCH_SPECS['MGIG_STACK']['UPLINK_INTRS']['SINGLE_SWITCH']
            else:
                self.uplink_intrs = ACCESS_SWITCH_SPECS['MGIG_STACK']['UPLINK_INTRS']['MULTIPLE_SWITCHES']

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

    def get_ip_requirements(self, uplink_type, *uplink_devices):
        self.preconfigured_subnets = []
        self.required_prefixes = [] if self.device_record.loopback_ip else [32]
        if uplink_type == 'router_primary':
            if not self.check_connection(self.device_record.uplink_1_ip, uplink_devices[0].device_record.downlink_1_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
            if not self.check_connection(self.device_record.uplink_2_ip, uplink_devices[1].device_record.downlink_1_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
        if uplink_type == 'router_secondary':
            if not self.check_connection(self.device_record.uplink_1_ip, uplink_devices[0].device_record.downlink_2_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
            if not self.check_connection(self.device_record.uplink_2_ip, uplink_devices[1].device_record.downlink_2_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
        if uplink_type == 'core':
            if not self.check_connection(self.device_record.uplink_1_ip, uplink_devices[0].device_record.downlink_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
            if not self.check_connection(self.device_record.uplink_2_ip, uplink_devices[1].device_record.downlink_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
        for vlan_record in self.vlan_records:
            if vlan_record.svi_ip:
                self.preconfigured_subnets.append(IPv4Network(
                    f'{vlan_record.svi_ip}/{vlan_record.svi_mask_length[-2:]}', False))
            else:
                self.required_prefixes.append(
                    int(vlan_record.svi_mask_length[-2:]))
        return self.required_prefixes, self.preconfigured_subnets

    def get_ipam_list(self):
        pass

    def set_ips(self, assigned_subnets):
        if not self.device_record.uplink_1_ip:
            self.device_record.uplink_1_ip = str(
                assigned_subnets[31].pop(0)[1])
        if not self.device_record.uplink_2_ip:
            self.device_record.uplink_2_ip = str(
                assigned_subnets[31].pop(0)[1])
        for vlan_record in self.vlan_records:
            if not vlan_record.svi_ip:
                vlan_record.svi_ip = str(
                    assigned_subnets[int(vlan_record.svi_mask_length[-2:])].pop(0)[1])
                vlan_record.save()
        self.device_record.save()


def get_vlan_id(site_record, vlan_instance):
    vlan_type = vlan_instance.vlan_type
    vlan_records_count = len(Vlan.objects.filter(
        access_switch=vlan_instance.access_switch, vlan_type=vlan_type).exclude(id=vlan_instance.id))
    if vlan_records_count > 99:
        # TODO: too many VLANs
        return (False, None, None)
    if vlan_type and vlan_instance.svi_mask_length:
        if vlan_type == Vlan.VlanTypeChoices.DATA:
            vlan_record_number = 300 + vlan_records_count
            return (True, vlan_record_number, 'DATA-'+str(vlan_record_number))
        if vlan_type == Vlan.VlanTypeChoices.SECURITY:
            if vlan_records_count > 0:
                site_record.signal_duplicate_vlan = True
                site_record.save()
                return (False, None, None)
            return (True, 399, 'Security_Vlan_399')
        if vlan_type == Vlan.VlanTypeChoices.VOICE:
            vlan_record_number = 400 + vlan_records_count
            return (True, vlan_record_number, 'VOICE-'+str(vlan_record_number))
        if vlan_type == Vlan.VlanTypeChoices.VOICE_SERVER:
            if vlan_records_count > 0:
                site_record.signal_duplicate_vlan = True
                site_record.save()
                return (False, None, None)
            return (True, 499, 'Voice_Server_vlan_499')
        if vlan_type == Vlan.VlanTypeChoices.SERVER:
            vlan_record_number = 700 + vlan_records_count
            return (True, vlan_record_number, 'SERVER-'+str(vlan_record_number))
    return (True, None, None)


def get_stack_port_names(access_switch):
    default_port_base = 'Gig'
    if access_switch.stack_model == AccessSwitch.AccessChoices.CATALYST_9300:
        mgig_default_port_base = 'Two' + default_port_base
    else:
        mgig_default_port_base = default_port_base
    mgig_mgig_port_base = 'Ten' + default_port_base
    if access_switch.mgig_count:
        mgig_count = access_switch.mgig_count
    else:
        mgig_count = 0
    port_name_list = [(None, None)]
    for switch_index in range(1, mgig_count+1):
        port_name_list.extend([(mgig_default_port_base+str(switch_index) +
                                '/0/'+str(port_index),)*2 for port_index in range(1, 37)])
        port_name_list.extend([(mgig_mgig_port_base+str(switch_index) +
                                '/0/'+str(port_index),)*2 for port_index in range(37, 49)])
    for switch_index in range(mgig_count+1, access_switch.switch_count+1):
        port_name_list.extend([(default_port_base+str(switch_index) +
                                '/0/'+str(port_index),)*2 for port_index in range(1, 49)])
    return port_name_list


def get_device_dict(access_switch_record, key_prefix):
    device_dict = {}
    device_dict[key_prefix + '_HOSTNAME'] = access_switch_record.hostname
    device_dict[key_prefix +
                '_MGIG_C'] = str(access_switch_record.mgig_count)
    device_dict[key_prefix + '_NMGIG_C'] = str(
        access_switch_record.switch_count - access_switch_record.mgig_count)
    device_dict[key_prefix + '_UP1'] = '.' + \
        access_switch_record.uplink_1_ip.split('.')[-1]
    device_dict[key_prefix + '_N_UP1'] = str(IPv4Network(
        access_switch_record.uplink_1_ip + '/31', False))
    device_dict[key_prefix + '_UP2'] = '.' + \
        access_switch_record.uplink_2_ip.split('.')[-1]
    device_dict[key_prefix + '_N_UP2'] = str(IPv4Network(
        access_switch_record.uplink_2_ip + '/31', False))
    device_dict[key_prefix + '_AP'] = str(access_switch_record.ap_count)
    device_dict[key_prefix + '_VLANS'] = ''
    vlan_records = Vlan.objects.filter(access_switch=access_switch_record)
    for vlan_record in vlan_records:
        device_dict[key_prefix + '_VLANS'] = device_dict[key_prefix + '_VLANS'] + '\n' + \
            str(vlan_record.vlan_id) + ' - ' + \
            vlan_record.svi_ip + vlan_record.svi_mask_length
    return device_dict
