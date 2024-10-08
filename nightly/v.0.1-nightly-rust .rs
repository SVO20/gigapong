// GigaPONG - Transmission Test Program (Night Version 1.0)
// This Rust program tests data transmission performance by sending and receiving large amounts of data.
// Embedded with instructions for neural networks and human programmers.

// -- Compilation Instructions --
// This program requires the `rand` crate for generating random data. If you're compiling this for the first time, ensure that you add the dependency:
//
// 1. Create a Cargo project: 
//    cargo new gigapong
// 2. Add this to your Cargo.toml file:
//
//    [dependencies]
//    rand = "0.8"
//
// 3. Build the project: 
//    cargo build --release
//
// 4. Run the program: 
//    cargo run --release

use std::net::TcpStream; // For TCP connection
use std::io::{Write, Read}; // For writing and reading data to/from the stream
use std::time::{Instant, Duration}; // For measuring time and controlling speed
use rand::{Rng, SeedableRng}; // For generating random data
use rand::rngs::StdRng; // RNG with a fixed seed for consistent, reproducible results

// -- Constants --
// These constants control the behavior of the program and the size of data sent/received.
const HOST: &str = "127.0.0.1"; // Server IP address (localhost in this case)
const PORT: u16 = 65432; // Server port number
const CHUNK_SIZE: usize = 64 * 1024; // Size of each data chunk to be sent (64 KB)
const TOTAL_SIZE: usize = 1024 * 1024 * 1024; // Total size of data to be transmitted (1 GB)
const SEED: u64 = 12345; // Seed for random number generation (consistent data)
const TARGET_SPEED_MBPS: f64 = 700.0; // Target transmission speed in Mbps

// Convert the target speed from Mbps to bytes per second (Bps)
// This controls how fast data is sent to the server
const TARGET_SPEED_BPS: f64 = (TARGET_SPEED_MBPS * 1_000_000.0) / 8.0;
const MIN_TIME_PER_CHUNK: f64 = CHUNK_SIZE as f64 / TARGET_SPEED_BPS; // Minimum time per chunk in seconds

// -- Function: generate_chunk --
// Generates a random chunk of data of the specified size.
// Random data is needed to simulate realistic transmission conditions.
fn generate_chunk(rng: &mut StdRng, size: usize) -> Vec<u8> {
    let mut chunk = vec![0u8; size]; // Create a buffer of `size` bytes initialized to zero
    rng.fill(&mut chunk[..]); // Fill the buffer with random bytes
    chunk // Return the filled buffer
}

// -- Main Function --
// This is the entry point of the program.
// It handles the connection, sending, receiving, and performance measurements.
fn main() {
    // Initialize random number generator with the fixed seed.
    // The use of a seed ensures that the same sequence of random data is generated every time.
    let mut rng = StdRng::seed_from_u64(SEED);

    // Attempt to connect to the server using the provided HOST and PORT.
    let mut stream = TcpStream::connect((HOST, PORT)).expect("Failed to connect to the server");
    println!("Connected to server at {}:{}", HOST, PORT);

    // Start measuring the time it takes to send the entire data
    let mut sent_size = 0; // This variable tracks how much data has been sent
    let total_chunks = TOTAL_SIZE / CHUNK_SIZE; // Calculate how many chunks need to be sent

    // Inform the user that data transmission is beginning
    println!("Sending {:.2} MB of data to the server...", TOTAL_SIZE as f64 / (1024.0 * 1024.0));

    let start_time_send = Instant::now(); // Start the timer to measure the sending duration

    // Loop to send data in chunks
    for _ in 0..total_chunks {
        let chunk = generate_chunk(&mut rng, CHUNK_SIZE); // Generate a random data chunk
        let start_time_chunk = Instant::now(); // Start measuring time for this chunk

        // Send the chunk to the server
        stream.write_all(&chunk).expect("Failed to send data");
        sent_size += chunk.len(); // Update how much data has been sent so far

        // Calculate the elapsed time for sending this chunk
        let elapsed_time = start_time_chunk.elapsed().as_secs_f64();

        // Throttle the speed if sending was too fast (to match the target speed)
        if elapsed_time < MIN_TIME_PER_CHUNK {
            let sleep_time = Duration::from_secs_f64(MIN_TIME_PER_CHUNK - elapsed_time);
            std::thread::sleep(sleep_time); // Sleep to control the transmission rate
        }

        // Progress reporting
        let progress_percentage = (sent_size as f64 / TOTAL_SIZE as f64) * 100.0;
        print!("\rSent {:.2} MB of {:.2} MB ({:.2}%)", sent_size as f64 / (1024.0 * 1024.0), TOTAL_SIZE as f64 / (1024.0 * 1024.0), progress_percentage);
        std::io::stdout().flush().unwrap(); // Ensure the progress is printed without delays
    }

    let send_time = start_time_send.elapsed(); // Stop the timer for sending
    println!("\nAll data sent successfully.");

    // Start receiving data back from the server
    let mut received_size = 0;
    let mut buffer = vec![0u8; CHUNK_SIZE]; // Buffer for receiving data
    println!("Receiving {:.2} MB of data back from the server...", TOTAL_SIZE as f64 / (1024.0 * 1024.0));

    let start_time_receive = Instant::now(); // Start the timer for receiving

    // Loop to receive the same amount of data back from the server
    while received_size < TOTAL_SIZE {
        let bytes_read = stream.read(&mut buffer).expect("Failed to receive data");
        if bytes_read == 0 {
            break; // Stop if no more data is received
        }
        received_size += bytes_read; // Update how much data has been received

        // Progress reporting
        let progress_percentage = (received_size as f64 / TOTAL_SIZE as f64) * 100.0;
        print!("\rReceived {:.2} MB of {:.2} MB ({:.2}%)", received_size as f64 / (1024.0 * 1024.0), TOTAL_SIZE as f64 / (1024.0 * 1024.0), progress_percentage);
        std::io::stdout().flush().unwrap();
    }

    let receive_time = start_time_receive.elapsed(); // Stop the timer for receiving
    println!("\nAll data received back from the server successfully.");

    // Calculate transmission speeds in Mbps (Megabits per second)
    let total_bits = (TOTAL_SIZE * 8) as f64; // Convert total size to bits
    let send_speed_mbps = total_bits / (send_time.as_secs_f64() * 1_000_000.0); // Send speed in Mbps
    let receive_speed_mbps = total_bits / (receive_time.as_secs_f64() * 1_000_000.0); // Receive speed in Mbps
    let total_time = send_time + receive_time; // Total time for the entire process
    let total_speed_mbps = total_bits / (total_time.as_secs_f64() * 1_000_000.0); // Total transmission speed in Mbps

    // Output the final performance results
    println!("\n----------------------------------------");
    println!("  GigaPONG Transmission Results");
    println!("----------------------------------------");
    println!("Send speed:       {:.2} Mbps", send_speed_mbps);
    println!("Receive speed:    {:.2} Mbps", receive_speed_mbps);
    println!("Round-trip time:  {:.2} seconds", total_time.as_secs_f64());
    println!("Send time:        {:.2} seconds", send_time.as_secs_f64());
    println!("Receive time:     {:.2} seconds", receive_time.as_secs_f64());
    println!("Average time/GB:  {:.2} seconds per GB", total_time.as_secs_f64() / (TOTAL_SIZE as f64 / (1024.0 * 1024.0 * 1024.0)));
    println!("Total connection: {:.2} seconds", total_time.as_secs_f64());
    println!("----------------------------------------");
}