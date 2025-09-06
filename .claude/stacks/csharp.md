# C# Stack Instructions

MANDATORY operational instructions for Claude Code when working with C#/.NET projects.

## Project Setup - ENFORCE

**MANDATORY .NET CLI workflow:**
```bash
# REQUIRED project creation
dotnet new webapi -n MyApi --framework net8.0
dotnet new classlib -n MyLibrary --framework net8.0  
dotnet new xunit -n MyTests --framework net8.0

# MANDATORY solution management
dotnet new sln -n MySolution
dotnet sln add **/*.csproj  # Add all projects

# REQUIRED build workflow
dotnet restore                    # ALWAYS before build
dotnet build --no-restore         # MANDATORY before run/test
dotnet test --no-build           # REQUIRED before commit
dotnet publish -c Release        # Production deployment only
```

## Project Configuration - MANDATORY

**REQUIRED .csproj settings:**
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>              <!-- MANDATORY -->
    <ImplicitUsings>enable</ImplicitUsings>  <!-- REQUIRED -->
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>  <!-- ENFORCE -->
  </PropertyGroup>

  <!-- MANDATORY packages -->
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.0.0" />
    <PackageReference Include="FluentValidation.AspNetCore" Version="11.3.0" />
    <PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
  </ItemGroup>
</Project>
```

## Modern C# Features - MANDATORY USAGE

**ENFORCE C# 12 features:**
```csharp
// MANDATORY: Primary constructors for services
public class UserService(IUserRepository repository, ILogger<UserService> logger) {
    public async Task<User?> GetUserAsync(int id, CancellationToken cancellationToken = default) {
        logger.LogInformation("Getting user {UserId}", id);
        // REQUIRED: Always pass cancellation token
        return await repository.GetByIdAsync(id, cancellationToken);
    }
}

// REQUIRED: Records for DTOs and requests
public record CreateUserRequest(string Email, string Name) {
    // MANDATORY: Input validation in record
    public CreateUserRequest {
        ArgumentException.ThrowIfNullOrWhiteSpace(Email);
        ArgumentException.ThrowIfNullOrWhiteSpace(Name);
    }
};

public record UserResponse(int Id, string Email, string Name, DateTime CreatedAt);

// MANDATORY: Pattern matching over if-else chains
public string GetUserStatus(UserResponse user) => user switch {
    { Id: 0 } => "New user",
    { CreatedAt: var date } when date > DateTime.Now.AddDays(-7) => "Recently joined",
    { CreatedAt: var date } when date < DateTime.Now.AddYears(-1) => "Inactive user",
    _ => "Regular user"
};
```

## ASP.NET Core Controllers - ENFORCE

**MANDATORY controller patterns:**
```csharp
[ApiController]
[Route("api/v1/[controller]")]  // REQUIRED: Versioned routes
[Produces("application/json")]   // MANDATORY: Content type
public class UsersController(IUserService userService) : ControllerBase {
    
    [HttpGet]
    [ProducesResponseType(typeof(PagedResult<UserResponse>), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetAll(
        [FromQuery] int page = 1, 
        [FromQuery] int pageSize = 20,
        CancellationToken cancellationToken = default) {
        // MANDATORY: Always paginate and use cancellation tokens
        var users = await userService.GetPaginatedAsync(page, pageSize, cancellationToken);
        return Ok(users);
    }
    
    [HttpPost]
    [ProducesResponseType(typeof(UserResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> Create(
        [FromBody] CreateUserRequest request, 
        CancellationToken cancellationToken = default) {
        // REQUIRED: Business validation before processing
        var user = await userService.CreateAsync(request, cancellationToken);
        return CreatedAtAction(nameof(GetById), new { id = user.Id }, user);
    }
}
```

## Entity Framework - MANDATORY PATTERNS

**REQUIRED EF Core configuration:**
```csharp
public class ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : DbContext(options) {
    public DbSet<User> Users => Set<User>();
    
    protected override void OnModelCreating(ModelBuilder modelBuilder) {
        // MANDATORY: Explicit entity configuration
        modelBuilder.Entity<User>(entity => {
            entity.HasKey(u => u.Id);
            entity.Property(u => u.Email).IsRequired().HasMaxLength(256);
            entity.HasIndex(u => u.Email).IsUnique();
            
            // REQUIRED: Audit fields configuration
            entity.Property(u => u.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
            entity.Property(u => u.RowVersion).IsRowVersion();  // MANDATORY: Concurrency
        });
    }
}

// MANDATORY: Domain entity with required properties
public class User {
    public int Id { get; set; }
    public required string Email { get; set; }
    public required string Name { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
    public byte[] RowVersion { get; set; } = Array.Empty<byte>();  // REQUIRED: Optimistic concurrency
}
```

## Dependency Injection - ENFORCE

**MANDATORY service registration:**
```csharp
var builder = WebApplication.CreateBuilder(args);

// REQUIRED: Database configuration
builder.Services.AddDbContext<ApplicationDbContext>(options => {
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection"));
    options.EnableSensitiveDataLogging(builder.Environment.IsDevelopment());
});

// MANDATORY: Service registration with proper lifetimes
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<IUserRepository, UserRepository>();

// REQUIRED: Configuration binding with validation
builder.Services.Configure<JwtSettings>(builder.Configuration.GetSection("Jwt"));
builder.Services.AddOptions<JwtSettings>()
    .BindConfiguration("Jwt")
    .ValidateDataAnnotations()
    .ValidateOnStart();

var app = builder.Build();
```

## Error Handling - MANDATORY

**REQUIRED global exception middleware:**
```csharp
public class GlobalExceptionMiddleware(RequestDelegate next, ILogger<GlobalExceptionMiddleware> logger) {
    
    public async Task InvokeAsync(HttpContext context) {
        try {
            await next(context);
        } catch (Exception ex) {
            logger.LogError(ex, "Unhandled exception occurred");
            await HandleExceptionAsync(context, ex);
        }
    }
    
    private static async Task HandleExceptionAsync(HttpContext context, Exception exception) {
        var (statusCode, message) = exception switch {
            NotFoundException => (404, exception.Message),
            ValidationException => (400, "Validation failed"),
            ArgumentException => (400, exception.Message),
            UnauthorizedAccessException => (401, "Unauthorized"),
            _ => (500, "Internal server error")
        };
        
        context.Response.StatusCode = statusCode;
        context.Response.ContentType = "application/json";
        
        var response = new { Error = message, StatusCode = statusCode };
        await context.Response.WriteAsync(JsonSerializer.Serialize(response));
    }
}
```

## Testing - MANDATORY COVERAGE

**REQUIRED xUnit test patterns:**
```csharp
public class UserServiceTests {
    private readonly Mock<IUserRepository> _mockRepository = new();
    private readonly Mock<ILogger<UserService>> _mockLogger = new();
    private readonly UserService _service;
    
    public UserServiceTests() {
        _service = new UserService(_mockRepository.Object, _mockLogger.Object);
    }
    
    [Fact]
    public async Task GetByIdAsync_WhenUserExists_ReturnsUser() {
        // MANDATORY: Arrange-Act-Assert pattern
        var expectedUser = new User { Id = 1, Email = "test@example.com", Name = "Test" };
        _mockRepository.Setup(r => r.GetByIdAsync(1, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expectedUser);
        
        var result = await _service.GetByIdAsync(1);
        
        // REQUIRED: Comprehensive assertions
        Assert.NotNull(result);
        Assert.Equal(expectedUser.Email, result.Email);
        _mockRepository.Verify(); // MANDATORY: Verify mock interactions
    }
    
    [Theory]
    [InlineData("")]
    [InlineData(" ")]
    [InlineData(null)]
    public async Task CreateAsync_WithInvalidEmail_ThrowsValidationException(string? email) {
        // REQUIRED: Test all invalid input scenarios
        var request = new CreateUserRequest(email!, "Test");
        
        await Assert.ThrowsAsync<ValidationException>(() => 
            _service.CreateAsync(request, CancellationToken.None));
    }
}
```

## Non-Negotiable Requirements

- **ENFORCE**: Nullable reference types enabled project-wide
- **MANDATE**: Async/await for all I/O operations with CancellationToken support
- **REQUIRE**: Dependency injection for all service dependencies
- **ENFORCE**: Global exception handling middleware for all applications
- **MANDATE**: Entity Framework migrations for all database changes
- **REQUIRE**: Comprehensive unit and integration test coverage (minimum 80%)
- **ENFORCE**: SOLID principles in all class design
- **MANDATE**: Configuration validation with strongly-typed options
- **REQUIRE**: Structured logging with Serilog
- **ENFORCE**: Optimistic concurrency control on all entities