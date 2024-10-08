import socket
import random

# Parameters
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 65432  # Server port
CHUNK_SIZE = 64 * 1024  # 64 KB chunk size
TOTAL_SIZE = 1024 * 1024 * 1024  # 1 GB total data to handle
SEED = 12345  # Known seed for random data generation
PING_RESPONSE = b'GIGAPONG'  # Response to PING


def generate_chunk(random_gen, size):
    """Generates random bytes of given size."""
    return random_gen.randbytes(size)


def start_server():
    random_gen = random.Random(SEED)  # Initialize random generator with a known seed

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))  # * Bind the server to all interfaces on the given port
        s.listen()  # Start listening for incoming connections
        print(f"Server listening on {HOST}:{PORT}...")

        while True:
            conn, addr = s.accept()  # Accept a client connection
            with conn:
                print(f"Connected client: {addr}")

                # Check first 4 bytes for PING
                initial_data = conn.recv(4)

                if initial_data == b'PING':
                    print("Received PING, sending GIGAPONG")
                    conn.sendall(PING_RESPONSE)
                    continue  # Go back to listening for new connections

                # Proceed with normal data transfer if not PING
                received_size = 4  # Account for already received first 4 bytes

                # * Verify initial chunk matches the generated random data
                expected_chunk = generate_chunk(random_gen, len(initial_data))
                if initial_data != expected_chunk:
                    print("Error: initial data mismatch.")
                    conn.close()
                    return

                # Receive the remaining chunks of data
                while received_size < TOTAL_SIZE:
                    data = conn.recv(CHUNK_SIZE)  # Receive chunk
                    if not data:
                        break

                    expected_chunk = generate_chunk(random_gen,
                                                    len(data))  # Generate expected chunk

                    if data != expected_chunk:
                        print("Error: received chunk mismatch.")
                        conn.close()
                        return

                    received_size += len(data)  # Update received size
                    print(f"Received {received_size / (1024 * 1024):.2f} MB")

                print("All data received and verified successfully.")

                # Send data back to the client
                random_gen = random.Random(SEED)  # Reinitialize generator for sending back
                sent_size = 0

                while sent_size < TOTAL_SIZE:
                    chunk = generate_chunk(random_gen, CHUNK_SIZE)  # Generate chunk
                    conn.sendall(chunk)  # Send chunk to client
                    sent_size += len(chunk)  # Update sent size
                    print(f"Sent back {sent_size / (1024 * 1024):.2f} MB")

                print("All data sent back to client successfully.")


if __name__ == "__main__":
    start_server()
