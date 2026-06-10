# ============================================================
#  WinGet Discovery Script  (v3.5 / app v0.4.4)
#  Identifies all applications with available updates on this endpoint.
#  Designed to be called by Forescout HPS via SecureConnector.
#
#  v3.5 change: ROOT-CAUSE fix for long-named packages (e.g. the
#  Microsoft.VCRedist.* family) being mis-parsed or dropped.
#
#  What was actually happening:
#    When winget's table is captured by a script (non-interactive,
#    Run Interactive = No) rather than shown in a console, winget
#    truncates long Name values with an ellipsis "..." (U+2026). In
#    the captured stream that character was being decoded with the
#    wrong code page and turned into multi-character mojibake junk
#    (it showed up as "GG-a" / box-drawing garbage). That junk is
#    LONGER than the single ellipsis winget intended, so it shoved
#    every column on those rows a couple characters to the right of
#    where the header said they'd be.
#      - v3.3 (fixed-width slicing) clipped the last char of the
#        longest Id -> "Microsoft.VCRedist.2015+.x86" rendered as
#        "...x8 (6 ... -> ...)".
#      - v3.4 (naive whitespace split) read the leading junk token
#        as the Id, found it wasn't a valid Id, and SKIPPED the whole
#        row -> VCRedist disappeared entirely on every endpoint whose
#        name was long enough to be truncated.
#    Only the longest-named packages are affected because only they
#    get truncated in the first place.
#
#  Two-part fix:
#    1. Force UTF-8 output encoding before calling winget, so the
#       ellipsis decodes correctly and columns line up. (Wrapped in
#       try/catch: in some service contexts there is no console to
#       set encoding on; if that throws, part 2 still saves us.)
#    2. Parse each row by LOCATING the real package Id (the first
#       ASCII, dotted "Publisher.Package" token) instead of trusting
#       a fixed character offset, then taking the next two tokens as
#       the current/available versions. If no Id can be located on a
#       row, FALL BACK to the v3.3 fixed-width method so the row is
#       still emitted. Net effect: a row can never silently vanish
#       again -- worst case we reproduce old visible-but-clipped
#       behaviour, which still matches family-name policy conditions.
#
#  ---- prior change history -------------------------------------
#  v3.3: consolidated output into a single multi-line field
#        WINGET_UPDATES_APPS ("PackageId (current -> available)"),
#        which renders as a vertical list in Forescout host details
#        and stays substring-searchable by package ID.
#  v3.1: added Clean-WingetField to strip non-ASCII spinner artifacts
#        from parsed package IDs/versions.
#  v3:   reversed winget.exe lookup order (real binary first, per-user
#        execution aliases last) to avoid the SecureConnector
#        "file cannot be accessed by the system" alias error.
#
#  Output (parseable by Forescout):
#    WINGET_UPDATES_COUNT=<integer>
#    WINGET_UPDATES_APPS=<newline-separated "PackageId (cur -> avail)">
#
#  Exit codes:
#    0 = success (even if 0 updates available)
#    1 = winget.exe could not be located on this machine
# ============================================================

function Find-WinGet {
    # --- Strategy 1: System-wide WindowsApps folder (the REAL binary) ---
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
    $allUsersPath = "C:\Program Files\WindowsApps\Microsoft.DesktopAppInstaller_*\winget.exe"
    try {
        $found = Get-ChildItem $allUsersPath -ErrorAction SilentlyContinue |
                 Select-Object -First 1 -ExpandProperty FullName
        if ($found) {
            return $found
        }
    } catch { }

    # --- Strategy 4: PATH lookup (last resort, may return an alias) ---
    $cmd = Get-Command winget -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) {
        return $cmd.Source
    }

    return $null
}

# --- Helper: scrub junk characters from parsed values ---
# Strips leading/trailing chars outside the valid package-ID/version set
# (alphanumerics, dot, underscore, hyphen, plus). This also cleans the
# mojibake-ellipsis fragments off the front of a token when they appear.
function Clean-WingetField {
    param([string]$Value)
    if ([string]::IsNullOrEmpty($Value)) { return $Value }
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
# Force UTF-8 so winget's ellipsis (used when it truncates long Name values)
# decodes correctly instead of turning into multi-char mojibake that shifts
# the columns. Setting the console encoding can throw in contexts with no
# console attached; if it does, the encoding-independent parser in Step 3
# still recovers every row.
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
try { $OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

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

# Column start positions from the header line. $idCol is the primary anchor
# (the Name column, the only space-containing field, lives to its left). The
# other three are used only by the fixed-width FALLBACK path below.
$headerLine   = $lines[$headerIndex]
$idCol        = $headerLine.IndexOf("Id")
$versionCol   = $headerLine.IndexOf("Version")
$availableCol = $headerLine.IndexOf("Available")
$sourceCol    = $headerLine.IndexOf("Source")

# A real winget package Id is ASCII, starts alphanumeric, and contains at
# least one dot (Publisher.Package). That dot requirement is what lets us
# tell a genuine Id apart from mojibake junk (non-ASCII) and from plain
# name words that may bleed into view (no dot).
$idPattern = '^[A-Za-z0-9][A-Za-z0-9._+\-]*\.[A-Za-z0-9._+\-]+$'

# Data rows start two lines after the header (header + separator + data)
$dataStart = $headerIndex + 2

$packageIds     = @()
$packageDetails = @()

for ($i = $dataStart; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]

    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    if ($line -match '^\d+ upgrades? available') { break }
    if ($line -match '^The following packages') { break }
    if ($line.Length -le $idCol) { continue }

    $id = $null; $current = $null; $available = $null

    # --- Primary: locate the real Id token from $idCol onward -----------
    # Everything from $idCol to end of line is whitespace-separated tokens
    # (the Name column sits to the left of $idCol). On a clean row the first
    # token is the Id. On a truncated/mojibake row the leading token(s) are
    # junk fragments; we skip them and lock onto the first token that is a
    # valid winget Id. The two tokens after it are current/available.
    $rest   = $line.Substring($idCol).Trim()
    $tokens = $rest -split '\s+'
    for ($t = 0; $t -lt $tokens.Count; $t++) {
        $candidate = Clean-WingetField $tokens[$t]
        if (($candidate -match $idPattern) -and (($t + 2) -lt $tokens.Count)) {
            $id        = $candidate
            $current   = Clean-WingetField $tokens[$t + 1]
            $available = Clean-WingetField $tokens[$t + 2]
            break
        }
    }

    # --- Fallback: original v3.3 fixed-width slicing --------------------
    # If we couldn't lock onto an Id (some unforeseen layout), reproduce the
    # old column-position behaviour so the row is STILL emitted rather than
    # dropped. Visible-but-clipped beats invisible, and family-name policy
    # conditions still match.
    if ([string]::IsNullOrWhiteSpace($id)) {
        if ($line.Length -ge $sourceCol) {
            try {
                $id        = Clean-WingetField ($line.Substring($idCol,        $versionCol   - $idCol).Trim())
                $current   = Clean-WingetField ($line.Substring($versionCol,   $availableCol - $versionCol).Trim())
                $available = Clean-WingetField ($line.Substring($availableCol, $sourceCol    - $availableCol).Trim())
            } catch { }
        }
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
$appsLines = @()
for ($i = 0; $i -lt $packageIds.Count; $i++) {
    $detail = $packageDetails[$i]
    $parts = $detail -split '\|'
    if ($parts.Count -eq 3) {
        $appsLines += '{0} ({1} -> {2})' -f $parts[0], $parts[1], $parts[2]
    } else {
        $appsLines += $packageIds[$i]
    }
}

Write-Output "WINGET_UPDATES_COUNT=$count"
Write-Output "WINGET_UPDATES_APPS=$($appsLines -join "`n")"

exit 0
