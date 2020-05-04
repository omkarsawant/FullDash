from ipaddress import IPv4Network


class SubnetPlanner:
    def __init__(self, supernets):
        self.supernets = [IPv4Network(supernet) for supernet in supernets]
        self.supernet_breakdown = []
        self.supernet_breakdown_archive = []

    def adjust_subnet_breakdown(self, subnet_list, subnet, remaining_subnet):
        subnet_list.remove(subnet)
        subnet_list.extend(remaining_subnet)
        subnet_list.sort()

    def assign_subnet(self, prefix_length):
        if not self.supernet_breakdown:
            if not self.supernets:
                return None
            self.supernet_breakdown = [self.supernets.pop(0)]
        subnet = None
        for supernet in self.supernet_breakdown:
            try:
                if supernet.prefixlen > prefix_length:
                    continue
                subnet = next(supernet.subnets(new_prefix=prefix_length))
                break
            except:
                continue
        if not subnet:
            self.supernet_breakdown_archive.extend(self.supernet_breakdown)
            self.supernet_breakdown = None
            self.assign_subnet(prefix_length)
        else:
            remaining_supernet = list(supernet.address_exclude(subnet))
            self.adjust_subnet_breakdown(
                self.supernet_breakdown, supernet, remaining_supernet)
            return subnet

    def exclude_subnets(self, excluded_subnets):
        extra_subnets = []
        for excluded_subnet in excluded_subnets:
            supernets = self.supernets.copy()
            remaining_supernet = None
            for supernet in supernets:
                try:
                    remaining_supernet = list(
                        supernet.address_exclude(excluded_subnet))
                except:
                    continue
                self.adjust_subnet_breakdown(
                    self.supernets, supernet, remaining_supernet)
                break
            if not remaining_supernet:
                extra_subnets.append(str(excluded_subnet))
        return extra_subnets
