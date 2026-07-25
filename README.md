# Distributed Chat System

A fault-tolerant distributed chat system implemented in Python using TCP sockets and Apache ZooKeeper. The system supports leader election, automatic failover, replication, state recovery, and client reconnection.

---

## Features

- Multi-client chat server
- TCP socket communication
- JSON-based messaging protocol
- Multi-threaded server architecture
- Apache ZooKeeper integration
- Automatic leader election
- Leader failover
- Message replication
- State recovery for recovering servers
- Client automatic reconnection
- Global message ordering
- Message history synchronization

---

## Technologies

- Python 3
- TCP Sockets
- Threading
- Apache ZooKeeper
- Kazoo (Python ZooKeeper Client)
- Git & GitHub

---

## System Architecture

```
                    +----------------+
                    |   ZooKeeper    |
                    +-------+--------+
                            |
        -----------------------------------------
        |                 |                     |
+---------------+ +---------------+ +---------------+
|   Server 1    | |   Server 2    | |   Server 3    |
| Leader/Follower| | Leader/Follower| | Leader/Follower|
+-------+-------+ +-------+-------+ +-------+-------+
        \              |               /
         \             |              /
          \            |             /
           +------------------------+
           |        Clients         |
           +------------------------+
```

ZooKeeper is responsible for:
- Server registration
- Leader election
- Failure detection

The Leader handles all client requests and replicates messages to Followers.

---

## Project Structure

```
DistributedChatSystem/
│
├── client.py
├── server.py
├── protocol.py
├── config.py
│
├── models/
│   └── message.py
│
├── services/
│   ├── leader_election.py
│   ├── client_discovery.py
│   └── state_manager.py
│
├── utils/
│
├── tests/
│
└── README.md
```

---

## Main Components

### Chat Server

- Accepts multiple client connections
- Processes incoming messages
- Broadcasts chat messages
- Maintains message history

---

### Leader Election

ZooKeeper automatically elects one server as the Leader.

Followers continuously monitor the Leader.

If the Leader crashes:

- A new Leader is elected automatically.
- Clients reconnect automatically.

---

### Replication

Every message received by the Leader is replicated to all Followers.

This ensures that every server maintains the same chat history.

---

### Recovery

When a failed server comes back online:

1. It discovers the current Leader.
2. Requests missing messages.
3. Synchronizes its local state.
4. Rejoins the cluster as a fully synchronized server.

---

### Client Failover

If the Leader fails while clients are connected:

1. ZooKeeper elects a new Leader.
2. The client detects the lost connection.
3. The client discovers the new Leader.
4. Automatically reconnects.
5. Continues sending messages without restarting.

---

### Global Message Ordering

Every chat message receives a unique sequential ID.

Example:

```
#1 Hello
#2 Hi
#3 How are you?
#4 Fine
```

Message ordering is preserved even after Leader Failover.

---

## Installation

### Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/DistributedChatSystem.git
cd DistributedChatSystem
```

---

### Install dependencies

```bash
pip install kazoo
```

---

### Start ZooKeeper

Start your local ZooKeeper server before launching the application.

---

## Running the System

### Start Server 1

```bash
python server.py 5001
```

### Start Server 2

```bash
python server.py 5002
```

### Start Server 3

```bash
python server.py 5003
```

### Start Client

```bash
python client.py
```

Run multiple clients to simulate a distributed chat environment.

---

## Failure Scenarios Tested

- Leader failure
- Leader election
- Follower failure
- Follower recovery
- State synchronization
- Client automatic reconnection
- Message replication
- Global message ordering

---

## Example Workflow

1. Start ZooKeeper
2. Start three servers
3. Leader is elected automatically
4. Connect one or more clients
5. Exchange chat messages
6. Stop the Leader
7. Observe automatic Leader election
8. Clients reconnect automatically
9. Continue chatting without restarting clients

---

## Future Improvements

- Persistent message storage
- Secure communication (TLS)
- User authentication
- Private messaging
- Chat rooms
- Load balancing
- Docker deployment

---

## Authors

Final Project

Distributed Systems

Implemented in Python using ZooKeeper and TCP sockets.
