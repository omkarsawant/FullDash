from ipaddress import IPv4Interface, IPv4Network
from interactive import base_system
from interactive.settings import BASE_DIR
from .models import AccessPortBlock, AccessSwitch, Vlan
from closet.models import Closet

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

DNS_SUFFIX = '.network.aig.net'


class AccessSwitchDevice:
    def __init__(self, site_record, access_switch_record, uplink_devices):
        self.site_record = site_record
        self.device_record = access_switch_record
        self.access_switch_model = self.device_record.stack_model
        self.uplink_devices = uplink_devices
        if self.site_record.signal_present_core:
            self.uplink_type = 'core'
        else:
            other_access_switch_record = AccessSwitch.objects.filter(
                closet__in=Closet.objects.filter(site=site_record)).exclude(id=self.device_record.id)
            if other_access_switch_record and other_access_switch_record[0].id < self.device_record.id:
                self.uplink_type = 'router_secondary'
            else:
                self.uplink_type = 'router_primary'
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

    def get_ip_requirements(self):
        self.preconfigured_subnets = []
        self.required_prefixes = [] if self.device_record.loopback_ip else [32]
        if self.uplink_type == 'router_primary':
            if not self.check_connection(self.device_record.uplink_1_ip, self.uplink_devices[0].device_record.downlink_1_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
            if not self.check_connection(self.device_record.uplink_2_ip, self.uplink_devices[1].device_record.downlink_1_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
        if self.uplink_type == 'router_secondary':
            if not self.check_connection(self.device_record.uplink_1_ip, self.uplink_devices[0].device_record.downlink_2_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
            if not self.check_connection(self.device_record.uplink_2_ip, self.uplink_devices[1].device_record.downlink_2_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
        if self.uplink_type == 'core':
            if not self.check_connection(self.device_record.uplink_1_ip, self.uplink_devices[0].device_record.downlink_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
            if not self.check_connection(self.device_record.uplink_2_ip, self.uplink_devices[1].device_record.downlink_ip, 31):
                raise AttributeError('')  # TODO: get error from base_system
        for vlan_record in self.vlan_records:
            if vlan_record.svi_ip:
                self.preconfigured_subnets.append(IPv4Network(
                    f'{vlan_record.svi_ip}{vlan_record.svi_mask_length}', False))
            else:
                self.required_prefixes.append(
                    int(vlan_record.svi_mask_length[-2:]))
        return self.required_prefixes, self.preconfigured_subnets

    def get_dns_base(self):
        return self.device_record.hostname + '$$' + self.device_record.hostname + '-'

    def get_ipam_list(self):
        ip_list = [self.get_dns_base() + 'lo-0' + DNS_SUFFIX + '$$' +
                   self.device_record.loopback_ip]
        ip_list.append(self.get_uplink_ipam(
            self.uplink_intrs[0], self.device_record.uplink_1_ip))
        ip_list.append(self.get_uplink_ipam(
            self.uplink_intrs[1], self.device_record.uplink_2_ip))
        vlan_list = []
        for vlan_record in self.vlan_records:
            ip_list.append(self.get_dns_base() + 'vl-' +
                           str(vlan_record.vlan_id) + DNS_SUFFIX + '$$' + vlan_record.svi_ip)
            vlan_list.append(self.device_record.hostname + '$$VLAN ' + str(vlan_record.vlan_id) + '$$' + str(IPv4Network(
                vlan_record.svi_ip + vlan_record.svi_mask_length, False)))
        return ip_list, vlan_list

    def get_uplink_ipam(self, uplink_intr, uplink_ip):
        uplink_intr_breakdown = uplink_intr.split('/')
        return self.get_dns_base() + uplink_intr_breakdown[0][:2].lower() + '-' + uplink_intr_breakdown[0][-1] + '-' + uplink_intr_breakdown[1] + '-' + uplink_intr_breakdown[2] + DNS_SUFFIX + '$$' + uplink_ip

    def set_ips(self, assigned_subnets):
        if not self.device_record.loopback_ip:
            self.device_record.loopback_ip = str(
                assigned_subnets[32].pop(0))[:-3]
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

    def make_model(self):
        if self.uplink_type == 'router_primary':
            if not self.device_record.uplink_1_desc:
                self.device_record.uplink_1_desc = base_system.get_interface_description(
                    'l3_p2p', remote_device=self.uplink_devices[0].device_record.hostname, remote_port=self.uplink_devices[0].downlink_intrs[0])
            if not self.device_record.uplink_2_desc:
                self.device_record.uplink_2_desc = base_system.get_interface_description(
                    'l3_p2p', remote_device=self.uplink_devices[1].device_record.hostname, remote_port=self.uplink_devices[1].downlink_intrs[0])
        if self.uplink_type == 'router_secondary':
            if not self.device_record.uplink_1_desc:
                self.device_record.uplink_1_desc = base_system.get_interface_description(
                    'l3_p2p', remote_device=self.uplink_devices[0].device_record.hostname, remote_port=self.uplink_devices[0].downlink_intrs[1])
            if not self.device_record.uplink_2_desc:
                self.device_record.uplink_2_desc = base_system.get_interface_description(
                    'l3_p2p', remote_device=self.uplink_devices[1].device_record.hostname, remote_port=self.uplink_devices[1].downlink_intrs[1])
        if self.uplink_type == 'core':
            if not self.device_record.uplink_1_desc:
                self.device_record.uplink_1_desc = base_system.get_interface_description(
                    'l3_p2p', remote_device=self.uplink_devices[0].device_record.hostname, remote_port=self.uplink_devices[0].downlink_intr)
            if not self.device_record.uplink_2_desc:
                self.device_record.uplink_2_desc = base_system.get_interface_description(
                    'l3_p2p', remote_device=self.uplink_devices[1].device_record.hostname, remote_port=self.uplink_devices[1].downlink_intr)
        self.device_record.save()

    def make_configuration(self):
        self.make_model()
        config_path = BASE_DIR + base_system.DIRECTORIES['config']
        base_config_dict = {}
        base_config_file = open(config_path + 'base_switch.txt', 'r')
        base_config_template = base_config_file.read()
        base_config_file.close()
        vlan_string, svi_string = self.get_vlan_svi_strings(config_path)
        legacy_qos_required, access_ports_string = self.get_access_ports_string(
            config_path)
        base_config_dict['<PRIORITIES>'] = self.get_priority_string(
            config_path)
        base_config_dict['<HOSTNAME>'] = self.device_record.hostname
        base_config_dict['<QoS>'] = self.get_qos_policy_string(
            config_path, legacy_qos_required)
        base_config_dict['<VLANS>'] = vlan_string
        base_config_dict['<SVIS>'] = svi_string
        base_config_dict['<LOOPBACK_IP>'] = self.device_record.loopback_ip
        base_config_dict['<LOOPBACK_DESC>'] = base_system.get_interface_description(
            'loop')
        base_config_dict['<UP_1_INTR>'] = self.uplink_intrs[0]
        base_config_dict['<UP_1_DESC>'] = self.device_record.uplink_1_desc
        base_config_dict['<UP_1_IP>'] = self.device_record.uplink_1_ip
        base_config_dict['<UP_2_INTR>'] = self.uplink_intrs[1]
        base_config_dict['<UP_2_DESC>'] = self.device_record.uplink_2_desc
        base_config_dict['<UP_2_IP>'] = self.device_record.uplink_2_ip
        base_config_dict['<ACCESS_PORTS>'] = access_ports_string
        base_config_dict['<STUB>'] = self.get_ospf_stub_string(config_path)
        if self.uplink_type == 'core':
            base_config_dict['<AREA>'] = str(self.device_record.closet.floor)
        else:
            base_config_dict['<AREA>'] = '0'
        base_config_dict['<DEVICE_MANAGEMENT>'] = self.get_device_management_string(
            config_path)
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

    def get_access_ports_string(self, config_path):
        access_ports_file = open(config_path + 'switch_interface.txt', 'r')
        access_ports_template = access_ports_file.read()
        access_ports_file.close()
        access_port_dict = {}
        legacy_qos_required = False
        stack_port_names = get_stack_port_names(self.device_record)
        for access_port_block_record in AccessPortBlock.objects.filter(access_switch=self.device_record):
            access_vlan = access_port_block_record.access_vlan
            voice_vlan = access_port_block_record.voice_vlan
            legacy_qos = access_port_block_record.legacy_qos
            description_string = base_system.get_interface_description(
                'access', access_vlan=access_vlan, voice_vlan=voice_vlan)
            voice_statement_string = self.get_voice_statement_string(
                config_path, voice_vlan)
            legacy_qos_required = legacy_qos_required or legacy_qos
            qos_statement_string = self.get_qos_statement_string(
                config_path, legacy_qos)
            for port_index in range(stack_port_names.index((access_port_block_record.start_intr,)*2), stack_port_names.index((access_port_block_record.end_intr,)*2)):
                access_port_dict[port_index] = access_ports_template.replace(
                    '<INTR>', stack_port_names[port_index][0])
                access_port_dict[port_index] = access_port_dict[port_index].replace(
                    '<INTR_DESC>', description_string)
                access_port_dict[port_index] = access_port_dict[port_index].replace(
                    '<ACCESS_VLAN>', str(access_vlan))
                access_port_dict[port_index] = access_port_dict[port_index].replace(
                    '<VOICE_STATEMENT>', voice_statement_string)
                access_port_dict[port_index] = access_port_dict[port_index].replace(
                    '<QoS_STATEMENT>', qos_statement_string)
        access_port_string = ''
        for access_port_value in access_port_dict.values():
            access_port_string = access_port_string + '\n' + access_port_value
        return legacy_qos_required, access_port_string

    def get_qos_policy_string(self, config_path, legacy_qos_required):
        qos_policy_string = ''
        if legacy_qos_required:
            qos_policy_file = open(config_path + 'qos_lan_ingress.txt', 'r')
            qos_policy_string = qos_policy_file.read()
            qos_policy_file.close()
        return qos_policy_string

    def get_voice_statement_string(self, config_path, voice_vlan):
        voice_statement_string = ''
        if voice_vlan:
            voice_statement_file = open(
                config_path + 'switch_voice.txt', 'r')
            voice_statement_template = voice_statement_file.read()
            voice_statement_file.close()
            voice_statement_string = '\n' + voice_statement_template.replace(
                '<VOICE_VLAN>', str(voice_vlan))
        return voice_statement_string

    def get_qos_statement_string(self, config_path, legacy_qos):
        qos_string = ''
        if legacy_qos:
            qos_statement_file = open(
                config_path + 'qos_statement.txt', 'r')
            qos_statement_template = qos_statement_file.read()
            qos_statement_file.close()
            qos_string = qos_statement_template.replace('<FLOW>', 'output')
            qos_string = qos_string.replace(
                '<QoS_POLICY>', base_system.QOS_POLICIES['LAN Ingress'])
        return qos_string

    def get_priority_string(self, config_path):
        priority_file = open(config_path + 'switch_priority.txt', 'r')
        priority_template = priority_file.read()
        priority_file.close()
        priority_string = ''
        priority_start = 15
        for switch_number in range(self.device_record.switch_count):
            string_segment = priority_template.replace(
                '<SWI_NUM>', str(switch_number+1))
            switch_priority = priority_start-switch_number
            if switch_priority > 13:
                string_segment = string_segment.replace(
                    '<SWI_PRI>', str(switch_priority))
            else:
                string_segment = string_segment.replace('<SWI_PRI>', '1')
            priority_string = priority_string + '\n' + string_segment
        return priority_string

    def get_vlan_svi_strings(self, config_path):
        vlan_file = open(config_path + 'switch_vlan.txt', 'r')
        vlan_template = vlan_file.read()
        vlan_file.close()
        svi_file = open(config_path + 'switch_svi.txt', 'r')
        svi_template = svi_file.read()
        svi_file.close()
        vlan_string = ''
        svi_string = ''
        for vlan_record in Vlan.objects.filter(access_switch=self.device_record):
            vlan_id_str = str(vlan_record.vlan_id)
            string_segment_vlan = vlan_template.replace(
                '<VLAN_ID>', vlan_id_str)
            string_segment_vlan = string_segment_vlan.replace(
                '<VLAN_NAME>', vlan_record.name)
            vlan_string = vlan_string + '\n' + string_segment_vlan
            string_segment_svi = svi_template.replace('<VLAN_ID>', vlan_id_str)
            string_segment_svi = string_segment_svi.replace('<VLAN_DESC>', base_system.get_interface_description(
                'vlan', vlan_note=vlan_record.vlan_type+str(vlan_record.vlan_id)))
            string_segment_svi = string_segment_svi.replace(
                '<VLAN_IP>', vlan_record.svi_ip)
            string_segment_svi = string_segment_svi.replace('<VLAN_MASK>', str(
                IPv4Network(vlan_record.svi_ip + vlan_record.svi_mask_length, False).netmask))
            string_segment_svi = string_segment_svi.replace(
                '<VLAN_HELPERS>', self.get_helper_strings(config_path))
            svi_string = svi_string + '\n' + string_segment_svi
        return vlan_string, svi_string

    def get_helper_strings(self, config_path):
        helper_file = open(config_path + 'ip_helper_' +
                           self.site_record.nearest_dc + '.txt', 'r')
        helper_template = helper_file.read()
        helper_file.close()
        return '\n' + helper_template

    def get_ospf_stub_string(self, config_path):
        ospf_stub_file = open(config_path + 'ospf_stub.txt', 'r')
        ospf_stub_template = ospf_stub_file.read()
        ospf_stub_file.close()
        ospf_stub_string = ''
        if self.uplink_type == 'core':
            ospf_stub_string = ospf_stub_template.replace(
                '<AREA>', str(self.device_record.closet.floor))
        return ospf_stub_string

    def get_device_management_string(self, config_path):
        management_file = open(
            config_path + 'management_switch_' + self.site_record.nearest_dc + '.txt', 'r')
        management_template = management_file.read()
        management_file.close()
        management_template = management_template.replace(
            '<SITE_ADDRESS>', self.site_record.address)
        return management_template


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
    device_dict[key_prefix + '_LOOPBACK'] = access_switch_record.loopback_ip
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
