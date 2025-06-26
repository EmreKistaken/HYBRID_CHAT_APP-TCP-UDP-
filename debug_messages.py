#!/usr/bin/env python3
"""
Debug script to test message sending and receiving.
"""

import socket
import json
import time
from network_chat.common.message import Message, MessageType, MessageFactory
from network_chat.common.utils import send_message, receive_message

def test_message_sending(username, host='localhost', port=8000):
    """Test message sending for a specific user."""
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
            
            # Send a test message
            test_message = MessageFactory.create_chat(username, f"Hello from {username}!")
            send_message(sock, test_message)
            print(f"📤 {username} sent message: {test_message.content}")
            
            # Wait for messages from others
            print(f"👂 {username} listening for messages...")
            sock.settimeout(5)  # 5 second timeout
            
            try:
                while True:
                    message = receive_message(sock)
                    if message:
                        if message.msg_type == MessageType.CHAT:
                            print(f"📥 {username} received: {message.sender}: {message.content}")
                        elif message.msg_type == MessageType.STATUS:
                            print(f"📊 {username} status update: {message.sender} {message.content}")
                        elif message.msg_type == MessageType.DISCOVER_RESP:
                            topology = json.loads(message.content)
                            print(f"🌐 {username} topology: {list(topology.keys())}")
            except socket.timeout:
                print(f"⏰ {username} timeout waiting for messages")
            
            return sock
        else:
            print(f"❌ {username} connection failed")
            return None
            
    except Exception as e:
        print(f"❌ Error with {username}: {e}")
        return None

def main():
    """Test message sending between users."""
    print("💬 Testing message system...")
    
    # Test users
    users = ["Alice", "Bob"]
    connections = {}
    
    # Connect all users
    for user in users:
        sock = test_message_sending(user)
        if sock:
            connections[user] = sock
        time.sleep(1)  # Wait between connections
    
    print(f"\n📈 Connected users: {list(connections.keys())}")
    
    # Test message exchange
    if len(connections) > 1:
        print("\n🔄 Testing message exchange...")
        
        # Alice sends a message
        if "Alice" in connections:
            alice_sock = connections["Alice"]
            message = MessageFactory.create_chat("Alice", "Hello everyone!")
            send_message(alice_sock, message)
            print("📤 Alice sent: Hello everyone!")
            time.sleep(1)
        
        # Bob sends a reply
        if "Bob" in connections:
            bob_sock = connections["Bob"]
            message = MessageFactory.create_chat("Bob", "Hi Alice!")
            send_message(bob_sock, message)
            print("📤 Bob sent: Hi Alice!")
            time.sleep(1)
        
        # Listen for messages
        print("\n👂 Listening for messages...")
        for user, sock in connections.items():
            sock.settimeout(3)
            try:
                while True:
                    message = receive_message(sock)
                    if message and message.msg_type == MessageType.CHAT:
                        print(f"📥 {user} received: {message.sender}: {message.content}")
            except socket.timeout:
                print(f"⏰ {user} timeout")
    
    # Clean up
    for sock in connections.values():
        try:
            sock.close()
        except:
            pass
    
    print("\n✅ Message test completed!")

if __name__ == "__main__":
    main() 