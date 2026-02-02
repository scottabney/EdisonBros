# EdisonBros - OpenClaw

OpenClaw is a simple yet powerful file viewing and concatenation utility available for both Unix/Linux (Bash) and Windows (PowerShell) platforms.

## Features

OpenClaw provides the following features:

- **File Concatenation**: Display contents of one or multiple files
- **Line Numbering**: Number all lines or only non-blank lines
- **Blank Line Squeezing**: Suppress repeated empty lines
- **Special Character Display**: Show tabs and line endings
- **Pipeline Support**: Read from standard input or pipeline
- **Cross-Platform**: Works on Unix/Linux/macOS (Bash) and Windows (PowerShell)

## Installation

### Bash Version (Unix/Linux/macOS)

```bash
# Make the script executable
chmod +x openclaw.sh

# Optionally, move to a directory in your PATH
sudo cp openclaw.sh /usr/local/bin/openclaw
```

### PowerShell Version (Windows)

```powershell
# No installation needed - just run directly
# Or add to your PowerShell profile for easy access
```

## Usage

### Bash (openclaw.sh)

```bash
# Display help
./openclaw.sh --help

# Display a file
./openclaw.sh file.txt

# Display multiple files
./openclaw.sh file1.txt file2.txt

# Number all lines
./openclaw.sh -n file.txt

# Number only non-blank lines
./openclaw.sh -b file.txt

# Squeeze blank lines
./openclaw.sh -s file.txt

# Show line endings
./openclaw.sh -E file.txt

# Show tabs as ^I
./openclaw.sh -T file.txt

# Show all special characters
./openclaw.sh -A file.txt

# Read from stdin
cat file.txt | ./openclaw.sh
./openclaw.sh -
```

### PowerShell (openclaw.ps1)

```powershell
# Display help
.\openclaw.ps1 -Help

# Display a file
.\openclaw.ps1 file.txt

# Display multiple files
.\openclaw.ps1 file1.txt file2.txt

# Number all lines
.\openclaw.ps1 -Number file.txt

# Number only non-blank lines
.\openclaw.ps1 -NumberNonBlank file.txt

# Squeeze blank lines
.\openclaw.ps1 -SqueezeBlank file.txt

# Show line endings
.\openclaw.ps1 -ShowEnds file.txt

# Show tabs as ^I
.\openclaw.ps1 -ShowTabs file.txt

# Show all special characters
.\openclaw.ps1 -ShowAll file.txt

# Read from pipeline
Get-Content file.txt | .\openclaw.ps1
```

## Options

| Bash Option | PowerShell Option | Description |
|-------------|-------------------|-------------|
| -h, --help | -Help, -h | Show help message |
| -v, --version | -ShowVersion, -v | Show version information |
| -n, --number | -Number, -n | Number all output lines |
| -b, --number-nonblank | -NumberNonBlank, -b | Number non-blank output lines only |
| -s, --squeeze-blank | -SqueezeBlank, -s | Suppress repeated empty lines |
| -E, --show-ends | -ShowEnds, -E | Display $ at end of each line |
| -T, --show-tabs | -ShowTabs, -T | Display TAB characters as ^I |
| -A, --show-all | -ShowAll, -A | Equivalent to -ET (show tabs and ends) |

## Examples

### Basic File Display
```bash
# Bash
./openclaw.sh example.txt

# PowerShell
.\openclaw.ps1 example.txt
```

### Multiple Files
```bash
# Bash
./openclaw.sh file1.txt file2.txt file3.txt

# PowerShell
.\openclaw.ps1 file1.txt file2.txt file3.txt
```

### Numbered Lines
```bash
# Bash
./openclaw.sh -n document.txt

# PowerShell
.\openclaw.ps1 -Number document.txt
```

### Clean Up Multiple Blank Lines
```bash
# Bash
./openclaw.sh -s messy-file.txt

# PowerShell
.\openclaw.ps1 -SqueezeBlank messy-file.txt
```

## Feature Parity

Both the Bash and PowerShell versions provide identical functionality:

- ✅ File viewing and concatenation
- ✅ Line numbering (all lines)
- ✅ Line numbering (non-blank only)
- ✅ Squeeze blank lines
- ✅ Show line endings
- ✅ Show tabs
- ✅ Show all special characters
- ✅ Read from stdin/pipeline
- ✅ Multiple file support
- ✅ Error handling
- ✅ Help and version information

## Requirements

### Bash Version
- Bash 4.0 or higher
- Unix/Linux/macOS operating system

### PowerShell Version
- PowerShell 5.1 or higher
- Windows, Linux, or macOS with PowerShell Core

## License

This project is open source and available for educational purposes.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Version History

- **1.0.0** - Initial release with full feature parity between Bash and PowerShell versions
