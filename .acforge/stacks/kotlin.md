# Kotlin Stack Instructions

MANDATORY operational instructions for Claude Code when working with Kotlin backend projects.

## Build System - ENFORCE

**MANDATORY Gradle Kotlin DSL setup:**
```kotlin
// build.gradle.kts - REQUIRED configuration
plugins {
    kotlin("jvm") version "1.9.20"
    kotlin("plugin.spring") version "1.9.20"
    kotlin("plugin.jpa") version "1.9.20"  // REQUIRED for JPA
    id("org.springframework.boot") version "3.2.0"
}

// MANDATORY dependencies
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-reactor")  // REQUIRED for reactive
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")  // MANDATORY JSON
    testImplementation("io.mockk:mockk")  // REQUIRED for testing
}
```

## Project Structure - ENFORCE

**MANDATORY Kotlin project layout:**
```
src/main/kotlin/com/company/app/
├── Application.kt              # REQUIRED main class
├── controller/                 # REST controllers only
├── service/                    # Business logic
├── repository/                 # Data access
└── model/                      # Data classes and entities
src/test/kotlin/                # MANDATORY test coverage
```

## Modern Kotlin Features - MANDATORY USAGE

**ENFORCE Kotlin idioms:**
```kotlin
// MANDATORY: Data classes with validation
data class CreateUserRequest(
    @field:NotBlank @field:Email val email: String,
    @field:NotBlank @field:Size(min = 2, max = 100) val name: String
) {
    // REQUIRED: Input validation in init block when needed
    init {
        require(email.isNotBlank()) { "Email cannot be blank" }
    }
}

// REQUIRED: Sealed classes for type-safe results
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val cause: Throwable? = null) : Result<Nothing>()
}

// MANDATORY: Extension functions for domain operations
inline fun <T, R> Result<T>.onSuccess(action: (T) -> R): Result<T> {
    if (this is Result.Success) action(data)
    return this
}
```

## Spring Boot Controllers - ENFORCE

**MANDATORY controller patterns:**
```kotlin
@RestController
@RequestMapping("/api/v1/users")
@Validated  // REQUIRED for validation
class UserController(private val userService: UserService) {
    
    @GetMapping
    suspend fun getAllUsers(
        @PageableDefault(size = 20) pageable: Pageable
    ): ResponseEntity<Page<UserResponse>> {
        // MANDATORY: Always return ResponseEntity with proper status
        val users = userService.findAll(pageable)
        return ResponseEntity.ok(users.map(UserResponse::from))
    }
    
    @PostMapping
    suspend fun createUser(
        @Valid @RequestBody request: CreateUserRequest
    ): ResponseEntity<UserResponse> {
        // REQUIRED: Return 201 Created with location header
        val user = userService.create(request)
        val location = URI.create("/api/v1/users/${user.id}")
        return ResponseEntity.created(location).body(UserResponse.from(user))
    }
}
```

## Service Layer - MANDATORY PATTERNS

**REQUIRED service implementation:**
```kotlin
@Service
@Transactional(readOnly = true)  // MANDATORY: Default read-only
class UserService(private val userRepository: UserRepository) {
    
    @Transactional  // REQUIRED: Override for write operations
    suspend fun create(request: CreateUserRequest): User = withContext(Dispatchers.IO) {
        // MANDATORY: Business validation before persistence
        validateBusinessRules(request)
        userRepository.save(User(email = request.email, name = request.name))
    }
    
    private suspend fun validateBusinessRules(request: CreateUserRequest) {
        userRepository.findByEmail(request.email)?.let {
            throw DuplicateEmailException("Email already exists")
        }
    }
}
```

## Database & JPA - ENFORCE

**MANDATORY entity and repository patterns:**
```kotlin
@Entity
@Table(name = "users")
class User(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,  // REQUIRED: Immutable ID
    
    @Column(unique = true, nullable = false)
    val email: String,  // MANDATORY: Immutable fields where possible
    
    @CreatedDate val createdAt: Instant = Instant.now(),
    @Version val version: Long = 0  // REQUIRED: Optimistic locking
)

@Repository
interface UserRepository : JpaRepository<User, Long> {
    // REQUIRED: Specific query methods over @Query
    fun findByEmail(email: String): User?
    fun existsByEmail(email: String): Boolean
    
    // MANDATORY: Suspend functions for async operations
    suspend fun findByNameContaining(name: String): List<User>
}
```

## Coroutines - MANDATORY USAGE

**REQUIRED async patterns:**
```kotlin
// MANDATORY: Structured concurrency with coroutineScope
suspend fun processMultipleSources(): ProcessingResult = coroutineScope {
    val deferred1 = async { fetchFromSource1() }
    val deferred2 = async { fetchFromSource2() }
    awaitAll(deferred1, deferred2)  // REQUIRED: Wait for all
}

// ENFORCE: Flow for reactive streams
fun processStream(): Flow<ProcessedItem> = flow {
    getDataStream().collect { rawData ->
        emit(processItem(rawData))
    }
}.flowOn(Dispatchers.Default)  // REQUIRED: Specify dispatcher
```

## Testing - MANDATORY COVERAGE

**REQUIRED test patterns:**
```kotlin
@ExtendWith(MockKExtension::class)
class UserServiceTest {
    @MockK private lateinit var userRepository: UserRepository
    @InjectMockKs private lateinit var userService: UserService
    
    @Test
    fun `should create user successfully`() = runTest {
        // MANDATORY: Given-When-Then structure
        every { userRepository.findByEmail(any()) } returns null
        every { userRepository.save(any()) } returns user
        
        val result = userService.create(request)
        
        // REQUIRED: Verify both result and interactions
        assertThat(result).isEqualTo(user)
        verify { userRepository.save(any()) }
    }
}
```

## Non-Negotiable Requirements

- **ENFORCE**: Coroutines for all async operations - NO blocking calls
- **MANDATE**: Null safety - NEVER use !! operator in production
- **REQUIRE**: Immutability with val over var where possible
- **ENFORCE**: Data classes for DTOs, entities use regular classes
- **MANDATE**: Extension functions for domain-specific operations
- **REQUIRE**: MockK for all Kotlin testing - never Mockito
- **ENFORCE**: Structured concurrency with coroutineScope
- **MANDATE**: Suspend functions for all IO operations
- **REQUIRE**: Flow for reactive streams and event processing