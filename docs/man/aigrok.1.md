% AIGROK(1) AIGrok 1.0.0
% Your Name
% February 2024

# NAME

aigrok - AI-powered document analysis and processing tool

# SYNOPSIS

**aigrok** [*OPTIONS*] *COMMAND* [*ARGS*]

# DESCRIPTION

AIGrok is a command-line tool for processing and analyzing documents using AI models. It supports various document formats and provides multiple output formats for analysis results.

# COMMANDS

**process** [*OPTIONS*] *FILE*
: Process a document with AI analysis

**validate** [*OPTIONS*] *FILE*
: Validate document format and compatibility

**cache** *SUBCOMMAND*
: Manage the processing cache

**config** *SUBCOMMAND*
: Manage AIGrok configuration

# OPTIONS

**-c**, **--config**=*FILE*
: Path to configuration file

**-v**, **--verbose**
: Enable verbose output

**-q**, **--quiet**
: Suppress all output except errors

**--log-level**=*LEVEL*
: Set logging level (debug/info/warn/error)

**--version**
: Show version information

**--help**
: Show help message

# PROCESS COMMAND OPTIONS

**-m**, **--model**=*NAME*
: AI model to use (default: llama2-vision)

**-p**, **--prompt**=*TEXT*
: Custom processing prompt

**-f**, **--format**=*FORMAT*
: Output format (text/json/markdown)

**-o**, **--output**=*FILE*
: Output file path

**--cache**
: Enable result caching

**--timeout**=*SECONDS*
: Processing timeout (default: 30)

# ENVIRONMENT

**AIGROK_CONFIG**
: Configuration file path

**AIGROK_MODEL**
: Default model name

**AIGROK_CACHE_DIR**
: Cache directory location

**AIGROK_LOG_LEVEL**
: Logging level

# FILES

*/etc/aigrok/config.yaml*
: System-wide configuration file

*~/.config/aigrok/config.yaml*
: User configuration file

*~/.cache/aigrok/*
: Cache directory

*~/.local/share/aigrok/aigrok.log*
: Log file

# EXIT STATUS

**0**
: Success

**1**
: General error

**2**
: Invalid arguments

**3**
: Configuration error

**4**
: Processing error

**5**
: Timeout error

# EXAMPLES

Process a PDF file:

```bash
aigrok process document.pdf
```

Process with custom prompt:

```bash
aigrok process --prompt "Extract main topics" document.pdf
```

Process multiple files:

```bash
aigrok process --output-dir results/ *.pdf
```

# BUGS

Report bugs at <https://github.com/yourusername/aigrok/issues>

# COPYRIGHT

Copyright © 2024 Your Name. License MIT <https://opensource.org/licenses/MIT>.

# SEE ALSO

**ollama**(1), **pdf2text**(1)

Full documentation at: <https://github.com/yourusername/aigrok>
