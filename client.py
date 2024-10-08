import socket
import random
import time
import sys

# Parameters
HOST = '127.0.0.1'  # Server IP address
PORT = 65432  # Server port
CHUNK_SIZE = 64 * 1024  # 64 KB chunk size
TOTAL_SIZE = 1024 * 1024 * 1024  # 1 GB total data size
SEED = 12345  # Known seed for random data generation
TARGET_SPEED_MBPS = 700  # Target speed in Mbps

# Convert target speed from Mbps to Bps (bytes per second)
TARGET_SPEED_BPS = (TARGET_SPEED_MBPS * 1_000_000) / 8  # Convert to bytes per second

# Calculate minimum time to send one chunk of data at the target speed
MIN_TIME_PER_CHUNK = CHUNK_SIZE / TARGET_SPEED_BPS  # in seconds


def generate_chunk(random_gen, size):
    """Generate a chunk of random bytes of the specified size."""
    return random_gen.randbytes(size)


def start_client():
    random_gen = random.Random(SEED)  # Initialize the random generator with the known seed

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)  # Малый тайм-аут на чтение и запись для высоких нагрузок
        s.connect((HOST, PORT))  # Connect to the server
        print(f"Connected to server at {HOST}:{PORT}")

        # Measure the time to send data to the server
        sent_size = 0
        total_chunks = TOTAL_SIZE // CHUNK_SIZE
        chunk_count = 0

        print(f"Sending {TOTAL_SIZE / (1024 * 1024):.2f} MB of data to the server...")

        start_time_send = time.time()
        while sent_size < TOTAL_SIZE:
            chunk = generate_chunk(random_gen, CHUNK_SIZE)  # Generate random chunk

            # Start the timer before sending
            start_time_chunk = time.time()

            s.sendall(chunk)  # Send the chunk to the server
            sent_size += len(chunk)  # Track total bytes sent
            chunk_count += 1

            # Calculate how much time has passed since the chunk was sent
            elapsed_time = time.time() - start_time_chunk

            # Calculate if we need to wait to limit the speed
            if elapsed_time < MIN_TIME_PER_CHUNK:
                time.sleep(MIN_TIME_PER_CHUNK - elapsed_time)  # Add delay to throttle speed

            # Update progress
            progress_percentage = (sent_size / TOTAL_SIZE) * 100
            sys.stdout.write(f"\rSent {sent_size / (1024 * 1024):.2f} MB of {TOTAL_SIZE / (1024 * 1024):.2f} MB "
                             f"({progress_percentage:.2f}%)")
            sys.stdout.flush()

        end_time_send = time.time()  # End the timer for sending
        send_time = end_time_send - start_time_send  # Calculate the sending time

        print("\nAll data sent successfully.")

        # Now receive data back from the server
        received_size = 0
        print(f"Receiving {TOTAL_SIZE / (1024 * 1024):.2f} MB of data back from the server...")

        start_time_receive = time.time()
        while received_size < TOTAL_SIZE:
            data = s.recv(CHUNK_SIZE)  # Receive chunk from server
            if not data:
                break
            received_size += len(data)

            # Update progress
            progress_percentage = (received_size / TOTAL_SIZE) * 100
            sys.stdout.write(f"\rReceived {received_size / (1024 * 1024):.2f} MB of {TOTAL_SIZE / (1024 * 1024):.2f} MB "
                             f"({progress_percentage:.2f}%)")
            sys.stdout.flush()

        end_time_receive = time.time()  # End the timer for receiving
        receive_time = end_time_receive - start_time_receive  # Calculate the receiving time

        print("\nAll data received back from the server successfully.")

        # Calculate data transmission speed in Mbps
        total_bits = TOTAL_SIZE * 8  # Convert data size to bits
        send_speed_mbps = total_bits / (send_time * 1_000_000)  # Sending speed in Mbps
        receive_speed_mbps = total_bits / (receive_time * 1_000_000)  # Receiving speed in Mbps
        total_time = send_time + receive_time  # Total round-trip time
        total_speed_mbps = total_bits / (total_time * 1_000_000)  # Total speed in Mbps

        # Output the final results as a table
        print("\n" + "-" * 40)
        print("  GigaPONG Transmission Results")
        print("-" * 40)
        print(f"Send speed:       {send_speed_mbps:.2f} Mbps")
        print(f"Receive speed:    {receive_speed_mbps:.2f} Mbps")
        print(f"Round-trip time:  {total_time:.2f} seconds")
        print(f"Send time:        {send_time:.2f} seconds")
        print(f"Receive time:     {receive_time:.2f} seconds")
        print(
            f"Average time/GB:  {(total_time / (TOTAL_SIZE / (1024 * 1024 * 1024))):.2f} seconds per GB")
        print(f"Total connection: {total_time:.2f} seconds")
        print("-" * 40)


if __name__ == "__main__":
    start_client()
