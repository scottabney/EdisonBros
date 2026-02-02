# OpenClaw - A simple file viewing and concatenation utility
# PowerShell version
# Usage: .\openclaw.ps1 [OPTIONS] [FILE...]

param(
    [Parameter(Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$Files,
    
    [Parameter(ValueFromPipeline=$true, DontShow=$true)]
    [object]$InputObject,
    
    [Alias('h')]
    [switch]$Help,
    
    [Alias('v')]
    [switch]$ShowVersion,
    
    [Alias('n')]
    [switch]$Number,
    
    [Alias('b')]
    [switch]$NumberNonBlank,
    
    [Alias('s')]
    [switch]$SqueezeBlank,
    
    [Alias('E')]
    [switch]$ShowEnds,
    
    [Alias('T')]
    [switch]$ShowTabs,
    
    [Alias('A')]
    [switch]$ShowAll
)

begin {
    $Script:VERSION = "1.0.0"
    
    # Function to display help
    function Show-Help {
        Write-Host ""
        Write-Host "OpenClaw " -NoNewline -ForegroundColor Cyan
        Write-Host "v$Script:VERSION" -ForegroundColor DarkGray
        Write-Host "File viewing and concatenation utility" -ForegroundColor Gray
        Write-Host ""
        Write-Host "USAGE" -ForegroundColor Cyan
        Write-Host "  .\openclaw.ps1 [OPTIONS] [FILE...]" -ForegroundColor White
        Write-Host ""
        Write-Host "OPTIONS" -ForegroundColor Cyan
        Write-Host "  -Help, -h          " -NoNewline -ForegroundColor White
        Write-Host "Show this help message" -ForegroundColor Gray
        Write-Host "  -ShowVersion, -v   " -NoNewline -ForegroundColor White
        Write-Host "Show version information" -ForegroundColor Gray
        Write-Host "  -Number, -n        " -NoNewline -ForegroundColor White
        Write-Host "Number all output lines" -ForegroundColor Gray
        Write-Host "  -NumberNonBlank, -b" -NoNewline -ForegroundColor White
        Write-Host "Number non-blank output lines only" -ForegroundColor Gray
        Write-Host "  -SqueezeBlank, -s  " -NoNewline -ForegroundColor White
        Write-Host "Suppress repeated empty lines" -ForegroundColor Gray
        Write-Host "  -ShowEnds, -E      " -NoNewline -ForegroundColor White
        Write-Host "Display $ at end of each line" -ForegroundColor Gray
        Write-Host "  -ShowTabs, -T      " -NoNewline -ForegroundColor White
        Write-Host "Display TAB characters as ^I" -ForegroundColor Gray
        Write-Host "  -ShowAll, -A       " -NoNewline -ForegroundColor White
        Write-Host "Equivalent to -ShowEnds -ShowTabs" -ForegroundColor Gray
        Write-Host ""
        Write-Host "EXAMPLES" -ForegroundColor Cyan
        Write-Host "  .\openclaw.ps1 file.txt" -ForegroundColor White
        Write-Host "    Display contents of file.txt" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "  .\openclaw.ps1 file1.txt file2.txt" -ForegroundColor White
        Write-Host "    Concatenate and display multiple files" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "  .\openclaw.ps1 -Number file.txt" -ForegroundColor White
        Write-Host "    Display file with line numbers" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "  Get-Content file.txt | .\openclaw.ps1" -ForegroundColor White
        Write-Host "    Read from pipeline/stdin" -ForegroundColor DarkGray
        Write-Host ""
    }

    # Function to display version
    function Show-VersionInfo {
        Write-Host "OpenClaw " -NoNewline -ForegroundColor Cyan
        Write-Host "version $Script:VERSION" -ForegroundColor White
    }

    # Handle help and version flags
    if ($Help) {
        Show-Help
        exit 0
    }

    if ($ShowVersion) {
        Show-VersionInfo
        exit 0
    }

    # Handle -ShowAll flag
    if ($ShowAll) {
        $ShowEnds = $true
        $ShowTabs = $true
    }

    # Initialize line counter
    $script:lineNumber = 1
    $script:previousBlank = $false
    $script:hasPipelineData = $false
    
    # Function to process a line
    function script:Process-Line {
        param([string]$Line)
        
        # Check if line is blank
        $isBlank = [string]::IsNullOrWhiteSpace($Line)
        
        # Handle squeeze blank
        if ($SqueezeBlank -and $isBlank -and $script:previousBlank) {
            return
        }
        
        # Handle line numbering
        if ($Number -or ($NumberNonBlank -and -not $isBlank)) {
            Write-Host -NoNewline ("{0,6}  " -f $script:lineNumber)
            $script:lineNumber++
        }
        
        # Process the line
        $outputLine = $Line
        
        # Show tabs
        if ($ShowTabs) {
            $outputLine = $outputLine -replace "`t", "^I"
        }
        
        # Output the line
        Write-Host -NoNewline $outputLine
        
        # Show ends
        if ($ShowEnds) {
            Write-Host -NoNewline '$'
        }
        
        Write-Host ""
        
        $script:previousBlank = $isBlank
    }
}

process {
    # Process pipeline input
    if ($null -ne $InputObject) {
        $script:hasPipelineData = $true
        foreach ($item in $InputObject) {
            if ($item -is [string]) {
                Process-Line $item
            } else {
                Process-Line $item.ToString()
            }
        }
    }
}

end {
    # Main processing logic for file arguments
    try {
        $hasFileArguments = ($null -ne $Files -and $Files.Count -gt 0)
        if ($hasFileArguments) {
            foreach ($file in $Files) {
                if ($file -eq "-") {
                    # Read from stdin (console)
                    Write-Host ""
                    Write-Host "→ " -NoNewline -ForegroundColor Cyan
                    Write-Host "Reading from stdin (press Ctrl+Z then Enter to end input)" -ForegroundColor Gray
                    Write-Host ""
                    while ($true) {
                        $line = [Console]::ReadLine()
                        if ($null -eq $line) { break }
                        Process-Line $line
                    }
                }
                elseif (-not (Test-Path $file)) {
                    Write-Error "openclaw.ps1: $file : No such file or directory"
                    exit 1
                }
                else {
                    # Read and process file
                    Get-Content $file | ForEach-Object {
                        Process-Line $_
                    }
                }
            }
        }
    }
    catch {
        Write-Error "An error occurred: $_"
        exit 1
    }
}
