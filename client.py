import socket
import random
import time

# Parameters
HOST = '127.0.0.1'  # Server IP address
PORT = 65432  # Server port
CHUNK_SIZE = 64 * 1024  # Chunk size: 64 KB
TOTAL_SIZE = 1024 * 1024 * 1024  # 1 GB total data size
SEED = 12345  # Known seed for generating random data
PING_MESSAGE = b'PING'  # PING message to initiate communication


def generate_chunk(random_gen, size):
    """Generate a chunk of random bytes of the specified size."""
    return random_gen.randbytes(size)


def start_client():
    random_gen = random.Random(SEED)  # Initialize the random generator with the known seed

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # Connect to the server
        print(f"Connected to server at {HOST}:{PORT}")

        # Send the initial PING message
        s.sendall(PING_MESSAGE)

        # Wait for server's response
        response = s.recv(8)
        if response == b'GIGAPONG':
            print("Received GIGAPONG response, closing connection.")
            return

        # Measure the time to send data to the server
        start_time_send = time.time()

        sent_size = 4  # Count the already sent 4 bytes (PING)
        while sent_size < TOTAL_SIZE:
            chunk = generate_chunk(random_gen, CHUNK_SIZE)  # Generate random chunk
            s.sendall(chunk)  # Send the chunk to the server
            sent_size += len(chunk)  # Track total bytes sent
            print(f"Sent {sent_size / (1024 * 1024):.2f} MB")

        end_time_send = time.time()  # End the timer for sending
        send_time = end_time_send - start_time_send  # Calculate the sending time

        print("All data sent successfully.")

        # Measure the time to receive data back from the server
        start_time_receive = time.time()

        received_size = 0
        random_gen = random.Random(SEED)  # Reinitialize the generator for verification

        while received_size < TOTAL_SIZE:
            data = s.recv(CHUNK_SIZE)  # Receive data chunk from server
            if not data:
                break

            expected_chunk = generate_chunk(random_gen,
                                            len(data))  # Generate expected chunk for comparison

            if data != expected_chunk:
                print("Error: received chunk does not match expected data.")
                s.close()
                return

            received_size += len(data)  # Track total bytes received
            print(f"Received {received_size / (1024 * 1024):.2f} MB")

        end_time_receive = time.time()  # End the timer for receiving
        receive_time = end_time_receive - start_time_receive  # Calculate the receiving time

        # Total round-trip time
        total_time = send_time + receive_time

        # Calculate data transmission speed in Mbps
        total_bits = TOTAL_SIZE * 8  # Convert data size to bits
        send_speed_mbps = total_bits / (send_time * 1_000_000)  # Sending speed in Mbps
        receive_speed_mbps = total_bits / (receive_time * 1_000_000)  # Receiving speed in Mbps

        # Output the results
        print(f"Send time: {send_time:.2f} seconds, speed: {send_speed_mbps:.2f} Mbps")
        print(f"Receive time: {receive_time:.2f} seconds, speed: {receive_speed_mbps:.2f} Mbps")
        print(
            f"Total round-trip time: {total_time:.2f} seconds, total speed: {total_speed_mbps:.2f} Mbps")


if __name__ == "__main__":
    start_client()