from kazoo.client import KazooClient


class ZooKeeperManager:
    def __init__(self, server_id: str, hosts: str = "127.0.0.1:2181"):
        self.server_id = server_id
        self.client = KazooClient(hosts=hosts)

    def connect(self):
        self.client.start()
        print("Connected to ZooKeeper")

        if not self.client.exists("/servers"):
            self.client.ensure_path("/servers")

        path = f"/servers/{self.server_id}"

        self.client.create(
            path,
            ephemeral=True,
            makepath=True
        )

        print(f"Registered server: {self.server_id}")

    # הוסיפי את המתודה הזו
    def get_live_servers(self) -> list[str]:
        try:
            servers = self.client.get_children("/servers")
            return sorted(servers)
        except Exception as error:
            print(f"Failed to get live servers: {error}")
            return []

    def close(self):
        self.client.stop()
        self.client.close()
        print("Disconnected from ZooKeeper")


if __name__ == "__main__":
    manager = ZooKeeperManager("server-5001")
    manager.connect()

    input("Press Enter to exit...")

    manager.close()

