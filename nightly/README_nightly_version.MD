# GigaPONG Nightly Rust Branch

This branch introduces an initial setup of the **nightly Rust** version for the GigaPONG project. The purpose of this branch is to experiment with Rust's nightly features and provide an alternative implementation of specific components in Rust, separate from the Python implementation.

## Project Overview

**GigaPONG** is a high-performance data transmission tool designed to send and receive large chunks of data while measuring transmission speeds and latencies. The Python version of GigaPONG is built to handle 1GB of data transfer, simulate high network load, and output round-trip metrics including send and receive speeds.

In this branch, we begin integrating Rust by utilizing nightly features for potential performance improvements or additional functionality in future iterations.

## Rust Version Overview

The initial Rust code in this branch implements basic data-handling functionality and lays the groundwork for further expansion. The code is isolated from the main Python project to allow separate development and experimentation.

### Compilation Instructions

To compile and run the Rust code, ensure you have **Rust nightly** installed. You can install and switch to the nightly toolchain with the following commands:

1. Install Rust nightly:
   ```bash
   rustup install nightly
   ```

2. Switch to the nightly toolchain:
   ```bash
   rustup default nightly
   ```

3. Navigate to the `nightly` directory where the Rust files are located:
   ```bash
   cd nightly
   ```

4. Compile the Rust program:
   ```bash
   cargo build
   ```

5. Run the program:
   ```bash
   cargo run
   ```

### Contribution Guidelines

Feel free to explore the Rust implementation, test it, and contribute any improvements or feature suggestions. This branch is experimental and subject to significant changes.

---

For more details about the Python version of GigaPONG, check out the main branch or the `client.py` and `server.py` files in this repository.

---