class LeaderElection:
    def __init__(self, zookeeper_client, server_id: str):
        self.client = zookeeper_client
        self.server_id = server_id
        self.election_path = "/election"
        self.node_path = None
        self.is_leader = False

    def join_election(self) -> None:
        self.client.ensure_path(self.election_path)

        self.node_path = self.client.create(
            f"{self.election_path}/candidate-",
            value=self.server_id.encode("utf-8"),
            ephemeral=True,
            sequence=True
        )

        print(
            f"{self.server_id} joined election as "
            f"{self.node_path}"
        )

    def elect_leader(self) -> bool:
        children = self.client.get_children(self.election_path)
        children.sort()

        my_node = self.node_path.split("/")[-1]

        if children[0] == my_node:
            self.is_leader = True
            print(f"{self.server_id} is the LEADER")
        else:
            self.is_leader = False
            print(f"{self.server_id} is a FOLLOWER")

        return self.is_leader

    