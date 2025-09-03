# Technology Stack Mapping Rules

<mapping_overview priority="LOW">
<purpose>Centralized technology detection logic for guidelines-file and guidelines-repo agents</purpose>
<function>Map file patterns to appropriate stack-specific guidance documents</function>
<enforcement>MUST use consistent detection patterns across all agents</enforcement>
</mapping_overview>

<file_extension_mapping priority="LOW">
<python_projects priority="LOW">
  <file_indicators>
    <pattern>*.py</pattern>
    <pattern>pyproject.toml</pattern>
    <pattern>requirements.txt</pattern>
    <pattern>Pipfile</pattern>
    <pattern>setup.py</pattern>
  </file_indicators>
  <stack_file>@.support/stacks/python.md</stack_file>
  <key_patterns>Python files, uv/pip configuration</key_patterns>
  <enforcement>DETECT Python projects using any indicator pattern</enforcement>
</python_projects>

<rust_projects priority="LOW">
  <file_indicators>
    <pattern>*.rs</pattern>
    <pattern>Cargo.toml</pattern>
    <pattern>Cargo.lock</pattern>
  </file_indicators>
  <stack_file>@.support/stacks/rust.md</stack_file>
  <key_patterns>Rust source files, Cargo configuration</key_patterns>
  <enforcement>DETECT Rust projects using any indicator pattern</enforcement>
</rust_projects>

<javascript_typescript_projects priority="LOW">
  <file_indicators>
    <pattern>*.js</pattern>
    <pattern>*.ts</pattern>
    <pattern>*.jsx</pattern>
    <pattern>*.tsx</pattern>
    <pattern>package.json</pattern>
    <pattern>package-lock.json</pattern>
    <pattern>yarn.lock</pattern>
    <pattern>tsconfig.json</pattern>
  </file_indicators>
  <stack_file>@.support/stacks/javascript.md</stack_file>
  <key_patterns>JS/TS files, npm/yarn configuration</key_patterns>
  <enforcement>DETECT JavaScript/TypeScript projects using any indicator pattern</enforcement>
</javascript_typescript_projects>

<java_projects priority="LOW">
  <file_indicators>
    <pattern>*.java</pattern>
    <pattern>pom.xml</pattern>
    <pattern>build.gradle</pattern>
    <pattern>gradle.properties</pattern>
    <pattern>settings.gradle</pattern>
  </file_indicators>
  <stack_file>@.support/stacks/java.md</stack_file>
  <key_patterns>Java source files, Maven/Gradle configuration</key_patterns>
  <enforcement>DETECT Java projects using any indicator pattern</enforcement>
</java_projects>

<kotlin_projects priority="LOW">
  <file_indicators>
    <pattern>*.kt</pattern>
    <pattern>*.kts</pattern>
    <pattern>build.gradle.kts</pattern>
  </file_indicators>
  <stack_file>@.support/stacks/kotlin.md</stack_file>
  <key_patterns>Kotlin source files, Gradle Kotlin DSL</key_patterns>
  <enforcement>DETECT Kotlin projects using any indicator pattern</enforcement>
</kotlin_projects>

<ruby_projects priority="LOW">
  <file_indicators>
    <pattern>*.rb</pattern>
    <pattern>Gemfile</pattern>
    <pattern>Gemfile.lock</pattern>
    <pattern>Rakefile</pattern>
    <pattern>config.ru</pattern>
  </file_indicators>
  <stack_file>@.support/stacks/ruby.md</stack_file>
  <key_patterns>Ruby source files, Bundler configuration</key_patterns>
  <enforcement>DETECT Ruby projects using any indicator pattern</enforcement>
</ruby_projects>

<csharp_projects priority="LOW">
  <file_indicators>
    <pattern>*.cs</pattern>
    <pattern>*.csproj</pattern>
    <pattern>*.sln</pattern>
    <pattern>*.props</pattern>
    <pattern>Directory.Build.props</pattern>
  </file_indicators>
  <stack_file>@.support/stacks/csharp.md</stack_file>
  <key_patterns>C# source files, MSBuild configuration</key_patterns>
  <enforcement>DETECT C# projects using any indicator pattern</enforcement>
</csharp_projects>

<cpp_projects priority="LOW">
  <file_indicators>
    <pattern>*.cpp</pattern>
    <pattern>*.cc</pattern>
    <pattern>*.cxx</pattern>
    <pattern>*.c</pattern>
    <pattern>*.h</pattern>
    <pattern>*.hpp</pattern>
    <pattern>CMakeLists.txt</pattern>
    <pattern>Makefile</pattern>
  </file_indicators>
  <stack_file>@.support/stacks/cpp.md</stack_file>
  <key_patterns>C++ source files, CMake/Make configuration</key_patterns>
  <enforcement>DETECT C++ projects using any indicator pattern</enforcement>
</cpp_projects>

<docker_projects priority="LOW">
  <file_indicators>
    <pattern>Dockerfile</pattern>
    <pattern>docker-compose.yml</pattern>
    <pattern>docker-compose.yaml</pattern>
    <pattern>.dockerignore</pattern>
  </file_indicators>
  <stack_file>@.support/stacks/docker.md</stack_file>
  <key_patterns>Docker configuration files</key_patterns>
  <enforcement>DETECT Docker projects using any indicator pattern</enforcement>
</docker_projects>

<bash_shell_projects priority="LOW">
  <file_indicators>
    <pattern>*.sh</pattern>
    <pattern>*.bash</pattern>
    <pattern>launch-*.sh</pattern>
    <pattern>install.sh</pattern>
    <pattern>deploy.sh</pattern>
    <pattern>build.sh</pattern>
    <pattern>test.sh</pattern>
  </file_indicators>
  <stack_file>@.support/stacks/bash.md</stack_file>
  <key_patterns>Shell/Bash scripts, automation scripts</key_patterns>
  <enforcement>DETECT Shell/Bash projects using any indicator pattern</enforcement>
</bash_shell_projects>
</file_extension_mapping>

<detection_algorithm priority="LOW">
<pattern_matching priority="LOW">
  <instruction>Scan project directory for indicator file patterns</instruction>
  <precedence>Multiple stack detection is acceptable</precedence>
  <selection>Choose most relevant stack based on file count and primary language</selection>
  <enforcement>APPLY consistent detection logic across all agents</enforcement>
</pattern_matching>

<multi_stack_handling priority="LOW">
  <scenario>Project contains multiple technology indicators</scenario>
  <approach>Identify all detected stacks and prioritize based on prevalence</approach>
  <documentation>Note all detected technologies in analysis</documentation>
  <enforcement>HANDLE multi-stack projects gracefully</enforcement>
</multi_stack_handling>
</detection_algorithm>

<stack_file_resolution priority="LOW">
<path_resolution priority="LOW">
  <base_path>@.support/stacks/</base_path>
  <naming_convention>[technology].md</naming_convention>
  <fallback>Use generic guidelines if stack-specific file unavailable</fallback>
  <enforcement>RESOLVE stack files consistently</enforcement>
</path_resolution>

<availability_checking priority="LOW">
  <check>Verify stack file exists before referencing</check>
  <fallback_behavior>Use general best practices if stack file missing</fallback_behavior>
  <error_handling>Log missing stack files for future creation</error_handling>
  <enforcement>VALIDATE stack file availability</enforcement>
</availability_checking>
</stack_file_resolution>

<usage_guidelines priority="LOW">
<agent_integration priority="LOW">
  <guidelines_file_agent>Use for single-file technology detection</guidelines_file_agent>
  <guidelines_repo_agent>Use for project-wide stack analysis</guidelines_repo_agent>
  <consistency>Ensure identical detection logic across agents</consistency>
  <enforcement>MAINTAIN consistent stack detection behavior</enforcement>
</agent_integration>

<detection_workflow priority="LOW">
  <step order="1">Scan project/file directory for indicator patterns</step>
  <step order="2">Match patterns against technology stack definitions</step>
  <step order="3">Resolve appropriate stack guidance file path</step>
  <step order="4">Verify stack file availability</step>
  <step order="5">Apply stack-specific guidelines or fallback to general</step>
  <enforcement>FOLLOW workflow sequence for reliable detection</enforcement>
</detection_workflow>
</usage_guidelines>

<maintenance_requirements priority="LOW">
<pattern_updates priority="LOW">
  <requirement>Update patterns when new file types emerge</requirement>
  <requirement>Add new technology stacks as they become prevalent</requirement>
  <requirement>Maintain alignment between patterns and actual stack files</requirement>
  <enforcement>KEEP mapping current with technology evolution</enforcement>
</pattern_updates>

<validation_procedures priority="LOW">
  <procedure>Test detection against real project samples</procedure>
  <procedure>Verify stack file existence for all mapped technologies</procedure>
  <procedure>Validate multi-stack project handling</procedure>
  <enforcement>VALIDATE mapping accuracy periodically</enforcement>
</validation_procedures>
</maintenance_requirements>
EOF < /dev/null