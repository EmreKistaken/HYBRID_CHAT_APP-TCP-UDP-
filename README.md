# VoXLy - A Resilient Chat System

A multi-user chat application designed for resilience and performance, implementing custom communication protocols over both TCP and UDP. This system features robust network topology discovery, a user-friendly graphical interface, and detailed performance analysis tools.

## Key Features

- **Dual Protocol Support:** Uses TCP for reliable core messaging and UDP for efficient network discovery and status updates.
- **Custom Message Protocol:** A well-defined packet structure for clear and efficient communication.
- **Network Topology Discovery:** Actively discovers and visualizes the network topology of connected clients.
- **Graphical User Interface (GUI):** An intuitive interface built with `customtkinter` for a modern user experience.
- **Reliability Layer for UDP:** Implements acknowledgments and retransmissions for critical UDP messages.
- **Performance Testing Suite:** Includes scripts to measure and visualize key metrics like latency and throughput.
- **Real-time User Status:** Tracks and displays user online/offline status.

## Project Structure

The project is organized into modules for clarity and scalability:

```
Computer Network Project/
├── network_chat/
│   ├── server/
│   │   └── server.py         # Main server application
│   ├── client/
│   │   ├── client.py         # Main client application
│   │   └── gui.py            # GUI implementation
│   ├── common/
│   │   ├── message.py        # Core Message class and types
│   │   └── utils.py          # Shared utility functions
│   └── assets/
│       └── notify.wav        # Notification sound
├── performance_graphs/       # Directory for generated performance charts
├── quick_test.py             # Script for quick latency/throughput tests
├── performance_graphs.py     # Script to generate detailed performance graphs
├── requirements.txt          # A complete list of project dependencies
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A working `pip` package manager

### Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd Computer-Network-Project
    ```

2.  **Create and Activate a Virtual Environment** (Recommended)
    This isolates the project's dependencies from your system's Python installation.

    - On **Windows**:
      ```bash
      python -m venv venv
      .\venv\Scripts\activate
      ```
    - On **macOS/Linux**:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3.  **Install Dependencies**
    All required libraries are listed in `requirements.txt`. Install them with a single command:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run the Application

**Important:** The server and client must be run as modules from the project's root directory.

1.  **Start the Server**
    Open a terminal and run the following command. The server will start listening on TCP port 8000 and UDP port 8001.
    ```bash
    python -m network_chat.server.server
    ```

2.  **Start the Client**
    Open one or more new terminals and run the client application. Each instance will open a new GUI window.
    ```bash
    python -m network_chat.client.client
    ```

## Testing and Performance Analysis

The project includes two powerful scripts for performance evaluation. Ensure the server is running before executing them.

1.  **Quick Performance Test**
    This script runs a quick check of message latency and throughput, printing a summary to the console.
    ```bash
    python quick_test.py
    ```

2.  **Detailed Performance Graphs**
    This script performs more detailed tests and generates visual graphs for latency and throughput. The output graphs are saved in the `performance_graphs/` directory.
    ```bash
    python performance_graphs.py
    ```

## Core Dependencies

A brief overview of the key libraries used:

-   `customtkinter`: For the modern graphical user interface.
-   `matplotlib` & `numpy`: To generate performance graphs.
-   `networkx`: For network topology visualization.
-   `rich`: For enhanced terminal output formatting.

All dependencies and their specific versions are pinned in `requirements.txt`.

## License

This project was created for educational purposes as part of a Computer Networks course.