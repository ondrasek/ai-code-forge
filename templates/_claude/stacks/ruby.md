# Ruby Stack Instructions

MANDATORY operational instructions for Claude Code when working with Ruby projects.

## Version Management - ENFORCE

**MANDATORY Ruby version and dependency management:**
```bash
# REQUIRED: Use rbenv for version management - NO EXCEPTIONS
rbenv install 3.2.2
rbenv local 3.2.2

# MANDATORY bundler workflow
bundle install                # ALWAYS after Gemfile changes
bundle exec rspec             # REQUIRED for running tests
bundle exec rubocop           # MANDATORY before commits
bundle exec rake              # REQUIRED for deployment tasks
```

## Gemfile - MANDATORY CONFIGURATION

**REQUIRED gem setup:**
```ruby
source 'https://rubygems.org'
ruby '3.2.2'  # MANDATORY: Pin Ruby version

# REQUIRED: Core Rails gems
gem 'rails', '~> 7.0'
gem 'pg', '~> 1.4'      # MANDATORY: PostgreSQL only
gem 'puma', '~> 6.0'    # REQUIRED: Application server

# MANDATORY: Development and testing tools
group :development, :test do
  gem 'rspec-rails', '~> 6.0'   # REQUIRED: Testing framework
  gem 'rubocop', require: false  # MANDATORY: Code quality
  gem 'factory_bot_rails'        # REQUIRED: Test data
end

group :test do
  gem 'simplecov', require: false  # MANDATORY: Coverage reporting
end
```

## Ruby Conventions - ENFORCE

**MANDATORY naming and style conventions:**
```ruby
# REQUIRED: PascalCase for classes and modules
class UserAccount; end
module PaymentProcessor; end

# MANDATORY: snake_case for methods and variables
def calculate_total_price
  user_name = "John"  # REQUIRED: snake_case variables
end

# REQUIRED: SCREAMING_SNAKE_CASE for constants
MAX_RETRY_COUNT = 3
API_BASE_URL = "https://api.example.com"

# MANDATORY: Predicate methods end with ?
def valid?
  !expired? && active?
end

# REQUIRED: Destructive methods end with !
def save!
  save || raise(RecordNotSaved)
end
```

## Required Patterns - ENFORCE

**MANDATORY Ruby idioms:**
```ruby
# REQUIRED: Symbols for hash keys - NEVER strings
user = { name: "Alice", age: 30 }

# MANDATORY: Memoization pattern with ||=
def expensive_calculation
  @result ||= perform_calculation
end

# REQUIRED: Safe navigation operator
user&.profile&.name  # NEVER user.profile.name without safety

# MANDATORY: Trailing conditionals for guard clauses
return unless user.authorized?
process_order if order.valid?

# REQUIRED: Object initialization with tap
User.new.tap do |u|
  u.name = "Bob"
  u.email = "bob@example.com"
  u.save!
end
```

## Object-Oriented Design - MANDATORY PATTERNS

**REQUIRED Ruby class structure:**
```ruby
class User
  # MANDATORY: Use attr_* for accessor methods
  attr_reader :id, :name
  attr_accessor :email
  attr_writer :password
  
  # REQUIRED: Keyword arguments for initialize
  def initialize(name:, email:)
    @name = name
    @email = email
  end
  
  # MANDATORY: Class methods for finders
  def self.find_by_email(email)
    # Implementation with proper error handling
  end
  
  private
  
  # REQUIRED: Private methods for internal logic
  def validate_email
    # Private validation logic
  end
end

# MANDATORY: Modules with ActiveSupport::Concern
module Trackable
  extend ActiveSupport::Concern
  
  included do
    has_many :activities  # REQUIRED: Define associations
  end
  
  def track_activity(action)
    activities.create!(action: action)  # REQUIRED: Use bang methods
  end
end
```

## Error Handling - NO EXCEPTIONS

**MANDATORY error handling patterns:**
```ruby
# REQUIRED: Always handle StandardError specifically
begin
  risky_operation
rescue StandardError => e
  logger.error "Operation failed: #{e.message}"
  raise  # MANDATORY: Re-raise unless handling completely
end

# REQUIRED: Specific rescue clauses before generic
begin
  api_call
rescue Net::HTTPError => e
  handle_http_error(e)
rescue Timeout::Error => e
  handle_timeout(e)
rescue StandardError => e  # REQUIRED: Never bare rescue
  handle_generic_error(e)
ensure
  cleanup_resources  # MANDATORY: Always cleanup
end

# MANDATORY: Custom exception hierarchy
class ApplicationError < StandardError; end
class ValidationError < ApplicationError; end
class BusinessRuleError < ApplicationError; end

# REQUIRED: Retry pattern with exponential backoff
def fetch_with_retry(url, max_retries: 3)
  retries = 0
  begin
    HTTP.get(url)
  rescue Net::HTTPError => e
    retries += 1
    if retries < max_retries
      sleep(2 ** retries)  # REQUIRED: Exponential backoff
      retry
    else
      raise  # MANDATORY: Re-raise after max retries
    end
  end
end
```

## Testing - MANDATORY COVERAGE

**REQUIRED RSpec patterns:**
```ruby
# spec/models/user_spec.rb
require 'rails_helper'

RSpec.describe User, type: :model do
  # MANDATORY: Test all validations
  describe 'validations' do
    it { should validate_presence_of(:email) }
    it { should validate_uniqueness_of(:email) }
  end
  
  # REQUIRED: Test all public methods
  describe '#full_name' do
    let(:user) { build(:user, first_name: 'John', last_name: 'Doe') }
    
    it 'returns the combined first and last name' do
      expect(user.full_name).to eq('John Doe')
    end
  end
  
  # MANDATORY: Test scopes and class methods
  describe '.active' do
    let!(:active_user) { create(:user, active: true) }
    let!(:inactive_user) { create(:user, active: false) }
    
    it 'returns only active users' do
      expect(User.active).to include(active_user)
      expect(User.active).not_to include(inactive_user)
    end
  end
end
```

## Rails Patterns - ENFORCE

**MANDATORY ActiveRecord optimization:**
```ruby
# FORBIDDEN - N+1 queries
# users = User.all
# users.each { |user| puts user.posts.count }

# REQUIRED - Eager loading with includes
users = User.includes(:posts)
users.each { |user| puts user.posts.size }

# MANDATORY - Service objects for complex operations
class UserRegistrationService
  def initialize(user_params)
    @user_params = user_params
  end
  
  def call
    ActiveRecord::Base.transaction do
      user = User.create!(@user_params)  # REQUIRED: Bang methods
      send_welcome_email(user)
      create_default_settings(user)
      Result.success(user)
    end
  rescue ActiveRecord::RecordInvalid => e
    Result.error("Registration failed", e.record.errors)
  end
end
```

## Code Quality - MANDATORY ENFORCEMENT

**REQUIRED quality checks before every commit:**
```bash
# MANDATORY - RuboCop compliance
bundle exec rubocop --fail-level error
bundle exec rubocop -a  # Auto-fix safe corrections

# REQUIRED - Security scanning
bundle exec brakeman --no-pager

# MANDATORY - Test coverage (minimum 90%)
bundle exec rspec
# SimpleCov will enforce coverage threshold
```

## Non-Negotiable Requirements

- **ENFORCE**: Ruby Style Guide compliance via RuboCop
- **MANDATE**: TDD/BDD approach - tests before implementation
- **REQUIRE**: Methods under 10 lines - extract if longer
- **ENFORCE**: Descriptive names - no abbreviations or unclear terms
- **FORBID**: Monkey patching core classes - use refinements if needed
- **MANDATE**: Composition over inheritance pattern
- **REQUIRE**: frozen_string_literal pragma in all files
- **ENFORCE**: 90% minimum test coverage with SimpleCov
- **MANDATE**: ActiveRecord query optimization - no N+1 queries
- **REQUIRE**: Service objects for complex business operations