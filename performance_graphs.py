#!/usr/bin/env python3


import time
import socket
import json
import statistics
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# network_chat modülünü path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), 'network_chat'))

from network_chat.common.message import Message, MessageType

# Matplotlib varsayılan fontlarını kullanalım
# plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
# plt.rcParams['axes.unicode_minus'] = False


def connect_to_server(host='127.0.0.1', port=8000, username='perf_test'):
    """Sunucuya bağlan ve CONNECT mesajı gönder"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # CONNECT mesajı gönder
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
        
        # CONNECT_ACK yanıtını bekle
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


def detailed_latency_test(host='127.0.0.1', port=8000, num_tests=50):
    """Detaylı latency testi - tüm ölçümleri döndürür"""
    print(f"🔄 Running detailed latency test with {num_tests} messages...")
    
    try:
        username = f'latency_test_{int(time.time() * 1000)}'
        sock = connect_to_server(host, port, username)
        if not sock:
            return [], []
        
        latencies = []
        message_numbers = []
        
        for i in range(num_tests):
            msg = Message(
                msg_type=MessageType.CHAT,
                sender=username,
                content=f'Test {i}',
                timestamp=time.time(),
                is_udp=False,
                seq_num=i,
                ack_num=0,
                msg_id=f'test_{i}'
            )
            
            msg_json = msg.to_json().encode('utf-8')
            
            start_time = time.time()
            
            sock.send(len(msg_json).to_bytes(4, 'big'))
            sock.send(msg_json)
            
            try:
                sock.settimeout(2.0)
                length_bytes = sock.recv(4)
                if len(length_bytes) == 4:
                    response_length = int.from_bytes(length_bytes, 'big')
                    sock.recv(response_length)
                    
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
                    message_numbers.append(i + 1)
                else:
                    print(f"⚠️  Invalid response for message {i}")
            except socket.timeout:
                print(f"⚠️  Response timeout for message {i}")
            except Exception as e:
                print(f"⚠️  Response error for message {i}: {e}")
            
            time.sleep(0.1)
        
        sock.close()
        
        if latencies:
            print(f"✅ Latency test completed: {len(latencies)} successful measurements")
            return latencies, message_numbers
        else:
            print("❌ Latency measurement failed")
            return [], []
            
    except Exception as e:
        print(f"❌ Latency test error: {e}")
        return [], []


def detailed_throughput_test(host='127.0.0.1', port=8000, duration=10):
    """Detaylı throughput testi - zaman serisi verisi döndürür"""
    print(f"🔄 Running detailed throughput test for {duration} seconds...")
    
    try:
        username = f'throughput_test_{int(time.time() * 1000)}'
        sock = connect_to_server(host, port, username)
        if not sock:
            return [], []
        
        throughput_data = []
        time_points = []
        messages_sent = 0
        start_time = time.time()
        last_measurement_time = start_time
        
        while time.time() - start_time < duration:
            msg = Message(
                msg_type=MessageType.CHAT,
                sender=username,
                content=f'Throughput {messages_sent}',
                timestamp=time.time(),
                is_udp=False,
                seq_num=messages_sent,
                ack_num=0,
                msg_id=f'throughput_{messages_sent}'
            )
            
            msg_json = msg.to_json().encode('utf-8')
            sock.send(len(msg_json).to_bytes(4, 'big'))
            sock.send(msg_json)
            
            try:
                sock.settimeout(0.5)
                length_bytes = sock.recv(4)
                if len(length_bytes) == 4:
                    response_length = int.from_bytes(length_bytes, 'big')
                    sock.recv(response_length)
            except socket.timeout:
                pass
            except Exception as e:
                pass
            
            messages_sent += 1
            
            # Her 0.5 saniyede bir ölçüm al
            current_time = time.time()
            if current_time - last_measurement_time >= 0.5:
                elapsed = current_time - start_time
                throughput = messages_sent / elapsed
                throughput_data.append(throughput)
                time_points.append(elapsed)
                last_measurement_time = current_time
            
            time.sleep(0.05)
        
        sock.close()
        
        if throughput_data:
            print(f"✅ Throughput test completed: {len(throughput_data)} measurements")
            return throughput_data, time_points
        else:
            print("❌ Throughput measurement failed")
            return [], []
        
    except Exception as e:
        print(f"❌ Throughput test error: {e}")
        return [], []


def create_latency_graph(latencies, message_numbers, save_path='latency_graph.png'):
    """Create and display a graph for latency results."""
    if not latencies:
        print("❌ No latency data to plot")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), constrained_layout=True)
    fig.suptitle('System Latency Analysis', fontsize=18, fontweight='bold')

    # Main latency plot
    ax1.plot(message_numbers, latencies, 'b-o', linewidth=2, markersize=4, alpha=0.7)
    ax1.set_title('Round-Trip Time (RTT) for Each Message', fontsize=14)
    ax1.set_xlabel('Message Number')
    ax1.set_ylabel('Latency (ms)')
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Statistics
    avg_latency = statistics.mean(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
    
    # Add statistics box to the plot
    stats_text = (f'Average: {avg_latency:.2f} ms\n'
                  f'Min: {min_latency:.2f} ms\n'
                  f'Max: {max_latency:.2f} ms\n'
                  f'Std Dev: {std_latency:.2f} ms')
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Histogram of latencies
    bins = min(20, len(latencies) // 2 if len(latencies) > 4 else 5)
    ax2.hist(latencies, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
    ax2.axvline(avg_latency, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_latency:.2f} ms')
    ax2.set_title('Latency Distribution (Histogram)', fontsize=14)
    ax2.set_xlabel('Latency (ms)')
    ax2.set_ylabel('Frequency')
    ax2.legend()
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    fig.text(0.5, -0.02, 'Top: Latency for each message. Bottom: Frequency distribution of latency values.', 
             ha='center', fontsize=10, style='italic')

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Latency graph saved as: {save_path}")
    plt.show()


def create_throughput_graph(throughput_data, time_points, save_path='throughput_graph.png'):
    """Create and display a graph for throughput results."""
    if not throughput_data:
        print("❌ No throughput data to plot")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), constrained_layout=True)
    fig.suptitle('System Throughput Analysis', fontsize=18, fontweight='bold')
    
    # Main throughput plot
    ax1.plot(time_points, throughput_data, 'g-o', linewidth=2, markersize=4, alpha=0.7)
    ax1.set_title('Throughput Over Time', fontsize=14)
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Throughput (messages/second)')
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Statistics
    avg_throughput = statistics.mean(throughput_data)
    min_throughput = min(throughput_data)
    max_throughput = max(throughput_data)
    std_throughput = statistics.stdev(throughput_data) if len(throughput_data) > 1 else 0
    
    # Add statistics box to the plot
    stats_text = (f'Average: {avg_throughput:.2f} msg/s\n'
                  f'Min: {min_throughput:.2f} msg/s\n'
                  f'Max: {max_throughput:.2f} msg/s\n'
                  f'Std Dev: {std_throughput:.2f} msg/s')
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    # Moving average
    if len(throughput_data) > 3:
        # Dynamically adjust window size
        window_size = max(3, min(5, len(throughput_data) // 4))
        moving_avg = []
        # Calculate moving average more robustly
        for i in range(len(throughput_data)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(throughput_data), i + window_size // 2 + 1)
            moving_avg.append(statistics.mean(throughput_data[start_idx:end_idx]))
        
        ax1.plot(time_points, moving_avg, 'r-', linewidth=3, alpha=0.8, label=f'Moving Average (n={window_size})')
        ax1.legend()
    
    # Histogram of throughput data
    bins = min(15, len(throughput_data) // 2 if len(throughput_data) > 4 else 5)
    ax2.hist(throughput_data, bins=bins, alpha=0.7, color='lightgreen', edgecolor='black')
    ax2.axvline(avg_throughput, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_throughput:.2f} msg/s')
    ax2.set_title('Throughput Distribution (Histogram)', fontsize=14)
    ax2.set_xlabel('Throughput (messages/second)')
    ax2.set_ylabel('Frequency')
    ax2.legend()
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

    fig.text(0.5, -0.02, 'Top: Throughput over time. Bottom: Frequency distribution of throughput values.', 
             ha='center', fontsize=10, style='italic')

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Throughput graph saved as: {save_path}")
    plt.show()


def create_combined_graph(latencies, throughput_data, save_path='combined_performance.png'):
    """Create a combined graph for latency and throughput."""
    if not latencies or not throughput_data:
        print("❌ Insufficient data for combined graph")
        return
    
    # Ensure data lists are of the same length for correlation
    min_len = min(len(latencies), len(throughput_data))
    latencies = latencies[:min_len]
    throughput_data = throughput_data[:min_len]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), constrained_layout=True)
    fig.suptitle('Combined Performance Analysis', fontsize=18, fontweight='bold')
    
    # Latency and Throughput on the same plot
    ax1.set_title('Latency and Throughput Over Time', fontsize=16)
    message_numbers = list(range(1, len(latencies) + 1))
    
    # Latency plot (left y-axis)
    p1, = ax1.plot(message_numbers, latencies, 'b-o', linewidth=2, markersize=4, alpha=0.7, label='Latency (ms)')
    ax1.set_xlabel('Measurement Point')
    ax1.set_ylabel('Latency (ms)', color=p1.get_color())
    ax1.tick_params(axis='y', labelcolor=p1.get_color())
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Throughput plot (right y-axis)
    ax1_twin = ax1.twinx()
    p2, = ax1_twin.plot(message_numbers, throughput_data, 'g-s', linewidth=2, markersize=4, alpha=0.7, label='Throughput (msg/s)')
    ax1_twin.set_ylabel('Throughput (msg/s)', color=p2.get_color())
    ax1_twin.tick_params(axis='y', labelcolor=p2.get_color())
    
    # Combined legend
    ax1.legend(handles=[p1, p2], loc='upper right')
    
    # Statistics
    avg_latency = statistics.mean(latencies)
    avg_throughput = statistics.mean(throughput_data)
    
    stats_text = f'Avg Latency: {avg_latency:.2f} ms\nAvg Throughput: {avg_throughput:.2f} msg/s'
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Scatter plot for correlation
    ax2.scatter(throughput_data, latencies, alpha=0.6, s=50, c='purple', edgecolors='black')
    ax2.set_xlabel('Throughput (msg/s)')
    ax2.set_ylabel('Latency (ms)')
    ax2.set_title('Latency vs. Throughput Correlation', fontsize=14)
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Trend line
    if len(throughput_data) > 1:
        try:
            z = np.polyfit(throughput_data, latencies, 1)
            p = np.poly1d(z)
            ax2.plot(throughput_data, p(throughput_data), "r--", alpha=0.8, linewidth=2, label='Trend Line')
            ax2.legend()
        except np.linalg.LinAlgError:
            print("⚠️ Could not compute trend line for correlation plot.")

    fig.text(0.5, -0.02, 'Top: Latency and Throughput over measurement points. Bottom: Correlation between them.', 
             ha='center', fontsize=10, style='italic')

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Combined graph saved as: {save_path}")
    plt.show()


def main():
    """Main function to run tests and generate graphs."""
    print("🚀 Performance Graphs Generator Starting")
    print("=" * 60)
    
    # Create a directory for graphs if it doesn't exist
    output_dir = "performance_graphs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created directory: {output_dir}")

    # Server check
    print("⚠️  Make sure the server is running!")
    print("   python -m network_chat.server.server")
    print("   Server ports: TCP=8000, UDP=8001")
    input("Press Enter to continue...")
    
    # Test parameters
    latency_tests = 50
    throughput_duration = 10
    
    print(f"\n📊 Test Parameters:")
    print(f"   Latency tests: {latency_tests} messages")
    print(f"   Throughput duration: {throughput_duration} seconds")
    
    # Test 1: Detailed Latency
    print(f"\n1️⃣  Running Detailed Latency Test...")
    print("-" * 50)
    latencies, message_numbers = detailed_latency_test(num_tests=latency_tests)
    
    # Test 2: Detailed Throughput
    print(f"\n2️⃣  Running Detailed Throughput Test...")
    print("-" * 50)
    throughput_data, time_points = detailed_throughput_test(duration=throughput_duration)
    
    # Generate graphs
    print(f"\n📈 Generating Graphs...")
    print("-" * 30)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if latencies:
        save_path = os.path.join(output_dir, f'latency_graph_{timestamp}.png')
        create_latency_graph(latencies, message_numbers, save_path)
    
    if throughput_data:
        save_path = os.path.join(output_dir, f'throughput_graph_{timestamp}.png')
        create_throughput_graph(throughput_data, time_points, save_path)
    
    if latencies and throughput_data:
        save_path = os.path.join(output_dir, f'combined_performance_{timestamp}.png')
        create_combined_graph(latencies, throughput_data, save_path)
    
    # Summary Report
    print(f"\n📋 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    if latencies:
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
        
        print(f"Latency Results:")
        print(f"  Average: {avg_latency:.2f} ms")
        print(f"  Min-Max: {min_latency:.2f} - {max_latency:.2f} ms")
        print(f"  Std Dev: {std_latency:.2f} ms")
        print(f"  Samples: {len(latencies)}")
    
    if throughput_data:
        avg_throughput = statistics.mean(throughput_data)
        min_throughput = min(throughput_data)
        max_throughput = max(throughput_data)
        std_throughput = statistics.stdev(throughput_data) if len(throughput_data) > 1 else 0
        
        print(f"\nThroughput Results:")
        print(f"  Average: {avg_throughput:.2f} msg/s")
        print(f"  Min-Max: {min_throughput:.2f} - {max_throughput:.2f} msg/s")
        print(f"  Std Dev: {std_throughput:.2f} msg/s")
        print(f"  Samples: {len(throughput_data)}")
    
    print(f"\n✅ Performance graphs generated successfully!")
    print(f"📁 Check the generated PNG files in the '{output_dir}' directory.")


if __name__ == "__main__":
    main() 