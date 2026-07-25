from kazoo.client import KazooClient


class ClientDiscovery:
    def __init__(self, hosts: str = "127.0.0.1:2181"):
        self.client = KazooClient(hosts=hosts)

    def connect(self):
        self.client.start()

    def get_leader_server(self) -> str | None:
        election_path = "/election"

        children = self.client.get_children(election_path)

        if not children:
            return None

        children.sort()

        leader_node = children[0]
        leader_path = f"{election_path}/{leader_node}"

        leader_server, _ = self.client.get(leader_path)

        return leader_server.decode("utf-8")
    

    def close(self):
        self.client.stop()
        self.client.close()

