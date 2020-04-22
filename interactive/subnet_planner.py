from ipaddress import IPv4Network


class SubnetPlanner:
    def __init__(self, supernet_list):
        self.supernet_list = [IPv4Network(supernet)
                              for supernet in supernet_list]
        self.supernet_breakdown = []
        self.supernet_breakdown_archive = []

    def add_supernet(self, supernet):
        self.supernet_list.append(IPv4Network(supernet))

    def assign_subnet(self, prefix):
        if not self.supernet_breakdown:
            if not self.supernet_list:
                # TODO: get from base_system
                raise ValueError("Could not assign subnet")
            self.supernet_breakdown = [self.supernet_list.pop(0)]
        subnet = None
        for supernet in self.supernet_breakdown:
            try:
                subnet = next(supernet.subnets(new_prefix=prefix))
                break
            except:
                continue
        if not subnet:
            self.supernet_breakdown_archive.extend(self.supernet_breakdown)
            self.supernet_breakdown = None
            self.assign_subnet(prefix)
        else:
            self.supernet_breakdown.remove(supernet)
            remaining_supernet = list(supernet.address_exclude(subnet))
            self.supernet_breakdown.extend(remaining_supernet)
            self.supernet_breakdown.sort()
            return subnet
