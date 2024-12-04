import random
import textwrap
from typing import List

import fun_content
import globals
import helpers
import posprinter
from router import Router


def generate_random_packet(router_a, routers):
    random_router_b: Router = random.choice(routers)

    lines = [
        "-",
        f"[MESSAGE DELIVERY ORDER",
        f"[{random.randint(100,999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
        "-",
        "Deliver without hesitation. Delay is treason.".upper(),
        "-",
        f"SRC: {router_a.router_ip.network_address}",
        f"DST: {random_router_b.router_ip.network_address}",
        f"MSG",
        f'-',
    ]

    lines.extend(textwrap.wrap(random.choice(fun_content.evil_orders), width=48))
    lines.append("-")
    lines.append(f'///' + ("*" * router_a.num * 2) + "/" + ("*" * random_router_b.num * 2) + ('\\' * (48 - router_a.num * 2 - 4 - random_router_b.num * 2)))
    lines.append("-")

    return lines


if __name__ == "__main__":
    routers, connections = helpers.load_from_file()
    for router_name in globals.starting_routers:
        router = next((r for r in routers if r.name == router_name), None)
        all_router_except_source: List[Router] = routers.copy()
        all_router_except_source.remove(router)
        for i in range(0, globals.num_of_packets_per_router):
            random_packet = generate_random_packet(router, all_router_except_source)
            [print(line) for line in random_packet]
            #posprinter.print_pos(random_packet)
