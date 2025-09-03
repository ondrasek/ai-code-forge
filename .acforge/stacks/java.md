# Java Stack Instructions

MANDATORY operational instructions for Claude Code when working with Java projects.

## Build Tools - ENFORCE

**MANDATORY build workflow:**
```bash
# Maven - REQUIRED commands
mvn clean compile                    # ALWAYS clean before compile
mvn test                            # MANDATORY before any commit
mvn verify                          # REQUIRED integration tests
mvn spring-boot:run                 # Development execution

# Gradle - REQUIRED commands  
./gradlew clean build               # ALWAYS clean build
./gradlew test                      # MANDATORY testing
./gradlew bootRun                   # Development execution
```

## Project Configuration - ENFORCE

**MANDATORY Maven setup (pom.xml):**
```xml
<properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <spring-boot.version>3.2.0</spring-boot.version>
</properties>
```

## Modern Java Features - MANDATORY USAGE

**ENFORCE Java 17+ features:**
```java
// MANDATORY: Records for data classes
public record User(String name, int age) {
    // REQUIRED: Input validation in compact constructor
    public User {
        Objects.requireNonNull(name, "Name cannot be null");
        if (age < 0) throw new IllegalArgumentException("Age cannot be negative");
    }
}

// MANDATORY: Pattern matching for instanceof
if (obj instanceof String s && !s.isBlank()) {
    processString(s.toUpperCase());
}

// REQUIRED: Switch expressions over statements
String result = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> "Weekend prep";
    case TUESDAY, WEDNESDAY, THURSDAY -> "Workday";
    case SATURDAY -> "Weekend";
};
```

## Spring Boot Controllers - ENFORCE

**MANDATORY controller patterns:**
```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Validated  // REQUIRED for validation
public class UserController {
    private final UserService userService;
    
    @GetMapping
    public ResponseEntity<Page<UserDto>> getAllUsers(
            @PageableDefault(size = 20) Pageable pageable) {
        // MANDATORY: Always paginate collections
        return ResponseEntity.ok(userService.findAll(pageable));
    }
    
    @PostMapping
    public ResponseEntity<UserDto> createUser(
            @Valid @RequestBody CreateUserRequest request) {
        // REQUIRED: Return 201 Created with location header
        UserDto user = userService.create(request);
        URI location = URI.create("/api/v1/users/" + user.id());
        return ResponseEntity.created(location).body(user);
    }
}
```

## Service Layer - MANDATORY PATTERNS

**REQUIRED service implementation:**
```java
@Service
@Transactional(readOnly = true)  // MANDATORY: Default read-only
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final UserMapper userMapper;
    
    public Page<UserDto> findAll(Pageable pageable) {
        // ENFORCE: Always use pagination
        return userRepository.findAll(pageable)
            .map(userMapper::toDto);
    }
    
    @Transactional  // REQUIRED: Write operations override read-only
    public UserDto create(CreateUserRequest request) {
        // MANDATORY: Validate business rules
        validateBusinessRules(request);
        User user = userMapper.toEntity(request);
        user = userRepository.save(user);
        return userMapper.toDto(user);
    }
    
    private void validateBusinessRules(CreateUserRequest request) {
        // REQUIRED: Business validation separate from bean validation
        if (userRepository.existsByEmail(request.email())) {
            throw new DuplicateEmailException("Email already exists");
        }
    }
}
```

## JPA Repository - ENFORCE

**MANDATORY repository patterns:**
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // REQUIRED: Specific query methods over @Query when possible
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);
    
    // MANDATORY: Pageable support for collections
    Page<User> findByActiveTrue(Pageable pageable);
}
```

## JPA Entity - REQUIRED PATTERNS

**MANDATORY entity structure:**
```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    // REQUIRED: Non-null constraints with validation
    @Column(nullable = false, unique = true)
    @Email
    private String email;
    
    // MANDATORY: Audit fields
    @CreatedDate
    private LocalDateTime createdAt;
    
    @Version  // REQUIRED: Optimistic locking
    private Long version;
}
```

## Exception Handling - MANDATORY

**REQUIRED global exception handler:**
```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {
    
    @ExceptionHandler(EntityNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(EntityNotFoundException e) {
        log.error("Entity not found: {}", e.getMessage());
        return new ErrorResponse(e.getMessage());
    }
    
    // MANDATORY: Validation error handling
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ValidationErrorResponse handleValidation(MethodArgumentNotValidException e) {
        return ValidationErrorResponse.from(e.getBindingResult());
    }
}
```

## Testing - MANDATORY COVERAGE

**REQUIRED test patterns:**
```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private UserService userService;
    
    @Test
    void createUser_WithValidData_ReturnsCreated() throws Exception {
        // MANDATORY: Test happy path AND error cases
        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(validUserJson))
            .andExpect(status().isCreated())
            .andExpect(header().exists("Location"));
    }
}
```

## Non-Negotiable Requirements

- **ENFORCE**: Java 17+ features (records, pattern matching, switch expressions)
- **MANDATE**: @Transactional(readOnly = true) as default on services
- **REQUIRE**: Pagination for all collection endpoints
- **ENFORCE**: Bean validation (@Valid) on all request objects
- **MANDATE**: Global exception handling with proper HTTP status codes
- **REQUIRE**: Optimistic locking (@Version) on all entities
- **ENFORCE**: Comprehensive test coverage (unit + integration)
- **MANDATE**: Audit fields (created/modified timestamps) on entities
- **REQUIRE**: Connection pooling and query optimization
- **ENFORCE**: Security configuration for all endpoints