import socket
import random
import time
import sys

# Parameters
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 65432  # Server port
CHUNK_SIZE = 64 * 1024  # 64 KB chunk size
TOTAL_SIZE = 1024 * 1024 * 1024  # 1 GB total data to handle
SEED = 12345  # Known seed for random data generation
TARGET_SPEED_MBPS = 700  # Target speed in Mbps

# Convert target speed from Mbps to Bps (bytes per second)
TARGET_SPEED_BPS = (TARGET_SPEED_MBPS * 1_000_000) / 8  # Convert to bytes per second

# Calculate minimum time to send one chunk of data at the target speed
MIN_TIME_PER_CHUNK = CHUNK_SIZE / TARGET_SPEED_BPS  # in seconds


def generate_chunk(random_gen, size):
    """Generates random bytes of given size."""
    return random_gen.randbytes(size)


def start_server():
    random_gen = random.Random(SEED)  # Initialize random generator with a known seed

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, CHUNK_SIZE)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, CHUNK_SIZE)

        s.bind((HOST, PORT))  # Bind the server to all interfaces on the given port
        s.listen()  # Start listening for incoming connections
        print(f"Server listening on {HOST}:{PORT}...")

        while True:
            try:
                conn, addr = s.accept()  # Accept a client connection
                conn.settimeout(1)  # Минимальный полезный таймаут для обработки клиента
                print(f"Connected client: {addr}")

                with conn:
                    # Check first 4 bytes for PING
                    initial_data = conn.recv(4)

                    if initial_data == b'PING':
                        conn.sendall(b'GIGAPONG')
                        print(f"Handled PING from {addr}.")
                        continue  # Go back to listening for new connections

                    # Proceed with normal data transfer if not PING
                    received_size = 4  # Account for already received first 4 bytes

                    print(f"Receiving {TOTAL_SIZE / (1024 * 1024):.2f} MB of data from the client...")

                    # Measure receiving time
                    start_time_receive = time.time()

                    while received_size < TOTAL_SIZE:
                        try:
                            data = conn.recv(CHUNK_SIZE)  # Receive chunk
                            if not data:
                                break
                            received_size += len(data)  # Update received size

                            # Progress output
                            progress_percentage = (received_size / TOTAL_SIZE) * 100
                            sys.stdout.write(f"\rReceived {received_size / (1024 * 1024):.2f} MB of {TOTAL_SIZE / (1024 * 1024):.2f} MB "
                                             f"({progress_percentage:.2f}%)")
                            sys.stdout.flush()

                        except socket.timeout:
                            print("\nConnection timed out while receiving data.")
                            conn.close()
                            break
                        except ConnectionResetError:
                            print("\nConnection reset by client.")
                            conn.close()
                            break

                    end_time_receive = time.time()  # End the timer for receiving
                    receive_time = end_time_receive - start_time_receive

                    if received_size < TOTAL_SIZE:
                        continue  # Go back to listening for new connections if data incomplete

                    print("\nAll data received successfully, sending it back...")

                    # Send data back to the client
                    random_gen = random.Random(SEED)  # Reinitialize generator for sending back
                    sent_size = 0

                    start_time_send = time.time()

                    while sent_size < TOTAL_SIZE:
                        try:
                            chunk = generate_chunk(random_gen, CHUNK_SIZE)  # Generate chunk

                            # Start the timer before sending
                            start_time_chunk = time.time()

                            conn.sendall(chunk)  # Send chunk to client
                            sent_size += len(chunk)  # Update sent size

                            # Calculate how much time has passed since the chunk was sent
                            elapsed_time = time.time() - start_time_chunk

                            # Add delay if the chunk was sent too quickly
                            if elapsed_time < MIN_TIME_PER_CHUNK:
                                time.sleep(MIN_TIME_PER_CHUNK - elapsed_time)  # Add delay to throttle speed

                            # Progress output
                            progress_percentage = (sent_size / TOTAL_SIZE) * 100
                            sys.stdout.write(f"\rSent {sent_size / (1024 * 1024):.2f} MB of {TOTAL_SIZE / (1024 * 1024):.2f} MB "
                                             f"({progress_percentage:.2f}%)")
                            sys.stdout.flush()

                        except socket.timeout:
                            print("\nConnection timed out during sending.")
                            conn.close()
                            break
                        except ConnectionResetError:
                            print("\nConnection reset by client during sending.")
                            conn.close()
                            break

                    end_time_send = time.time()  # End the timer for sending
                    send_time = end_time_send - start_time_send

                    if sent_size < TOTAL_SIZE:
                        continue  # Go back to listening for new connections if data incomplete

                    print("\nAll data sent back to client successfully.")

                    # Calculate data transmission speed in Mbps
                    total_bits = TOTAL_SIZE * 8  # Convert data size to bits
                    send_speed_mbps = total_bits / (send_time * 1_000_000)  # Sending speed in Mbps
                    receive_speed_mbps = total_bits / (receive_time * 1_000_000)  # Receiving speed in Mbps
                    total_time = send_time + receive_time  # Total round-trip time
                    total_speed_mbps = total_bits / (total_time * 1_000_000)  # Total speed in Mbps

                    # Output the final results
                    print(f"\nGigaPONG completed successfully. Send time: {send_time:.2f} seconds, "
                          f"Receive time: {receive_time:.2f} seconds, "
                          f"Total round-trip time: {total_time:.2f} seconds, "
                          f"Send speed: {send_speed_mbps:.2f} Mbps, "
                          f"Receive speed: {receive_speed_mbps:.2f} Mbps, "
                          f"Total speed: {total_speed_mbps:.2f} Mbps.")

            except socket.timeout:
                continue  # Continue to listen for new connections if no client connects in time


if __name__ == "__main__":
    start_server()
