from ydk.providers import NetconfServiceProvider
from ydk.services import Datastore, ExecutorService, NetconfService
import logging


def get_bgp():
    from ydk.models.openconfig import openconfig_bgp
    bgp = openconfig_bgp.Bgp()
    global_ = openconfig_bgp.Bgp.Global()
    bgp.global_ = global_
    return bgp


def get_interface():
    from ydk.models.openconfig import openconfig_interfaces
    from ydk.types import Empty
    interfaces = openconfig_interfaces.Interfaces()
    return interfaces


def get_ydk():
    return get_bgp()
    # return get_interface()


def set_bgp():
    from ydk.models.openconfig import openconfig_bgp
    bgp = openconfig_bgp.Bgp()
    global_ = openconfig_bgp.Bgp.Global()
    config = openconfig_bgp.Bgp.Global.Config()
    config.as_ = 69273
    config.router_id = '1.1.1.2'
    global_.config = config
    bgp.global_ = global_
    return bgp


def set_interface():
    from ydk.models.ietf import iana_if_type
    from ydk.models.openconfig import openconfig_interfaces
    interfaces = openconfig_interfaces.Interfaces()
    interface = openconfig_interfaces.Interfaces.Interface()
    interface.name = 'GigabitEthernet2'
    config = openconfig_interfaces.Interfaces.Interface.Config()
    config.description = 'testtest'
    config.enabled = True
    config.name = 'GigabitEthernet2'
    config.type = iana_if_type.EthernetCsmacd()
    interface.config = config
    interfaces.interface.append(interface)
    return interfaces


def set_wr():
    from ydk.models.cisco_ios_xe import cisco_ia
    wr = cisco_ia.SaveConfig()
    return wr


def set_ydk():
    return set_bgp()
    # return set_interface()


if __name__ == "__main__":
    logger = logging.getLogger("ydk")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(("%(asctime)s - %(name)s - "
                                   "%(levelname)s - %(message)s"))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    provider = NetconfServiceProvider(address='192.168.253.4',
                                      username='admin',
                                      password='50olmw1d',
                                      protocol='ssh',
                                      port=830)
    netconf_service = NetconfService()
    executor_service = ExecutorService()

    # netconf_service.edit_config(provider, Datastore.running, set_ydk())
    netconf_service.get_config(provider, Datastore.running, get_ydk())

    executor_service.execute_rpc(provider, set_wr())
    netconf_service.close_session(provider)
