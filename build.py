import ipaddress

import functions
import helpers


if __name__ == "__main__":
    num_routers = 12  # Define the number of routers
    base_network = ipaddress.IPv4Network("10.10.0.0/16")
    base_network_router_ips = ipaddress.IPv4Network("10.50.0.0/24")
    subnets = list(base_network.subnets(new_prefix=30))
    router_ips = list(base_network_router_ips.subnets(new_prefix=32))
    routers, connections = functions.generate_random_network(num_routers, subnets, router_ips, 2)

    functions.add_static_routes(routers,connections,subnets)
    functions.aggregate_one_route_into_default(routers)

    helpers.save_to_json(routers, connections)




