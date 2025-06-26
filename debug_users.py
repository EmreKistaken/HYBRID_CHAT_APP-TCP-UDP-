#!/usr/bin/env python3
"""
Debug script to test user connections and topology updates.
"""

import socket
import json
import time
from network_chat.common.message import Message, MessageType, MessageFactory
from network_chat.common.utils import send_message, receive_message

def test_connection(username, host='localhost', port=8000):
    """Test connection for a specific user."""
    try:
        # Create socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # Send connection request
        connect_msg = MessageFactory.create_connect(username)
        send_message(sock, connect_msg)
        
        # Wait for acknowledgment
        response = receive_message(sock)
        if response and response.msg_type == MessageType.CONNECT_ACK:
            print(f"✅ {username} connected successfully")
            
            # Request topology
            discover_msg = MessageFactory.create_discover(username)
            send_message(sock, discover_msg)
            
            # Wait for topology response
            topology_response = receive_message(sock)
            if topology_response and topology_response.msg_type == MessageType.DISCOVER_RESP:
                topology = json.loads(topology_response.content)
                print(f"📊 Topology for {username}: {json.dumps(topology, indent=2)}")
            
            return sock
        else:
            print(f"❌ {username} connection failed")
            return None
            
    except Exception as e:
        print(f"❌ Error connecting {username}: {e}")
        return None

def main():
    """Test multiple user connections."""
    print("🔍 Testing user connections...")
    
    # Test users
    users = ["Alice", "Bob", "Charlie"]
    connections = {}
    
    # Connect all users
    for user in users:
        sock = test_connection(user)
        if sock:
            connections[user] = sock
        time.sleep(1)  # Wait between connections
    
    print(f"\n📈 Connected users: {list(connections.keys())}")
    
    # Test topology updates
    if len(connections) > 1:
        print("\n🔄 Testing topology updates...")
        for user, sock in connections.items():
            discover_msg = MessageFactory.create_discover(user)
            send_message(sock, discover_msg)
            
            topology_response = receive_message(sock)
            if topology_response:
                topology = json.loads(topology_response.content)
                print(f"📊 {user} sees: {list(topology.keys())}")
    
    # Clean up
    for sock in connections.values():
        try:
            sock.close()
        except:
            pass
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main() 