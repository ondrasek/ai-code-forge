# C++ Stack Instructions

MANDATORY operational instructions for Claude Code when working with modern C++ projects.

## Build System - ENFORCE

**MANDATORY CMake configuration:**
```cmake
# CMakeLists.txt - REQUIRED settings
cmake_minimum_required(VERSION 3.20)  # MANDATORY: Modern CMake
project(MyProject VERSION 1.0.0 LANGUAGES CXX)

# REQUIRED: C++20 or later
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)  # MANDATORY: No compiler extensions

# MANDATORY: Maximum warnings as errors
if(MSVC)
    add_compile_options(/W4 /WX /permissive-)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Werror -Wconversion)
endif()

# REQUIRED: Modern package management
find_package(fmt REQUIRED)
find_package(GTest REQUIRED)
find_package(spdlog REQUIRED)

# MANDATORY: Proper target configuration
add_library(mylib src/core.cpp src/utils.cpp)
target_include_directories(mylib 
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    PUBLIC $<INSTALL_INTERFACE:include>)
target_link_libraries(mylib PUBLIC fmt::fmt spdlog::spdlog)

# REQUIRED: Executable configuration
add_executable(myapp src/main.cpp)
target_link_libraries(myapp PRIVATE mylib)

# MANDATORY: Testing enabled
enable_testing()
add_subdirectory(tests)
```

## Build Workflow - MANDATORY

**REQUIRED build commands:**
```bash
# MANDATORY: Out-of-source build with specific build type
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

# REQUIRED: Parallel build
cmake --build build --parallel $(nproc)

# MANDATORY: Run tests before commit
ctest --test-dir build --output-on-failure --parallel

# REQUIRED: Static analysis (if available)
cmake --build build --target clang-tidy

# MANDATORY: Installation for distribution
cmake --install build --prefix /usr/local
```

## Modern C++ Features - MANDATORY USAGE

**ENFORCE C++20 features:**
```cpp
#include <concepts>
#include <ranges>
#include <span>
#include <string_view>

// MANDATORY: Concepts for template constraints
template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<Numeric T>
constexpr T add(T a, T b) noexcept {
    return a + b;  // REQUIRED: constexpr and noexcept where applicable
}

// REQUIRED: Ranges over raw loops
std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// MANDATORY: Use ranges pipeline syntax
auto result = numbers 
    | std::views::filter([](int n) { return n % 2 == 0; })
    | std::views::transform([](int n) { return n * n; })
    | std::ranges::to<std::vector>();  // C++23 or manual collection

// REQUIRED: Generic lambdas with proper constraints
template<Numeric T>
auto add_lambda = [](T x, T y) constexpr noexcept -> T { 
    return x + y; 
};
```

## Memory Management - NO EXCEPTIONS

**MANDATORY RAII and smart pointer usage:**
```cpp
#include <memory>
#include <span>

// REQUIRED: Smart pointers only - NEVER raw new/delete
auto unique = std::make_unique<Resource>(100);
auto shared = std::make_shared<Resource>(200);

// MANDATORY: Custom deleters for C resources
auto fileDeleter = [](FILE* f) noexcept { 
    if (f) fclose(f); 
};
std::unique_ptr<FILE, decltype(fileDeleter)> file(
    fopen("data.txt", "r"), fileDeleter);

// ENFORCE: Rule of Zero/Five implementation
class Resource {
public:
    explicit Resource(size_t size) : data_(size) {}
    
    // MANDATORY: Explicit default or delete
    ~Resource() = default;
    Resource(const Resource&) = delete;  // REQUIRED: Explicit copy policy
    Resource& operator=(const Resource&) = delete;
    Resource(Resource&&) = default;      // REQUIRED: Move semantics
    Resource& operator=(Resource&&) = default;
    
    // REQUIRED: Provide view interface
    std::span<const int> view() const noexcept { return data_; }
    
private:
    std::vector<int> data_;
};
```

## Error Handling - MANDATORY PATTERNS

**REQUIRED error handling strategies:**
```cpp
#include <optional>
#include <variant>
#include <expected>  // C++23 when available
#include <system_error>

// MANDATORY: std::optional for nullable returns
std::optional<int> divide(int a, int b) noexcept {
    if (b == 0) return std::nullopt;
    return a / b;
}

// REQUIRED: Result type for error propagation
template<typename T, typename E = std::string>
using Result = std::variant<T, E>;

Result<int> parseNumber(std::string_view str) noexcept {
    try {
        return std::stoi(std::string{str});
    } catch (const std::exception& e) {
        return std::string{"Parse error: "} + e.what();
    }
}

// MANDATORY: Exception safety guarantees
class Container {
    std::vector<std::unique_ptr<Resource>> resources_;
    
public:
    // REQUIRED: Strong exception safety
    void add(std::unique_ptr<Resource> resource) {
        resources_.push_back(std::move(resource));
    }
    
    // MANDATORY: noexcept for operations that cannot fail
    void swap(Container& other) noexcept {
        resources_.swap(other.resources_);
    }
    
    size_t size() const noexcept { return resources_.size(); }
};
```

## Concurrency - MANDATORY THREAD SAFETY

**REQUIRED thread-safe patterns:**
```cpp
#include <thread>
#include <mutex>
#include <atomic>
#include <future>

// MANDATORY: Lock-free when possible, proper locking otherwise
class ThreadSafeCounter {
    std::atomic<int> count_{0};
    
public:
    void increment() noexcept {
        count_.fetch_add(1, std::memory_order_relaxed);
    }
    
    int get() const noexcept {
        return count_.load(std::memory_order_relaxed);
    }
};

// REQUIRED: Async processing with proper exception handling
template<std::ranges::range Range>
auto parallel_sum(Range&& range) {
    using value_type = std::ranges::range_value_t<Range>;
    
    auto size = std::ranges::size(range);
    if (size < 1000) {
        return std::accumulate(std::ranges::begin(range), 
                             std::ranges::end(range), 
                             value_type{});
    }
    
    auto mid = std::ranges::begin(range) + size / 2;
    auto future = std::async(std::launch::async, 
        [mid, end = std::ranges::end(range)] {
            return std::accumulate(mid, end, value_type{});
        });
    
    auto sum1 = std::accumulate(std::ranges::begin(range), mid, value_type{});
    return sum1 + future.get();
}
```

## Testing - MANDATORY COVERAGE

**REQUIRED Google Test patterns:**
```cpp
#include <gtest/gtest.h>

// MANDATORY: Test fixture for complex setups
class MathTest : public ::testing::Test {
protected:
    void SetUp() override {
        // REQUIRED: Initialize test data
    }
    
    void TearDown() override {
        // REQUIRED: Cleanup resources
    }
};

// REQUIRED: Test both success and failure cases
TEST_F(MathTest, Addition) {
    EXPECT_EQ(add(2, 3), 5);
    EXPECT_EQ(add(-1, 1), 0);
    EXPECT_EQ(add(0, 0), 0);  // MANDATORY: Edge cases
}

// MANDATORY: Exception testing
TEST(MathTest, DivisionByZero) {
    EXPECT_THROW(divide(10, 0), std::invalid_argument);
}

// REQUIRED: Parameterized tests for comprehensive coverage
class PrimeTest : public ::testing::TestWithParam<int> {};

TEST_P(PrimeTest, IsPrime) {
    int n = GetParam();
    EXPECT_TRUE(isPrime(n));
}

INSTANTIATE_TEST_SUITE_P(PrimeNumbers, PrimeTest, 
    ::testing::Values(2, 3, 5, 7, 11, 13, 17, 19));
```

## Required Libraries - ENFORCE

**MANDATORY package management:**
```bash
# REQUIRED: Use modern package managers
vcpkg install fmt spdlog gtest nlohmann-json
# OR
conan install . --build=missing

# MANDATORY: Core libraries for all projects
fmt           # REQUIRED: String formatting (no printf)
spdlog        # REQUIRED: Structured logging
gtest         # REQUIRED: Unit testing framework
nlohmann-json # REQUIRED: JSON processing when needed
```

## Non-Negotiable Requirements

- **ENFORCE**: RAII for ALL resource management
- **MANDATE**: Stack allocation preferred over heap
- **REQUIRE**: const correctness - const by default
- **ENFORCE**: Rule of Zero/Five for all classes
- **FORBID**: Raw new/delete - smart pointers only
- **MANDATE**: STL algorithms over hand-written loops
- **REQUIRE**: Static analysis (clang-tidy) passes without warnings
- **ENFORCE**: All warnings enabled and treated as errors
- **MANDATE**: Minimum 80% unit test coverage
- **REQUIRE**: Profile before optimizing - measure first
- **ENFORCE**: Modern C++20 features - no legacy patterns
- **MANDATE**: Functions under 20 lines - extract if longer
- **REQUIRE**: Meaningful names - no abbreviations
- **FORBID**: Global state - use dependency injection