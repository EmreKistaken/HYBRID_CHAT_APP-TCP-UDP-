# 📁 Technical Report: `network_chat` Directory

This report provides an in-depth analysis of the `network_chat` directory, which contains the Python-based backend and desktop client logic of the project.

## 1. Overview and File Structure

The `network_chat` module contains the core logic of the project and includes all components of the client-server architecture.

```
network_chat/
├── __init__.py                 # Indicates that this is a Python package.
├── common/                     # Code shared between server and client.
│   ├── message.py              # Defines the application's message protocol.
│   └── utils.py                # Helper functions and UDP Reliability Manager.
├── server/                     # Server-side code.
│   └── server.py               # TCP/UDP hybrid server application.
├── client/                     # Desktop client code.
│   ├── client.py               # Client's network and logic layer.
│   └── gui.py                  # Pygame and CustomTkinter-based GUI.
├── assets/                     # Assets used by the GUI.
│   └── notify.wav              # New message notification sound.
└── tests/                      # Unit and integration tests.
    └── test_chat.py
```

---

## 2. Component Analysis

### 🔹 `network_chat/common/` - Shared Components

This directory contains the fundamental code used by both server and client sides. This prevents code duplication and ensures a consistent structure.

#### `message.py`
This file defines the **messaging protocol** that forms the foundation of communication between client and server.

*   **`MessageType(Enum)`**: An Enum class that defines all message types that can be used in the application (e.g., `CONNECT`, `CHAT`, `UDP_STATUS`, `UDP_ACK`).
*   **`Message(dataclass)`**: Defines the standard structure for all messages. Each message contains the following fields:
    *   `msg_type`: Type of the message.
    *   `sender`: User who sent the message.
    *   `content`: Content of the message.
    *   `seq_num`, `ack_num`, `is_udp`: Fields added for UDP reliability mechanism.
*   **`MessageFactory`**: A factory class used to easily create different types of messages. Contains methods such as `create_chat()` or `create_udp_status()`.

#### `utils.py`
This file contains helper functions used throughout the project and one of the most critical components, the **UDP Reliability Manager**.

*   **`send_message()` / `receive_message()`**: Ensures secure sending and receiving of messages over TCP sockets by adding length information to the beginning of messages (framing).
*   **`send_udp_message()` / `receive_udp_message()`**: Sends and receives messages directly over UDP sockets.
*   **`UDPReliabilityManager(class)`**: Creates our own reliability layer against UDP's unreliable nature.
    *   **Sequence Numbers (`seq_num`)**: Assigns a unique number to each UDP message sent.
    *   **Acknowledgment Packets (ACKs)**: Processes acknowledgments from the other side with the `handle_ack()` method and removes messages waiting for acknowledgment from the list.
    *   **Timeout and Retransmission**: The `check_timeouts()` method retransmits messages that don't receive acknowledgment within a certain time (timeout) up to `max_retries` times.

---

### サーバー `network_chat/server/` - Server

This directory contains the logic of the central server to which all clients connect.

#### `server.py`
This file runs the **hybrid server** that listens to both TCP and UDP requests simultaneously.

*   **`UserConnection(dataclass)`**: A data class that represents each user connected to the server. Holds the user's TCP socket, UDP address, status, and connections.
*   **`ChatServer(class)`**: The main server class.
    *   **`__init__()`**: Creates both TCP (`SOCK_STREAM`) and UDP (`SOCK_DGRAM`) sockets. Sets the UDP socket to non-blocking mode with `setblocking(False)`. Creates an object from `UDPReliabilityManager`.
    *   **`start()`**: Starts the server and runs three main threads:
        1.  **TCP Accept Thread**: Accepts new TCP connections with `server_socket.accept()` and starts a `_handle_client` thread for each.
        2.  **`_udp_handler()`**: Listens to the UDP socket using `select.select()`. Only reads when data arrives, improving performance and preventing unnecessary loops. Routes incoming UDP messages to appropriate functions based on their type (`_handle_udp_status` etc.).
        3.  **`_udp_timeout_checker()`**: Periodically checks for timed-out messages in `UDPReliabilityManager` and retransmits them.
    *   **`_handle_udp_*()` functions**: Immediately sends an **ACK packet** in response to an incoming UDP message and then performs the operation required by the message (e.g., updating status and broadcasting to other clients).
    *   **`_broadcast_*()` functions**: Broadcasts an event (new user, status change, etc.) to all clients via both TCP and UDP.

---

### 💻 `network_chat/client/` - Desktop Client

This directory contains the desktop application through which users interact with the server.

#### `client.py`
This file manages the client's network and business logic. Establishes communication with the server and processes events from the GUI.

*   **`ChatClient(class)`**: The main client class.
    *   **`__init__()`**: Initializes the GUI (`ChatGUI`), prepares TCP and UDP sockets for creation, and creates a `UDPReliabilityManager` object.
    *   **`connect()`**: Connects to the server via TCP, then runs necessary threads (UDP receiver and timeout checker) to start UDP communication.
    *   **`_message_receiver()` / `_udp_receiver()`**: Listens to both TCP and UDP sockets in separate threads to receive messages from the server. Forwards incoming messages to callback functions to update the GUI.
    *   **`update_status()` / `send_typing_indicator()`**: Sends user actions (status change, etc.) to the server. For such quick updates, it sends messages via both reliable TCP and fast UDP.

#### `gui.py`
This file contains the user interface created using `CustomTkinter` and `Pygame` (for sound) libraries.

*   **`ChatGUI(class)`**: Manages the entire interface.
    *   Creates components such as user login screen, main chat window, user list, and status menu.
    *   Displays data from `client.py` (new messages, user list) in the interface.
    *   Captures user actions (sending messages, changing status) and calls relevant functions in `client.py`.
    *   **`play_notify_sound()`**: Plays the `notify.wav` sound file using `pygame.mixer` when a new message arrives.
    *   **Matplotlib Integration**: Draws a graph to visualize network topology.

---

## 3. Performance Testing and Measurement System

The project includes a comprehensive performance testing infrastructure to measure and optimize system performance. This system provides various metrics to evaluate the efficiency of the hybrid TCP/UDP architecture.

### 📊 Performance Metrics

#### Latency
- **Definition**: Time between sending a message and receiving a response
- **Measurement**: In milliseconds (ms)
- **Target Values**:
  - Excellent: < 10ms
  - Good: 10-50ms
  - Acceptable: 50-100ms
  - Measured: > 100ms

#### Throughput
- **Definition**: Number of messages processed per unit time
- **Measurement**: Messages per second (msg/sec)
- **Target Values**:
  - Excellent: > 1000 msg/sec
  - Good: 500-1000 msg/sec
  - Acceptable: 100-500 msg/sec
  - Measured: < 100 msg/sec

#### Scalability
- **Definition**: System performance based on concurrent user count
- **Measurement**: Average latency and throughput per user
- **Test Scenarios**: 1-10 concurrent users

### 🧪 Performance Test Scripts

#### `quick_test.py` - Quick Performance Test
Script that quickly performs the most basic performance measurements.

**Features:**
- Latency test with 10 messages
- Throughput test for 3 seconds
- Automatic evaluation and reporting
- Collision prevention with unique usernames

**Usage:**
```bash
python quick_test.py
```

**Sample Output:**
```
🚀 Quick Performance Test Starting
==================================================
⚠️  Make sure the server is running!
   python -m network_chat.server.server
   Server ports: TCP=8000, UDP=8001
Press Enter to continue...

1️⃣  Latency Test
--------------------
🔄 Running latency test with 10 messages...
✅ Connected to server: Welcome to the chat server!
✅ Latency Results:
   Average: 15.23 ms
   Minimum: 12.45 ms
   Maximum: 18.67 ms
   Successful measurements: 10/10

2️⃣  Throughput Test
--------------------
🔄 Running throughput test for 3 seconds...
✅ Throughput Results:
   Messages sent: 45
   Successful responses: 43
   Response rate: 95.6%
   Duration: 3.02 seconds
   Throughput: 14.90 messages/second

📊 QUICK TEST SUMMARY
==================================================
Latency: 15.23 ms
Throughput: 14.90 msg/sec

📈 EVALUATION
--------------------
✅ Latency: Good (10-50ms)
⚠️  Throughput: Acceptable (100-500 msg/sec)

✅ Test completed!
```

#### `performance_benchmark.py` - Comprehensive Benchmark
Advanced test script for detailed performance analysis.

**Features:**
- Multiple test scenarios
- Statistical analysis
- CSV reporting
- Graph generation
- Stress testing

**Usage:**
```bash
python performance_benchmark.py
```

#### `simple_performance_test.py` - Simple Performance Test
For intermediate-level performance measurements.

**Features:**
- TCP and UDP latency comparison
- Throughput testing
- Basic scalability testing

### 🔧 Test Infrastructure

#### Message Protocol Compatibility
All test scripts use the message format expected by the server:
- JSON serialization with `Message` class
- Connection establishment with `CONNECT` message
- TCP framing with length prefix
- Message tracking with unique `msg_id`

#### Error Handling
- Timeout mechanisms (2-5 seconds)
- Automatic retry on connection errors
- Automatic resolution of username conflicts
- Detailed error reporting

#### Performance Optimization
- Use of non-blocking I/O
- Short delays between message sends (50-100ms)
- Prevention of server overload
- Memory usage optimization

### 📈 Result Analysis

#### Latency Analysis
- **Low Latency (< 10ms)**: Local network, optimized code
- **Medium Latency (10-50ms)**: Normal performance, acceptable
- **High Latency (> 50ms)**: Network issues, server load

#### Throughput Analysis
- **High Throughput (> 1000 msg/sec)**: Excellent performance
- **Medium Throughput (100-1000 msg/sec)**: Normal performance
- **Low Throughput (< 100 msg/sec)**: Optimization needed

#### Scalability Analysis
- **Linear Scaling**: Proportional performance decrease as user count increases
- **Exponential Decrease**: System bottlenecks, optimization needed
- **Constant Performance**: Perfect scalability

### 🛠️ Test Environment Setup

#### Requirements
```bash
# Virtual environment activation
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Required packages (available in requirements.txt)
pip install -r requirements.txt
```

#### Server Startup
```bash
# Start the server
python -m network_chat.server.server

# Or alternatively
cd network_chat/server
python server.py
```

#### Running Tests
```bash
# Quick test
python quick_test.py

# Comprehensive test
python performance_benchmark.py

# Simple test
python simple_performance_test.py
```

### 🔍 Troubleshooting

#### Common Errors
1. **"Connection refused"**: Server not running
2. **"Username already taken"**: Test script run repeatedly
3. **"Invalid initial message"**: Message format incompatibility
4. **"Response timeout"**: Network delay or server load

#### Solutions
- Ensure the server is running
- Check port numbers (TCP: 8000, UDP: 8001)
- Run test scripts with unique usernames
- Check network connection

This performance testing system provides the ability to continuously monitor and optimize the performance of the hybrid TCP/UDP chat application.

---

