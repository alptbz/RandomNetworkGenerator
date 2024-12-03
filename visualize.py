import pandas as pd
from jaal import Jaal
import helpers


def visualize_network(routers, connections):
    nodes = pd.DataFrame([{"id": router.num, "title": router.name} for router in routers])
    edges = pd.DataFrame([
        {"from": connection.router_left.num, "to": connection.router_right.num, "label": str(connection.network)}
        for connection in connections
    ])

    # Visualize with Jaal
    Jaal(edges, nodes).plot()


if __name__ == "__main__":
    routers, connections = helpers.load_from_file()
    # Visualize and save the network
    visualize_network(routers, connections)
