import typing
from ipaddress import IPv4Network


class RouterConnection:

    def __init__(self, router_left, router_right, network):
        self.router_left: Router = router_left
        self.router_right: Router = router_right
        self.network = network


    def equals(self, router_left, router_right):
        return (self.router_left == router_left and self.router_right == router_right) or (self.router_left == router_right and self.router_right == router_left)

    def get_other(self, router):
        if router == self.router_left:
            return self.router_right
        return self.router_left


class Router:

    def __init__(self, num, router_ip):
        self.num = num
        self.name = f"R{num}"
        self.connections: typing.List[RouterConnection] = []  # Stores (connected router, assigned IP)
        self.interfaces = []
        self.routing_table = []
        self.interface_counter = 0
        self.router_ip = router_ip

    def add_static_route(self, network, next_hop):
        destination = f"{network.network_address}/{network.prefixlen}"
        next_hop = str(next_hop)
        if next((e for e in self.routing_table if e["destination"] == destination), None) is None:
            self.routing_table.append({
                "type": "S",
                "destination": destination,
                "next_hop": next_hop
            })

    def delete_entries_by_next_hop(self, next_hop):
        self.routing_table = [entry for entry in self.routing_table if entry["next_hop"] != next_hop]

    def add_connection(self, other_router: typing.Self, network) -> RouterConnection:
        # Assign IPs for the /30 network
        ip_self = network.network_address + 1
        ip_other = network.network_address + 2

        # Assign unique interface numbers
        self_interface = f"GigabitEthernet {self.interface_counter}/0"
        self.interface_counter += 1
        other_interface = f"GigabitEthernet {other_router.interface_counter}/0"
        other_router.interface_counter += 1

        # Update connections and routing information
        connection = RouterConnection(self, other_router, network)

        self.connections.append(connection)
        self.interfaces.append({
            "comment" : other_router.name,
            "interface": self_interface,
            "network": network,
            "interface_ip": str(ip_self)
        })
        self.routing_table.append({
            "type": "C",
            "destination": f"{network.network_address}/{network.prefixlen}",
            "next_hop": str(ip_other)
        })

        other_router.connections.append(connection)
        other_router.interfaces.append({
            "comment": self.name,
            "interface": other_interface,
            "network": network,
            "interface_ip": str(ip_other)
        })
        other_router.routing_table.append({
            "type": "C",
            "destination": f"{network.network_address}/{network.prefixlen}",
            "next_hop": str(ip_self)
        })

        return connection

    def generate_config(self):
        lines = []
        lines.append(f"! Router {self.name}")
        for interface in self.interfaces:
            lines.append(f"! connected to {interface['comment']}")
            lines.append(f"interface {interface['interface']} ")
            lines.append(f"{interface['interface_ip']}/{interface['network'].prefixlen}")
        lines.append(f"\n! Routing {self.name}")
        for route in self.routing_table:
            lines.append(f"{route['type']} {route['destination']} {route['next_hop']}")
        return lines

    def get_matching_interface_address(self, router_from: typing.Self):
        for i_own in self.interfaces:
            for i_other in router_from.interfaces:
                if i_own["network"] == i_other["network"]:
                    return i_other["interface_ip"]
        return None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()




