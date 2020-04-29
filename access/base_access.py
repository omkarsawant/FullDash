from .models import AccessSwitch, Vlan


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
