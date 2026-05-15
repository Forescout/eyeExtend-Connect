# ============================================================
#  WinGet Inventory Script  (v1)
#  Searches the installed-package list on this endpoint for entries
#  matching an admin-supplied search term, and returns the matching
#  WinGet package IDs.
#
#  PURPOSE: this is the "find the string" helper. When an admin wants
#  to remove software they haven't removed before (i.e., not one of
#  the four pre-built uninstall templates), they need the exact
#  WinGet package ID to put in the Custom uninstall template. This
#  script bridges the gap between "I know I want to remove iTunes"
#  and "I need to tell WinGet 'Apple.iTunes' to uninstall it."
#
#  Designed to be called by a one-off Forescout HPS policy template
#  that the admin enables temporarily on a single test host, reads
#  the result from host details, then disables.
# ============================================================
#
#  USAGE (from a Forescout Run Script action's Command field):
#    WingetInventory.ps1 -SearchTerm "iTunes"
#    WingetInventory.ps1 -SearchTerm "shockwave"
#    WingetInventory.ps1 -SearchTerm "adobe"   (broad - will return all Adobe products)
#
#  Search behavior:
#    - Case-insensitive substring match
#    - Matches against BOTH the Name column AND the Id column from
#      `winget list` output. So "iTunes" finds entries named "iTunes"
#      OR with IDs containing "itunes" (e.g., "Apple.iTunes")
#    - No cap on results. If your search returns 50 matches, that's
#      a sign to be more specific (try ".NET" instead of "Microsoft")
#    - Returns clean WinGet IDs AND GUID-style IDs. If iTunes only
#      shows up as a GUID, that's what you get back; if there's a
#      clean ID, you get that. Either is usable in winget uninstall
#      (though the Custom uninstall template's regex validator only
#      accepts the clean ID format)
#
#  Output (parseable by Forescout, one line per match):
#    WINGET_INVENTORY_SEARCH=<search term>
#    WINGET_INVENTORY_COUNT=<integer>
#    WINGET_INVENTORY_MATCH=<package ID>     (one line per match)
#    WINGET_INVENTORY_MATCH=<package ID>
#    ...
#
#  When zero matches:
#    WINGET_INVENTORY_SEARCH=<search term>
#    WINGET_INVENTORY_COUNT=0
#    WINGET_INVENTORY_MESSAGE=No installed packages match the search term
#
#  Exit codes:
#    0 = success (even if 0 matches found)
#    1 = winget.exe could not be located on this machine
#    2 = unexpected exception during enumeration
# ============================================================

param(
    [Parameter(Mandatory=$true, HelpMessage="Substring to search for in installed package names/IDs. Case-insensitive. Example: 'iTunes' or 'shockwave'.")]
    [ValidateNotNullOrEmpty()]
    [string]$SearchTerm
)

# ---- Locate winget.exe (same strategy ordering as discovery and update scripts) ----
function Find-WinGet {
    # Strategy 1: Real binary in WindowsApps (works in SYSTEM/service contexts)
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

    # Strategy 2: AppX package lookup
    try {
        $pkg = Get-AppxPackage -Name Microsoft.DesktopAppInstaller -ErrorAction SilentlyContinue
        if ($pkg -and $pkg.InstallLocation) {
            $exePath = Join-Path $pkg.InstallLocation "winget.exe"
            if (Test-Path $exePath -ErrorAction SilentlyContinue) {
                return $exePath
            }
        }
    } catch { }

    # Strategy 3: AllUsers WindowsApps wildcard
    try {
        $found = Get-ChildItem "C:\Program Files\WindowsApps\Microsoft.DesktopAppInstaller_*\winget.exe" -ErrorAction SilentlyContinue |
                 Select-Object -First 1 -ExpandProperty FullName
        if ($found) {
            return $found
        }
    } catch { }

    # Strategy 4: PATH lookup (last resort, may return an alias)
    $cmd = Get-Command winget -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) {
        return $cmd.Source
    }

    return $null
}

# ---- Helper: strip junk leading/trailing characters (same as WingetDiscover_v3) ----
# WinGet's progress spinners and unicode artifacts sometimes bleed
# into the first column of the first parsed data row. Strip anything
# outside the valid character set from start/end.
function Clean-WingetField {
    param([string]$Value)
    if ([string]::IsNullOrEmpty($Value)) { return $Value }
    return ($Value -replace '^[^A-Za-z0-9{]+', '') -replace '[^A-Za-z0-9\._\-+}]+$', ''
}

# ---- Step 1: Locate winget ----
$winget = Find-WinGet
if ($null -eq $winget) {
    Write-Output "WINGET_INVENTORY_SEARCH=$SearchTerm"
    Write-Output "WINGET_INVENTORY_COUNT=-1"
    Write-Output "WINGET_INVENTORY_MESSAGE=winget.exe not found on this endpoint"
    exit 1
}

# ---- Step 2: Enumerate installed packages ----
try {
    $rawOutput = & "$winget" list --accept-source-agreements 2>&1 | Out-String
} catch {
    Write-Output "WINGET_INVENTORY_SEARCH=$SearchTerm"
    Write-Output "WINGET_INVENTORY_COUNT=-1"
    Write-Output "WINGET_INVENTORY_MESSAGE=Exception during enumeration: $($_.Exception.Message)"
    exit 2
}

$lines = $rawOutput -split "`r?`n"

# Find the header line so we know where the data starts and where the columns are
$headerIndex = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\s*Name\s+Id\s+Version') {
        $headerIndex = $i
        break
    }
}

if ($headerIndex -eq -1) {
    # No header means winget produced no list output - unusual, but possible on
    # a system with zero installed winget-recognized packages.
    Write-Output "WINGET_INVENTORY_SEARCH=$SearchTerm"
    Write-Output "WINGET_INVENTORY_COUNT=0"
    Write-Output "WINGET_INVENTORY_MESSAGE=No installed packages match the search term"
    exit 0
}

$headerLine = $lines[$headerIndex]
$idCol      = $headerLine.IndexOf("Id")
$versionCol = $headerLine.IndexOf("Version")

# Data rows start two lines after the header (header + separator + data)
$dataStart = $headerIndex + 2

# ---- Step 3: Parse + search ----
$matches = @()
$searchLower = $SearchTerm.ToLower()

for ($i = $dataStart; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]

    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    if ($line -match '^\d+ upgrades? available') { break }
    if ($line.Length -lt $versionCol) { continue }

    try {
        # Name column runs from char 0 to where Id starts
        $name = $line.Substring(0, $idCol).Trim()
        # Id column runs from where Id starts to where Version starts
        $id   = Clean-WingetField ($line.Substring($idCol, $versionCol - $idCol).Trim())
    } catch {
        continue
    }

    if ([string]::IsNullOrWhiteSpace($id)) { continue }
    if ($id -match '^-+$') { continue }

    # Case-insensitive substring match against BOTH name and ID.
    # Matching against name helps when an admin searches for the
    # human-readable name (e.g., "iTunes") and the WinGet ID looks
    # different (e.g., "Apple.iTunes" — matches via ID — or for a
    # GUID-only package where ID is "{8C24...}" but Name is "iTunes").
    if ($id.ToLower().Contains($searchLower) -or $name.ToLower().Contains($searchLower)) {
        $matches += $id
    }
}

# Dedupe in case the same ID appeared twice (shouldn't, but be safe)
$matches = $matches | Sort-Object -Unique

# ---- Step 4: Emit results ----
Write-Output "WINGET_INVENTORY_SEARCH=$SearchTerm"
Write-Output "WINGET_INVENTORY_COUNT=$($matches.Count)"

if ($matches.Count -eq 0) {
    Write-Output "WINGET_INVENTORY_MESSAGE=No installed packages match the search term"
} else {
    foreach ($id in $matches) {
        Write-Output "WINGET_INVENTORY_MATCH=$id"
    }
}

exit 0
