from datetime import datetime
from typing import List

import random
import ipaddress
import os
import json
from router import Router, RouterConnection
from dijkstar import Graph, find_path
import pickle


def every_router_has_three_connections(routers: List[Router]) -> bool:
    for router in routers:
        if len(router.connections) < 3:
            return False
    return True


def generate_random_network(num_routers, subnets, router_ips, max_num_of_connections):
    routers = []

    router_ips.pop(0)
    # Create routers
    for i in range(num_routers):
        routers.append(Router(i+1, router_ips.pop(0)))

    connections: List[RouterConnection] = []

    safety_counter = 0

    routers_to_connect = routers.copy()
    random.shuffle(routers_to_connect)
    while len(routers_to_connect) >= 2:
        router_a = routers_to_connect.pop()
        router_b = routers_to_connect[-1]
        connections.append(router_a.add_connection(router_b, subnets.pop()))
        print(f"Connection from {router_a.name} to {router_b.name}")

    while not every_router_has_three_connections(routers) and safety_counter < 100000:
        safety_counter += 1
        router_a:Router = random.choice(routers)
        routers_to_use = routers.copy()
        routers_to_use.remove(router_a)
        router_b:Router = random.choice(routers_to_use)
        if len(router_a.connections) >= max_num_of_connections or len(router_b.connections) >= max_num_of_connections:
            continue
        if next((e for e in connections if e.equals(router_a, router_b)), None) is None:
            connections.append(router_a.add_connection(router_b, subnets.pop()))

    for i in range(0, int(len(routers)/2)):
        router_a: Router = random.choice(routers)
        routers_to_use = routers.copy()
        routers_to_use.remove(router_a)
        router_b: Router = random.choice(routers_to_use)
        if next((e for e in connections if e.equals(router_a, router_b)), None) is None:
            connections.append(router_a.add_connection(router_b, subnets.pop()))

    return routers, connections


def add_static_routes(routers: List[Router], connections, subnets):
    for router in routers:
        for connection in router.connections:
            other_router = connection.get_other(router)
            router.add_static_route(other_router.router_ip, router.get_matching_interface_address(other_router))

    graph = Graph()
    paths: List = []
    for c in connections:
        graph.add_edge(c.router_left.num, c.router_right.num, 1)
    for router_from in routers:
        for router_to in routers:
            if router_to == router_from:
                continue
            path = None
            try:
                path = find_path(graph, router_from.num, router_to.num)
            except:
                c = router_from.add_connection(router_to, subnets.pop())
                connections.append(c)
                graph.add_edge(c.router_left.num, c.router_right.num, 1)
                path = find_path(graph, router_from.num, router_to.num)
                print(f"Added missing connection from {router_from.name} to {router_to.name}")
            paths.append((router_from, router_to, path))

    for p in paths:
        router_from: Router = p[0]
        router_to: Router = p[1]
        path = p[2]
        next_hop_router: Router = next((r for r in routers if r.num == path.nodes[1]), None)
        matching_interface = router_from.get_matching_interface_address(next_hop_router)
        router_from.add_static_route(router_to.router_ip, matching_interface)
        # print(f"Added from {router_from} to {router_to} via {matching_interface} for {path}")

    print("Added all static routes")


def aggregate_by_next_hop(routing_table):
    aggregation = {}
    for entry in routing_table:
        next_hop = entry["next_hop"]
        aggregation[next_hop] = aggregation.get(next_hop, 0) + 1
    return aggregation


def aggregate_one_route_into_default(routers: List[Router]):
    for router in routers:
        static_routes = [rt for rt in router.routing_table if rt["type"] == "S"]
        next_hop_aggregates = aggregate_by_next_hop(router.routing_table)
        max_key = max(next_hop_aggregates, key=lambda x: next_hop_aggregates[x])
        router.delete_entries_by_next_hop(max_key)
        router.add_static_route(ipaddress.IPv4Network("0.0.0.0/0"), max_key)
