# Rust Stack Instructions

MANDATORY operational instructions for Claude Code when working with Rust projects.

## Cargo Commands - ENFORCE

**MANDATORY project workflow:**
```bash
cargo check                    # ALWAYS check before build
cargo clippy                   # MANDATORY linting
cargo fmt                      # MANDATORY formatting before commit
cargo test                     # REQUIRED before any commit
cargo build --release         # Production builds only
```

**MANDATORY dependency management:**
```bash
cargo add serde --features derive    # Add with explicit features
cargo audit                          # REQUIRED security check
cargo update                         # Keep dependencies current
```

## Project Structure - ENFORCE

**MANDATORY Rust project layout:**
```
src/
├── main.rs                     # Application entry ONLY
├── lib.rs                      # Library entry ONLY
└── modules/                    # Organized module structure
tests/                          # Integration tests REQUIRED
```

## Error Handling - NO EXCEPTIONS

**MANDATORY Result pattern - NEVER panic in production code:**
```rust
// REQUIRED custom error types
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Parse error: {0}")]
    Parse(#[from] std::num::ParseIntError),
}

// MANDATORY ? operator usage
fn read_number(path: &str) -> Result<i32, AppError> {
    let contents = std::fs::read_to_string(path)?;
    let number = contents.trim().parse::<i32>()?;
    Ok(number)
}
```

**MANDATORY error library usage:**
- **Applications**: Use `anyhow` with `.context()`
- **Libraries**: Use `thiserror` for custom errors
- **NO EXCEPTIONS**: Never use `unwrap()` or `expect()` in production

## Testing - MANDATORY

**REQUIRED test coverage for ALL functions:**
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_happy_path() {
        assert_eq!(add(2, 2), 4);
    }

    #[test] 
    fn test_error_cases() -> Result<(), Box<dyn std::error::Error>> {
        let result = fallible_operation()?;
        assert_eq!(result, expected);
        Ok(())
    }
}
```

**MANDATORY testing commands:**
```bash
cargo test                      # REQUIRED before every commit
cargo test -- --nocapture       # Debug test output
cargo test --release            # Performance-sensitive tests
```

## Async Programming - ENFORCE

**MANDATORY async patterns:**
```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let result = async_operation().await?;
    println!("Result: {:?}", result);
    Ok(())
}

// REQUIRED error propagation in async
async fn async_operation() -> Result<String, Box<dyn std::error::Error>> {
    let response = reqwest::get("https://api.example.com")
        .await?
        .text()
        .await?;
    Ok(response)
}
```

## Memory Management - NO EXCEPTIONS

**MANDATORY ownership rules:**
```rust
// ENFORCE borrowing over ownership transfer
fn process_data(data: &str) -> usize {
    data.len() // Read-only access
}

// REQUIRED explicit cloning when necessary
let original = String::from("data");
let copy = original.clone(); // Explicit, intentional

// MANDATORY smart pointer usage for shared ownership
use std::sync::Arc;
let shared = Arc::new(expensive_data);
let reference = Arc::clone(&shared);
```

## Required Patterns - ENFORCE

**MANDATORY builder pattern for complex configuration:**
```rust
#[derive(Default)]
struct ConfigBuilder {
    host: Option<String>,
    port: Option<u16>,
}

impl ConfigBuilder {
    fn build(self) -> Result<Config, String> {
        Ok(Config {
            host: self.host.ok_or("host required")?,
            port: self.port.unwrap_or(8080),
        })
    }
}
```

**MANDATORY type state pattern for API safety:**
```rust
struct Authenticated { token: String }
struct Client<State> { state: State }

impl Client<Authenticated> {
    fn secure_request(&self) -> Result<Response, Error> {
        // Only callable when authenticated
    }
}
```

## Non-Negotiable Requirements

- **ENFORCE**: `cargo clippy` passes without warnings
- **MANDATE**: `cargo fmt` applied before every commit  
- **REQUIRE**: Documentation (`///`) for all public APIs
- **NO EXCEPTIONS**: All Results handled explicitly - no `unwrap()`
- **ENFORCE**: Type system prevents invalid states
- **MANDATE**: Tests for all public functions
- **REQUIRE**: Semantic versioning for all crates
- **ENFORCE**: Profile before performance optimization
- **NO UNSAFE**: Minimize unsafe code, document necessity