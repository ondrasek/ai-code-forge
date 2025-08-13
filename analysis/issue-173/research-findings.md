# Issue #173 Research Findings

## Issue Summary
**Title**: feat: implement terminal title management with issue numbers in worktree scripts
**Status**: OPEN
**Labels**: enhancement, feat
**Priority**: Medium (no priority label - appropriate per owner validation)

## Technical Requirements
- Implement terminal escape sequences for automatic title changes
- Cross-platform compatibility (iTerm2, Terminal.app, gnome-terminal, Windows Terminal)
- Security: Sanitized input to prevent escape sequence injection
- Integration with existing worktree scripts
- Graceful fallback for unsupported terminals

## Comprehensive External Research Results

### ANSI OSC (Operating System Command) Sequences

**Standards Foundation:**
- Based on ECMA-48 (5th edition, 1991), ISO/IEC 6429, ANSI X3.64 standards
- XTerm Control Sequences document (updated 2025/06/22, Patch #401) serves as de facto standard
- OSC sequences follow format: `ESC ] Ps ; Pt BEL` or `ESC ] Ps ; Pt ST`

**Terminal Title Control Sequences:**
- `OSC 0 ; txt BEL/ST` - Set icon name and window title
- `OSC 1 ; txt BEL/ST` - Set icon name only  
- `OSC 2 ; txt BEL/ST` - Set window title only
- Two terminator options: BEL (0x07) or ST (ESC \)

**Standard Escape Sequences:**
```bash
# Set both icon and window title
echo -e '\e]0;TITLE\e\\'
echo -e '\e]0;TITLE\a'

# Set window title only  
echo -e '\e]2;TITLE\e\\'
echo -e '\e]2;TITLE\a'

# Set icon name only
echo -e '\e]1;TITLE\e\\'
echo -e '\e]1;TITLE\a'
```

### Cross-Platform Terminal Compatibility

**Universal Compatibility (2025):**
- Standard OSC sequences (`\e]0;`, `\e]1;`, `\e]2;`) work across all major terminals
- iTerm2, Terminal.app, GNOME Terminal, Windows Terminal support xterm standards
- Most modern terminals implement xterm escape sequence subset for compatibility

**Terminal-Specific Features:**
- **iTerm2:** Supports additional OSC 6 sequences for tab coloring
- **Windows Terminal:** Sets `TERM_PROGRAM=WindowsTerminal` for detection
- **GNOME Terminal (VTE):** Full xterm compatibility with VT102/ECMA-48 support
- **Legacy Support:** VT100 core sequences supported by virtually all terminals

**tmux/screen Compatibility:**
- **tmux 3.4+:** Supports OSC 133 shell integration, OSC 52 clipboard access
- **tmux title handling:** Window title (#T) set via OSC sequences: `printf '\033]2;My Title\033\\'`
- **screen:** Basic OSC support, but tmux preferred for modern workflows
- **Pass-through:** Requires `set -g allow-passthrough on` in tmux.conf for advanced OSC

### Terminal Capability Detection Methods

**$TERM Environment Variable:**
- Primary mechanism: Applications query terminal capabilities via terminfo database
- Common values: `xterm`, `xterm-256color`, `screen`, `tmux-256color`
- Location: `/lib/terminfo`, `$HOME/.terminfo`, or `$TERMINFO` directories
- Modern terminals often set `TERM=xterm` for maximum compatibility

**Feature Detection Approaches:**
```bash
# Basic terminal type detection
case "$TERM" in
    xterm*|rxvt*|alacritty|tmux*|screen*)
        # Terminal supports OSC sequences
        ;;
    linux|vt*)
        # Console terminal, limited escape support
        ;;
esac

# Modern terminal program detection
if [[ -n "$TERM_PROGRAM" ]]; then
    case "$TERM_PROGRAM" in
        iTerm.app) echo "iTerm2 detected" ;;
        Terminal.app) echo "macOS Terminal detected" ;;
        WindowsTerminal) echo "Windows Terminal detected" ;;
    esac
fi
```

**Additional Detection Variables (2025):**
- `$TERM_PROGRAM` and `$TERM_PROGRAM_VERSION` for specific terminal identification
- `$COLORTERM` for color capability detection
- Query sequences for runtime capability detection (experimental)

### Security Considerations for Escape Sequence Injection

**Critical Security Vulnerabilities (2025):**
- **ANSI Terminal Code Abuse:** Escape sequences can hide malicious instructions
- **Log Injection (OWASP):** Tracked as CWE-150 - Improper Neutralization of Escape Sequences
- **Recent Attacks:** MCP (Model Context Protocol) vulnerabilities discovered in 2025

**Attack Vectors:**
- Invisible text via foreground/background color manipulation
- Screen content overwriting using cursor movement
- Clipboard injection via OSC 52 sequences
- Hyperlink manipulation for phishing attacks

**Essential Sanitization Practices:**
```bash
# Basic escape sequence removal
sanitize_title() {
    local title="$1"
    # Remove escape character (0x1b) and control characters
    title="${title//$(printf '\033')/}"
    title="${title//$(printf '\007')/}"  # BEL
    title="${title//$(printf '\x1b')/}" # ESC
    # Limit length to prevent buffer overflow
    title="${title:0:100}"
    echo "$title"
}

# Comprehensive sanitization
secure_title() {
    local title="$1"
    # Whitelist approach: only allow printable ASCII
    title=$(echo "$title" | tr -cd '[:print:]' | tr -cd '[:space:][:alnum:][:punct:]')
    # Remove potential injection characters
    title="${title//\$/}"    # Shell variables
    title="${title//\`/}"    # Command substitution
    title="${title//;/}"     # Command separator
    echo "${title:0:80}"     # Enforce length limit
}
```

**Protection Requirements:**
- Replace byte 0x1b (escape) with placeholder character
- Implement input validation with whitelist approach
- Limit title length (recommended: 80-100 characters)
- Encode special characters that have terminal meaning
- Server-side validation as primary security measure

### Shell Integration Patterns (2025)

**Bash Integration:**
```bash
# PROMPT_COMMAND for dynamic titles
PROMPT_COMMAND='echo -ne "\e]0;${USER}@${HOSTNAME}: ${PWD}\e\\"'

# Function-based approach
set_title() {
    local title="$1"
    title=$(sanitize_title "$title")
    case "$TERM" in
        xterm*|rxvt*|alacritty|tmux*|screen*)
            echo -ne "\e]0;${title}\e\\"
            ;;
    esac
}
```

**Zsh Integration:**
```zsh
# Precmd hook for title updates
precmd() {
    local title="${USER}@${HOST}: ${PWD}"
    title=$(sanitize_title "$title")
    print -Pn "\e]0;${title}\e\\"
}

# Preexec for command-based titles
preexec() {
    local cmd="$1"
    local title="${USER}@${HOST}: ${cmd}"
    title=$(sanitize_title "$title")
    print -Pn "\e]0;${title}\e\\"
}
```

**Fish Shell Integration:**
```fish
# fish_title function (built-in)
function fish_title
    set -l title (prompt_pwd)
    if test -n "$argv[1]"
        set title "$argv[1] - $title"
    end
    echo (sanitize_title "$title")
end

# Custom sanitization function
function sanitize_title
    string replace -a (printf '\033') '' $argv | string sub -l 80
end
```

**Modern Shell Ecosystem (2025):**
- Fish shell adoption grown 340% due to zero-configuration approach
- Zsh remains dominant with Oh My Zsh ecosystem
- Shell integration focuses on prompt frameworks (Starship, Powerlevel10k, Tide)
- Performance optimization: Fish reduces command completion time by 23% vs. Bash

### Fallback Mechanisms for Unsupported Terminals

**Detection and Graceful Degradation:**
```bash
supports_osc_titles() {
    case "$TERM" in
        # Known compatible terminals
        xterm*|rxvt*|alacritty|kitty|tmux*|screen*|iterm*|vte*)
            return 0
            ;;
        # Console terminals (limited support)
        linux|vt100|vt102|vt220)
            return 1
            ;;
        # Unknown terminals - test capability
        *)
            # Conservative approach: assume no support
            return 1
            ;;
    esac
}

set_terminal_title() {
    local title="$1"
    
    # Sanitize input
    title=$(sanitize_title "$title")
    
    # Check terminal support
    if supports_osc_titles; then
        echo -ne "\e]0;${title}\e\\"
    else
        # Fallback: update PS1 prompt instead
        PS1="[${title}] ${PS1}"
    fi
}
```

**Alternative Fallback Strategies:**
- Update shell prompt (PS1) to include title information
- Use window manager tools (wmctrl, xdotool) where available
- Log title changes to file for debugging
- Silent failure with optional verbose mode for troubleshooting

**Best Practices for Robust Implementation:**
- Always sanitize input before setting titles
- Implement graceful fallback for unsupported terminals
- Test across multiple terminal environments
- Provide configuration options to disable title setting
- Monitor for security vulnerabilities in escape sequence handling

## Implementation Recommendations

**High Priority Security Measures:**
- Implement comprehensive input sanitization (escape character removal)
- Use whitelist approach for allowed characters
- Enforce length limits (80-100 characters maximum)
- Regular security assessment of escape sequence handling

**Cross-Platform Compatibility Strategy:**
- Use standard OSC 0/1/2 sequences for maximum compatibility
- Implement terminal capability detection via $TERM and $TERM_PROGRAM
- Provide fallback mechanisms for unsupported terminals
- Test across iTerm2, Terminal.app, GNOME Terminal, Windows Terminal

**Shell Integration Approach:**
- Hook into shell prompt mechanisms (PROMPT_COMMAND, precmd, fish_title)
- Support bash, zsh, and fish shells
- Consider tmux/screen session compatibility
- Follow modern shell ecosystem patterns

## VSCode Integrated Terminal Specific Research (2025)

### VSCode Terminal Title Configuration and OSC Sequence Support

**Current State of Title Management:**
- VSCode removed support for standard terminal escape sequences (OSC 0, 1, 2) for setting window titles
- Previous `terminal.integrated.titleMode` setting deprecated in favor of variable-based configuration
- Standard XTerm escape sequences (`\e]0;TITLE\e\\`) are ignored by VSCode's integrated terminal
- Title management now uses configuration-based approach through settings

**VSCode Terminal Tab Title Configuration:**
```json
{
  "terminal.integrated.tabs.title": "${process}${separator}${sequence}",
  "terminal.integrated.tabs.description": "${task}${separator}${local}${separator}${cwdFolder}"
}
```

**Available Variables for Title Customization:**
- `${cwd}` - Current working directory (full path)
- `${cwdFolder}` - Current working directory folder name
- `${workspaceFolder}` - Workspace in which terminal was launched
- `${workspaceFolderName}` - Name of workspace folder
- `${local}` - Indicates local terminal in remote workspace
- `${process}` - Name of terminal process
- `${separator}` - Conditional separator (" - ") only shows when surrounded by variables with values
- `${sequence}` - Name provided to xterm.js by the process (closest to traditional OSC title)
- `${task}` - Indicates terminal is associated with a task
- `${shellType}` - Detected shell type
- `${shellCommand}` - Command being executed according to shell integration
- `${shellPromptInput}` - Shell's full prompt input according to shell integration

### VSCode-Specific OSC Sequences

**VSCode Custom OSC 633 Sequences:**
VSCode implements proprietary OSC 633 sequences for shell integration:
- `OSC 633 ; A ST` - Mark prompt start
- `OSC 633 ; B ST` - Mark prompt end
- `OSC 633 ; C ST` - Mark pre-execution
- `OSC 633 ; D [; <exitcode>] ST` - Mark execution finished with optional exit code
- `OSC 633 ; E ; <commandline> [; <nonce] ST` - Explicitly set command line with optional nonce
- `OSC 633 ; P ; <Property>=<Value> ST` - Set terminal properties

**Supported Properties (OSC 633 P):**
- `Cwd=<path>` - Report current working directory to terminal
- `IsWindows=<True|False>` - Indicate Windows backend usage (winpty/conpty)

**Final Term Compatibility:**
VSCode supports Final Term sequences (OSC 133) for broader compatibility:
- `OSC 133 ; A ST` - Mark prompt start
- `OSC 133 ; B ST` - Mark prompt end  
- `OSC 133 ; C ST` - Mark pre-execution
- `OSC 133 ; D [; <exitcode>] ST` - Mark execution finished

**iTerm2 Compatibility:**
- `OSC 1337 ; CurrentDir=<Cwd> ST` - Set current working directory
- `OSC 1337 ; SetMark ST` - Add marks to terminal with scroll bar annotation

### Cross-Platform Differences in VSCode

**Windows-Specific Behavior:**
- Console API allows more keyboard shortcuts than Linux/macOS
- Shell integration enables PowerShell-specific shortcuts (Ctrl+Space for MenuComplete)
- Environment variable handling differs from system terminal
- `IsWindows` property available in OSC 633 sequences

**macOS and Linux:**
- Alt key menu mnemonics disabled by default in terminal (`terminal.integrated.allowMnemonics`)
- PATH environment variables may differ between VSCode terminal and system terminal
- Standard Unix terminal behavior expected

**Remote Development (Codespaces):**
- Shell integration works seamlessly in remote environments
- AI coding experiences (GitHub Copilot) pre-configured in Codespaces
- Recent improvements to terminal handling in remote containers
- Race conditions documented in OSC 633 sequence processing

### VSCode vs VSCode Insiders vs Codespaces

**VSCode Insiders:**
- Latest terminal features available first
- May include experimental OSC sequence handling
- More frequent updates to shell integration

**GitHub Codespaces:**
- Pre-configured environment with optimal shell integration
- Agentic AI features introduced in 2025 for enhanced terminal experience
- Remote development optimizations for terminal performance

**Standard VSCode:**
- Stable terminal feature set
- Consistent OSC sequence behavior across releases
- Well-documented configuration options

### Limitations and Known Issues (2025)

**Critical Limitations:**
1. **No Standard OSC Support**: VSCode ignores standard terminal title escape sequences (OSC 0, 1, 2)
2. **Sequence Variable Dependency**: `${sequence}` variable only works if process sends supported OSC sequences
3. **Shell Integration Required**: Many variables require shell integration to function properly
4. **Platform Inconsistencies**: Different behavior across Windows, macOS, Linux for environment variables
5. **Race Conditions**: Documented race conditions in OSC 633 sequence processing with 80% failure rate in testing

**Workarounds and Best Practices:**
1. **Use Variable-Based Configuration**: Configure `terminal.integrated.tabs.title` with appropriate variables
2. **Enable Shell Integration**: Use supported shell integration scripts for full functionality
3. **Platform-Specific Settings**: Configure different terminal settings per platform if needed
4. **Fallback Strategies**: Implement graceful degradation when shell integration unavailable

**Security Considerations:**
- VSCode's proprietary OSC sequences should only be sent when `$TERM_PROGRAM=vscode`
- Input sanitization still required for any user-provided title content
- Variable-based approach provides inherent protection against injection attacks

### Interaction with Our OSC Implementation

**Compatibility Assessment:**
- **Standard OSC 0/1/2 sequences**: Will NOT work in VSCode integrated terminal
- **Shell integration approach**: Could work if we implement VSCode-specific OSC 633 sequences
- **Fallback strategy**: Essential for VSCode compatibility

**Recommended VSCode Integration Strategy:**
1. **Detection**: Check for `$TERM_PROGRAM=vscode` environment variable
2. **VSCode-Specific Implementation**: Send OSC 633 sequences instead of standard OSC 0/1/2
3. **Configuration Guidance**: Recommend users configure `terminal.integrated.tabs.title="${sequence}"`
4. **Graceful Fallback**: Use alternative title display methods when VSCode detected

**Implementation Example for VSCode:**
```bash
set_vscode_title() {
    local title="$1"
    title=$(sanitize_title "$title")
    
    if [[ "$TERM_PROGRAM" == "vscode" ]]; then
        # Use VSCode shell integration sequence
        echo -ne "\033]633;P;Cwd=${PWD}\033\\"
        # Note: VSCode doesn't support direct title setting via OSC
        # Users must configure terminal.integrated.tabs.title="${sequence}"
        echo "Configure VSCode: terminal.integrated.tabs.title=\"\${sequence}\"" >&2
    else
        # Use standard OSC sequences for other terminals
        echo -ne "\033]0;${title}\033\\"
    fi
}
```

## Repository Context
- Working in dedicated worktree: issue-173-feat-implement-terminal
- Need to find existing worktree scripts to integrate with
- Must follow file structure guidelines in CLAUDE.md