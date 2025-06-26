#!/usr/bin/env python3
"""
Quick Performance Test - Enhanced Version

This script performs comprehensive performance testing of the chat system.
Make sure the server is running before executing this test!
"""

import time
import socket
import json
import statistics
import sys
import os

# Add network_chat module to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'network_chat'))

from network_chat.common.message import Message, MessageType


def connect_to_server(host='127.0.0.1', port=8000, username='perf_test'):
    """Connect to server and send CONNECT message"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # Send CONNECT message
        connect_msg = Message(
            msg_type=MessageType.CONNECT,
            sender=username,
            content="Performance test connection",
            timestamp=time.time(),
            is_udp=False,
            seq_num=0,
            ack_num=0,
            msg_id=f'connect_{int(time.time() * 1000)}'
        )
        
        msg_json = connect_msg.to_json().encode('utf-8')
        sock.send(len(msg_json).to_bytes(4, 'big'))
        sock.send(msg_json)
        
        # Wait for CONNECT_ACK response
        length_bytes = sock.recv(4)
        if len(length_bytes) == 4:
            response_length = int.from_bytes(length_bytes, 'big')
            response_data = sock.recv(response_length)
            response_msg = Message.from_json(response_data.decode('utf-8'))
            
            if response_msg.msg_type == MessageType.CONNECT_ACK:
                print(f"✅ Connected to server: {response_msg.content}")
                return sock
            elif response_msg.msg_type == MessageType.ERROR:
                print(f"❌ Connection error: {response_msg.content}")
                sock.close()
                return None
        
        sock.close()
        return None
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None


def quick_latency_test(host='127.0.0.1', port=8000, num_tests=50):
    """Enhanced latency test with multiple message sizes"""
    print(f"🔄 Running enhanced latency test with {num_tests} messages...")
    
    try:
        # Connect to server with unique username
        username = f'latency_test_{int(time.time() * 1000)}'
        sock = connect_to_server(host, port, username)
        if not sock:
            return 0
        
        latencies = []
        message_sizes = [64, 128, 256, 512, 1024]  # Different message sizes
        
        for i in range(num_tests):
            # Create test messages with different sizes
            msg_size = message_sizes[i % len(message_sizes)]
            test_content = f'Test message {i} with size {msg_size} bytes. ' + 'A' * (msg_size - 50)
            
            msg = Message(
                msg_type=MessageType.CHAT,
                sender=username,
                content=test_content,
                timestamp=time.time(),
                is_udp=False,
                seq_num=i,
                ack_num=0,
                msg_id=f'test_{i}_{msg_size}'
            )
            
            # Convert message to JSON
            msg_json = msg.to_json().encode('utf-8')
            
            # High precision timing
            start_time = time.perf_counter()
            
            # Send message (4 byte length + message)
            sock.send(len(msg_json).to_bytes(4, 'big'))
            sock.send(msg_json)
            
            # Receive response with timeout
            try:
                sock.settimeout(3.0)  # 3 second timeout
                length_bytes = sock.recv(4)
                if len(length_bytes) == 4:
                    response_length = int.from_bytes(length_bytes, 'big')
                    response_data = sock.recv(response_length)
                    
                    # Validate response
                    if response_data:
                        response_msg = Message.from_json(response_data.decode('utf-8'))
                        
                        # End timing
                        end_time = time.perf_counter()
                        latency_ms = (end_time - start_time) * 1000
                        latencies.append(latency_ms)
                        
                        # Show progress every 10 messages
                        if (i + 1) % 10 == 0:
                            print(f"   Progress: {i + 1}/{num_tests} messages tested")
                    else:
                        print(f"⚠️  Empty response for message {i}")
                else:
                    print(f"⚠️  Invalid response length for message {i}")
            except socket.timeout:
                print(f"⚠️  Response timeout for message {i}")
            except Exception as e:
                print(f"⚠️  Response error for message {i}: {e}")
            
            # Shorter wait time
            time.sleep(0.05)  # 50ms wait
        
        sock.close()
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            median_latency = statistics.median(latencies)
            std_dev = statistics.stdev(latencies) if len(latencies) > 1 else 0
            
            print(f"✅ Enhanced Latency Results:")
            print(f"   Average: {avg_latency:.3f} ms")
            print(f"   Median: {median_latency:.3f} ms")
            print(f"   Minimum: {min_latency:.3f} ms")
            print(f"   Maximum: {max_latency:.3f} ms")
            print(f"   Std Dev: {std_dev:.3f} ms")
            print(f"   Successful measurements: {len(latencies)}/{num_tests}")
            
            return avg_latency
        else:
            print("❌ Latency measurement failed")
            return 0
            
    except Exception as e:
        print(f"❌ Latency test error: {e}")
        return 0


def quick_throughput_test(host='127.0.0.1', port=8000, duration=5):
    """Enhanced throughput test with different message types"""
    print(f"🔄 Running enhanced throughput test for {duration} seconds...")
    
    try:
        # Connect to server with unique username
        username = f'throughput_test_{int(time.time() * 1000)}'
        sock = connect_to_server(host, port, username)
        if not sock:
            return 0
        
        messages_sent = 0
        successful_responses = 0
        bytes_sent = 0
        start_time = time.perf_counter()
        
        # Different message types and sizes
        message_types = [MessageType.CHAT, MessageType.CHAT, MessageType.CHAT]  # Mostly CHAT
        message_sizes = [128, 256, 512, 1024, 2048]
        
        while time.perf_counter() - start_time < duration:
            # Use different message types and sizes
            msg_type = message_types[messages_sent % len(message_types)]
            msg_size = message_sizes[messages_sent % len(message_sizes)]
            
            # Create message content
            if msg_type == MessageType.CHAT:
                content = f'Throughput test message {messages_sent} with size {msg_size} bytes. ' + 'X' * (msg_size - 80)
            else:
                content = f'System message {messages_sent}'
            
            msg = Message(
                msg_type=msg_type,
                sender=username,
                content=content,
                timestamp=time.perf_counter(),
                is_udp=False,
                seq_num=messages_sent,
                ack_num=0,
                msg_id=f'throughput_{messages_sent}_{msg_size}'
            )
            
            msg_json = msg.to_json().encode('utf-8')
            bytes_sent += len(msg_json)
            
            # Send message
            sock.send(len(msg_json).to_bytes(4, 'big'))
            sock.send(msg_json)
            
            # Wait for server response (ACK)
            try:
                sock.settimeout(0.3)  # 300ms timeout - shorter
                length_bytes = sock.recv(4)
                if len(length_bytes) == 4:
                    response_length = int.from_bytes(length_bytes, 'big')
                    response_data = sock.recv(response_length)
                    
                    if response_data:
                        response_msg = Message.from_json(response_data.decode('utf-8'))
                        if response_msg.msg_type == MessageType.ACK:
                            successful_responses += 1
            except socket.timeout:
                pass  # Silently handle timeouts
            except Exception as e:
                pass  # Silently handle errors
            
            messages_sent += 1
            
            # Very short wait (for higher throughput)
            time.sleep(0.01)  # 10ms wait
        
        sock.close()
        
        actual_duration = time.perf_counter() - start_time
        throughput = messages_sent / actual_duration
        response_rate = (successful_responses / messages_sent * 100) if messages_sent > 0 else 0
        bytes_per_sec = bytes_sent / actual_duration
        
        print(f"✅ Enhanced Throughput Results:")
        print(f"   Messages sent: {messages_sent}")
        print(f"   Successful responses: {successful_responses}")
        print(f"   Response rate: {response_rate:.1f}%")
        print(f"   Duration: {actual_duration:.3f} seconds")
        print(f"   Throughput: {throughput:.2f} messages/second")
        print(f"   Data rate: {bytes_per_sec:.2f} bytes/second ({bytes_per_sec/1024:.2f} KB/s)")
        
        return throughput
        
    except Exception as e:
        print(f"❌ Throughput test error: {e}")
        return 0


def main():
    """Main function"""
    print("🚀 Enhanced Performance Test Starting")
    print("=" * 50)
    
    # Server check
    print("⚠️  Make sure the server is running!")
    print("   python -m network_chat.server.server")
    print("   Server ports: TCP=8000, UDP=8001")
    input("Press Enter to continue...")
    
    # Test 1: Latency
    print("\n1️⃣  Latency Test")
    print("-" * 20)
    latency = quick_latency_test()
    
    # Test 2: Throughput
    print("\n2️⃣  Throughput Test")
    print("-" * 20)
    throughput = quick_throughput_test()
    
    # Summary
    print("\n📊 ENHANCED TEST SUMMARY")
    print("=" * 50)
    print(f"Latency: {latency:.3f} ms")
    print(f"Throughput: {throughput:.2f} msg/sec")
    
    # Evaluation
    print("\n📈 PERFORMANCE EVALUATION")
    print("-" * 20)
    
    if latency > 0:
        if latency < 10:
            print("✅ Latency: Excellent (< 10ms)")
        elif latency < 50:
            print("✅ Latency: Good (10-50ms)")
        elif latency < 100:
            print("⚠️  Latency: Acceptable (50-100ms)")
        else:
            print("📊 Latency: Measured (> 100ms)")
    
    if throughput > 0:
        if throughput > 1000:
            print("✅ Throughput: Excellent (> 1000 msg/sec)")
        elif throughput > 500:
            print("✅ Throughput: Good (500-1000 msg/sec)")
        elif throughput > 100:
            print("⚠️  Throughput: Acceptable (100-500 msg/sec)")
        else:
            print("📊 Throughput: Measured (< 100 msg/sec)")
    
    print("\n✅ Enhanced test completed!")


if __name__ == "__main__":
    main() 