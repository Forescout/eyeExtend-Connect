# ============================================================
#  WinGet Discovery Script  (v3.3 / app v0.4.4)
#  Identifies all applications with available updates on this endpoint.
#  Designed to be called by Forescout HPS via SecureConnector.
#
#  v3.3 change: consolidated output. The two redundant fields
#  WINGET_UPDATES_LIST and WINGET_UPDATES_DETAIL are replaced by
#  ONE multi-line field WINGET_UPDATES_APPS, with one app per line
#  in the format: "PackageId (current -> available)". This renders
#  as a vertical list in Forescout's host details view (verified in
#  testing) and remains substring-searchable by package ID, so all
#  existing 'contains <PackageId>' policy conditions still match.
#
#  v3.1 change: added Clean-WingetField helper to strip non-ASCII
#  junk characters (winget progress-spinner artifacts) from parsed
#  package IDs and versions. Without this, the first parsed row's
#  package ID was getting a leading 'ª' or similar garbage char
#  prepended, which made copy-paste of package IDs from the host
#  details view in Forescout produce strings that didn't match.
#
#  v3 change: strategy order reversed. Real winget.exe binary is
#  now tried FIRST, before the per-user execution alias paths.
#  Reason: execution aliases at %LOCALAPPDATA%\Microsoft\WindowsApps\
#  are reparse points that only work in interactive sessions. When
#  SecureConnector runs the script non-interactively, invoking the
#  alias produces the error: "The file cannot be accessed by the
#  system." Targeting the real binary in C:\Program Files\WindowsApps\
#  avoids this entirely.
#
#  Output (parseable by Forescout):
#    WINGET_UPDATES_COUNT=<integer>
#    WINGET_UPDATES_APPS=<newline-separated "PackageId (cur -> avail)">
#
#
#  Exit codes:
#    0 = success (even if 0 updates available)
#    1 = winget.exe could not be located on this machine
# ============================================================

function Find-WinGet {
    # --- Strategy 1: System-wide WindowsApps folder (the REAL binary) ---
    # This is the actual winget.exe executable, not an execution alias.
    # Works reliably for SYSTEM and service contexts (SecureConnector).
    # The wildcard handles version variations in the package folder name.
    try {
        $sysFolder = Get-ChildItem "C:\Program Files\WindowsApps\Microsoft.DesktopAppInstaller_*_x64__8wekyb3d8bbwe" -ErrorAction SilentlyContinue |
                     Sort-Object Name -Descending |
                     Select-Object -First 1 -ExpandProperty FullName
        if ($sysFolder) {
            $exePath = Join-Path $sysFolder "winget.exe"
            if (Test-Path $exePath -ErrorAction SilentlyContinue) {
                return $exePath
            }
        }
    } catch { }

    # --- Strategy 2: AppX package lookup ---
    # Uses Windows itself to tell us where the App Installer package lives.
    # Slightly slower but very reliable. Also returns the real binary path,
    # not an alias.
    try {
        $pkg = Get-AppxPackage -Name Microsoft.DesktopAppInstaller -ErrorAction SilentlyContinue
        if ($pkg -and $pkg.InstallLocation) {
            $exePath = Join-Path $pkg.InstallLocation "winget.exe"
            if (Test-Path $exePath -ErrorAction SilentlyContinue) {
                return $exePath
            }
        }
    } catch { }

    # --- Strategy 3: AllUsers WindowsApps execution alias ---
    # The system-wide execution alias. Works in more contexts than the
    # per-user alias but may still have issues in some non-interactive runs.
    $allUsersPath = "C:\Program Files\WindowsApps\Microsoft.DesktopAppInstaller_*\winget.exe"
    try {
        $found = Get-ChildItem $allUsersPath -ErrorAction SilentlyContinue |
                 Select-Object -First 1 -ExpandProperty FullName
        if ($found) {
            return $found
        }
    } catch { }

    # --- Strategy 4: PATH lookup (last resort, may return an alias) ---
    # Only used if nothing else worked. Documented to potentially return
    # an execution alias that fails in non-interactive contexts. If this
    # is the only path that resolves, we may still hit the alias bug,
    # but at that point we've exhausted real options.
    $cmd = Get-Command winget -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) {
        return $cmd.Source
    }

    return $null
}

# --- Helper: scrub junk characters from parsed values ---
# WinGet's progress spinners and unicode artifacts sometimes bleed
# into the first column of the first parsed data row, producing
# leading garbage characters like 'ª' on the very first package ID.
# This strips any leading/trailing chars that aren't in the valid
# character set for package IDs/versions: alphanumerics, dot,
# underscore, hyphen, plus. Whitespace was already removed by .Trim().
function Clean-WingetField {
    param([string]$Value)
    if ([string]::IsNullOrEmpty($Value)) { return $Value }
    # Strip anything outside the valid set from start and end.
    # The valid set matches WingetUpdate_v3.ps1's package ID validator.
    return ($Value -replace '^[^A-Za-z0-9]+', '') -replace '[^A-Za-z0-9\._\-+]+$', ''
}

# --- Step 1: Locate winget.exe ---
$winget = Find-WinGet

if ($null -eq $winget) {
    Write-Output "WINGET_UPDATES_COUNT=-1"
    Write-Output "WINGET_UPDATES_APPS=ERROR_WINGET_NOT_FOUND"
    exit 1
}

# --- Step 2: Ask winget what's out of date ---
$rawOutput = & "$winget" upgrade --include-unknown --accept-source-agreements 2>&1 | Out-String

# --- Step 3: Parse winget's output ---
$lines = $rawOutput -split "`r?`n"

# Find the header line containing the column names
$headerIndex = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\s*Name\s+Id\s+Version\s+Available') {
        $headerIndex = $i
        break
    }
}

# No header found = either no updates available, or unexpected output
if ($headerIndex -eq -1) {
    Write-Output "WINGET_UPDATES_COUNT=0"
    Write-Output "WINGET_UPDATES_APPS="
    exit 0
}

# Determine column positions from the header line
$headerLine = $lines[$headerIndex]
$idCol        = $headerLine.IndexOf("Id")
$versionCol   = $headerLine.IndexOf("Version")
$availableCol = $headerLine.IndexOf("Available")
$sourceCol    = $headerLine.IndexOf("Source")

# Data rows start two lines after the header (header + separator + data)
$dataStart = $headerIndex + 2

$packageIds     = @()
$packageDetails = @()

for ($i = $dataStart; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]

    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    if ($line -match '^\d+ upgrades? available') { break }
    if ($line -match '^The following packages') { break }
    if ($line.Length -lt $sourceCol) { continue }

    try {
        $id        = Clean-WingetField ($line.Substring($idCol,        $versionCol   - $idCol).Trim())
        $current   = Clean-WingetField ($line.Substring($versionCol,   $availableCol - $versionCol).Trim())
        $available = Clean-WingetField ($line.Substring($availableCol, $sourceCol    - $availableCol).Trim())
    } catch {
        continue
    }

    if ([string]::IsNullOrWhiteSpace($id)) { continue }
    if ($id -match '^-+$') { continue }

    $packageIds     += $id
    $packageDetails += "$id|$current|$available"
}

# --- Step 4: Emit results in Forescout-parseable format ---
$count = $packageIds.Count

# Build the consolidated "apps" output: one line per package, format:
#   PackageId (current -> available)
# Example: "Google.Chrome (118.0 -> 120.0)"
$appsLines = @()
for ($i = 0; $i -lt $packageIds.Count; $i++) {
    $detail = $packageDetails[$i]
    $parts = $detail -split '\|'
    if ($parts.Count -eq 3) {
        $appsLines += '{0} ({1} -> {2})' -f $parts[0], $parts[1], $parts[2]
    } else {
        # Fallback if somehow the detail doesn't parse - just emit the ID
        $appsLines += $packageIds[$i]
    }
}

Write-Output "WINGET_UPDATES_COUNT=$count"
Write-Output "WINGET_UPDATES_APPS=$($appsLines -join "`n")"

exit 0
