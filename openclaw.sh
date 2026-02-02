#!/bin/bash

# OpenClaw - A simple file viewing and concatenation utility
# Usage: openclaw.sh [OPTIONS] [FILE...]

VERSION="1.0.0"

# Function to display help
show_help() {
    cat << EOF

OpenClaw v${VERSION}
File viewing and concatenation utility

USAGE
  openclaw.sh [OPTIONS] [FILE...]

OPTIONS
  -h, --help          Show this help message
  -v, --version       Show version information
  -n, --number        Number all output lines
  -b, --number-nonblank Number non-blank output lines only
  -s, --squeeze-blank Suppress repeated empty lines
  -E, --show-ends     Display $ at end of each line
  -T, --show-tabs     Display TAB characters as ^I
  -A, --show-all      Equivalent to -ET

EXAMPLES
  openclaw.sh file.txt
    Display contents of file.txt

  openclaw.sh file1.txt file2.txt
    Concatenate and display multiple files

  openclaw.sh -n file.txt
    Display file with line numbers

  openclaw.sh -
    Read from standard input

EOF
}

# Function to display version
show_version() {
    echo "OpenClaw version ${VERSION}"
}

# Initialize options
number_lines=false
number_nonblank=false
squeeze_blank=false
show_ends=false
show_tabs=false
line_number=1
previous_blank=false

# Parse command line arguments
files=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            show_version
            exit 0
            ;;
        -n|--number)
            number_lines=true
            shift
            ;;
        -b|--number-nonblank)
            number_nonblank=true
            shift
            ;;
        -s|--squeeze-blank)
            squeeze_blank=true
            shift
            ;;
        -E|--show-ends)
            show_ends=true
            shift
            ;;
        -T|--show-tabs)
            show_tabs=true
            shift
            ;;
        -A|--show-all)
            show_ends=true
            show_tabs=true
            shift
            ;;
        -*)
            echo "Error: Unknown option $1" >&2
            echo "Try 'openclaw.sh --help' for more information." >&2
            exit 1
            ;;
        *)
            files+=("$1")
            shift
            ;;
    esac
done

# Function to process a line
process_line() {
    local line="$1"
    local is_blank=false
    
    # Check if line is blank
    if [[ -z "$line" ]]; then
        is_blank=true
    fi
    
    # Handle squeeze blank
    if $squeeze_blank && $is_blank && $previous_blank; then
        return
    fi
    
    # Handle line numbering
    if $number_lines || ($number_nonblank && ! $is_blank); then
        printf "%6d  " "$line_number"
        ((line_number++))
    fi
    
    # Show tabs
    if $show_tabs; then
        line="${line//$'\t'/^I}"
    fi
    
    # Show line
    echo -n "$line"
    
    # Show ends
    if $show_ends; then
        echo -n '$'
    fi
    
    echo
    
    previous_blank=$is_blank
}

# Function to process a file or stdin
process_input() {
    while IFS= read -r line || [[ -n "$line" ]]; do
        process_line "$line"
    done
}

# If no files specified, read from stdin
if [[ ${#files[@]} -eq 0 ]]; then
    process_input
else
    # Process each file
    for file in "${files[@]}"; do
        if [[ "$file" == "-" ]]; then
            # Read from stdin
            process_input
        elif [[ ! -f "$file" ]]; then
            echo "openclaw.sh: $file: No such file or directory" >&2
            exit 1
        else
            # Read from file
            process_input < "$file"
        fi
    done
fi
