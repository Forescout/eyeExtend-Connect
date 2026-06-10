# ============================================================
#  WinGet Update Script  (v3.1)
#  Performs a silent WinGet update for a single, explicitly-named
#  package OR a bounded family of packages (prefix wildcard mode).
#
#  Designed to be called by Forescout HPS "Run Script on Windows"
#  actions configured by per-application policy templates.
# ============================================================
#
#  v3.1 change: fixed wildcard mode silently skipping long-named
#  packages (e.g. Microsoft.VCRedist.2015+.x86/.x64 were not being
#  updated, while the shorter Microsoft.VCRedist.2013.x86 was).
#
#  Root cause: Get-InstalledPackagesByPrefix enumerated via
#  `winget list`, which returns hundreds of rows. winget narrows the
#  Id column to fit, truncating long IDs with an ellipsis. When that
#  ellipsis is captured non-interactively it becomes multi-character
#  mojibake junk, so the truncated ID failed the ASCII sanity check
#  and was dropped from the match list -> never upgraded. Only the
#  longest IDs were affected, which is why 2013 worked but 2015+ did
#  not.
#
#  Fix (mirrors WingetDiscover_v3.ps1 v3.5):
#    * Enumerate via `winget upgrade --include-unknown` instead of
#      `winget list`. It returns only out-of-date packages (few rows),
#      so the Id column stays wide and long IDs are not truncated.
#      This is also semantically correct: wildcard mode only needs the
#      packages that actually have an upgrade available. (This is what
#      the older v2 script did, and why; the v3 rewrite regressed it.)
#    * Force UTF-8 output encoding so the ellipsis decodes cleanly.
#    * Locate the real Id token (first ASCII, dotted Publisher.Package
#      token) rather than trusting a fixed column offset, with a
#      fixed-width fallback so a row can't be silently lost.
#
#  The DESIGN GUARANTEE below is UNCHANGED: still per-package only,
#  still one `winget upgrade --id <exact>` per matched package, still
#  never `--all`. Only HOW the matched list is discovered changed.
# ============================================================
#
#  ⚠️ DESIGN GUARANTEE — DO NOT BREAK THIS ⚠️
#
#  This script will ONLY upgrade packages whose IDs were explicitly
#  named by the admin via -PackageId. It will NEVER:
#    * Run `winget upgrade --all`
#    * Patch packages outside the admin's stated scope
#    * Allow leading wildcards or middle wildcards
#
#  Why this matters: Forescout admins create per-application policy
#  templates that explicitly enable patching for SPECIFIC apps
#  (Chrome, Acrobat family, etc.) on SPECIFIC endpoints. Enabling
#  the Chrome template = consent to update Chrome. Enabling the
#  Adobe.Acrobat.* template = consent to update all Acrobat
#  variants. Not enabling the Office template = explicit refusal to
#  touch Office. A script that "helpfully" updates everything else
#  while it's there would trample that intent and could break
#  critical workflows during business hours.
#
#  PACKAGE ID MODES
#  ----------------
#  Two modes are supported, both safe:
#
#  1. EXACT MATCH (recommended default)
#       -PackageId "Google.Chrome"
#     Updates exactly one package by its full ID. Most policy
#     templates use this mode.
#
#  2. PREFIX WILDCARD (for app families)
#       -PackageId "Adobe.Acrobat.*"
#     Updates every installed package whose ID starts with the
#     given prefix. The trailing ".*" is REQUIRED to opt into
#     wildcard mode. The prefix must be at least one character.
#
#     The script enumerates matching packages via `winget list`,
#     then loops with one `winget upgrade --id <exact>` call per
#     package. It NEVER calls `winget upgrade --all`. It NEVER
#     touches anything that doesn't already match the prefix
#     and isn't already installed on the endpoint.
#
#     Common wildcards customers may use:
#       Adobe.Acrobat.*       (Reader 32, Reader 64, Pro, DC, etc.)
#       Microsoft.VCRedist.*  (all VC++ Redistributables)
#       Adobe.Photoshop.*     (Photoshop CC, Photoshop 2024, etc.)
#
#     Wildcards are bounded: ONLY trailing ".*", ONLY when
#     preceded by at least one valid character. The validator
#     rejects:  *   .*   *Chrome   Adobe.*.Reader   Adobe**
#
#  ENFORCEMENT LAYERS (defense in depth)
#  -------------------------------------
#  Per-package safety is enforced at three levels:
#    1. POLICY: Each per-app policy template only matches endpoints
#       whose WinGet Updates - Package IDs property contains the
#       intended substring (e.g. "Google.Chrome" or "Adobe.Acrobat").
#    2. COMMAND LINE: The policy template's action passes the exact
#       package ID (or bounded wildcard) hardcoded by the admin.
#    3. THIS SCRIPT: The -PackageId parameter is Mandatory, typed
#       [string] (not array), regex-validated, and the upgrade
#       command always uses --id <specific> (never --all).
#
#  If you find yourself "improving" this script to accept arbitrary
#  patterns or update everything, STOP. The bounded prefix wildcard
#  is the maximum flexibility this script should ever offer. For
#  additional scope, the admin should create additional policies
#  with additional -PackageId values.
# ============================================================
#
#  USAGE (from a Forescout Run Script action's "Command or Script" field):
#    WingetUpdate.ps1 -PackageId "Google.Chrome"
#    WingetUpdate.ps1 -PackageId "Adobe.Acrobat.*"
#
#  Output (parseable by Forescout):
#    WINGET_UPDATE_RESULT=<SUCCESS|PARTIAL|FAILED|NOT_FOUND|ERROR>
#    WINGET_UPDATE_PACKAGE=<original -PackageId argument>
#    WINGET_UPDATE_MATCHED=<comma-separated list of package IDs found>
#    WINGET_UPDATE_SUCCEEDED=<count of packages updated successfully>
#    WINGET_UPDATE_FAILED=<count of packages that failed>
#    WINGET_UPDATE_EXIT_CODE=<integer>   (only on FAILED/ERROR/PARTIAL)
#    WINGET_UPDATE_MESSAGE=<single-line summary>
#
#  Exit codes:
#    0 = all updates succeeded (or no matching packages installed)
#    1 = winget.exe could not be located on this machine
#    2 = one or more updates failed
#    3 = unexpected exception during update
#
#  Naming convention note: this script uses the same Find-WinGet
#  strategy ordering as WingetDiscover_v3.ps1 (real binary first,
#  aliases last) to avoid the SecureConnector execution alias issue
#  where per-user reparse points throw "The file cannot be accessed
#  by the system" when invoked non-interactively.
# ============================================================

param(
    [Parameter(Mandatory=$true, HelpMessage="WinGet package ID, e.g. 'Google.Chrome' or 'Adobe.Acrobat.*' (prefix wildcard). NO leading or middle wildcards.")]
    # Validator: allowed chars + optional trailing .*
    # Examples accepted: Google.Chrome, Adobe.Acrobat.*, Microsoft.VCRedist.*
    # Examples rejected: *, .*, *.Chrome, Adobe.*.Reader, Adobe**, ; rm -rf, --all
    [ValidatePattern('^[A-Za-z0-9\._\-+]+(\.\*)?$')]
    [string]$PackageId
)

# ---- Locate winget.exe (same strategy ordering as discovery script) ----
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

# ---- Helper: enumerate OUT-OF-DATE packages matching a prefix ----
# Used only in wildcard mode. Returns the IDs of packages that (a) have an
# upgrade available and (b) start with $Prefix.
#
# Enumerates via `winget upgrade --include-unknown` rather than `winget list`.
# `winget list` returns hundreds of rows, which makes winget narrow the Id
# column and TRUNCATE long IDs with an ellipsis -- and that truncated ID then
# fails the sanity check and gets dropped (this is what caused the long
# Microsoft.VCRedist.2015+.x86/.x64 packages to be skipped while the shorter
# 2013 ID slipped through). `winget upgrade` returns only out-of-date packages
# (few rows), so the Id column stays wide and the IDs are not truncated. It is
# also semantically correct: wildcard mode only needs packages that actually
# have an upgrade available.
#
# This remains bounded enumeration over packages winget ALREADY KNOWS need
# updating on this endpoint - it cannot reach beyond winget's catalog or the
# prefix scope.
function Get-InstalledPackagesByPrefix {
    param(
        [string]$WingetExe,
        [string]$Prefix
    )

    try {
        # Force UTF-8 so winget's truncation ellipsis decodes cleanly instead
        # of becoming column-shifting mojibake. Wrapped in try/catch: some
        # service contexts have no console to set encoding on; if it throws,
        # the token-locating parser below still recovers the IDs.
        try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
        try { $OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

        $rawOutput = & "$WingetExe" upgrade --include-unknown --accept-source-agreements 2>&1 | Out-String
        $lines = $rawOutput -split "`r?`n"

        # Locate the header line (Name / Id / Version / Available / Source).
        $headerIndex = -1
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match '^\s*Name\s+Id\s+Version\s+Available') {
                $headerIndex = $i
                break
            }
        }
        if ($headerIndex -eq -1) {
            # No header = no upgrades available, or unexpected output.
            return @()
        }

        $headerLine   = $lines[$headerIndex]
        $idCol        = $headerLine.IndexOf("Id")
        $versionCol   = $headerLine.IndexOf("Version")
        $availableCol = $headerLine.IndexOf("Available")
        $sourceCol    = $headerLine.IndexOf("Source")

        # A real winget Id is ASCII, starts alphanumeric, and contains at least
        # one dot (Publisher.Package). That lets us tell a genuine Id apart from
        # mojibake junk (non-ASCII) and from plain name words (no dot).
        $idPattern = '^[A-Za-z0-9][A-Za-z0-9._+\-]*\.[A-Za-z0-9._+\-]+$'

        $dataStart = $headerIndex + 2
        $matched = @()

        for ($i = $dataStart; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]

            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            if ($line -match '^\d+ upgrades? available') { break }
            if ($line -match '^The following packages') { break }
            if ($line.Length -le $idCol) { continue }

            $id = $null

            # Primary: from the Id column onward, lock onto the first token that
            # is a valid winget Id (skipping any leading mojibake junk fragments
            # from a truncated name).
            $tokens = $line.Substring($idCol).Trim() -split '\s+'
            foreach ($tok in $tokens) {
                $cand = ($tok -replace '^[^A-Za-z0-9]+', '') -replace '[^A-Za-z0-9\._\-+]+$', ''
                if ($cand -match $idPattern) {
                    $id = $cand
                    break
                }
            }

            # Fallback: original fixed-width slice, so a row is never lost.
            if ([string]::IsNullOrWhiteSpace($id) -and ($line.Length -ge $sourceCol)) {
                try {
                    $id = $line.Substring($idCol, $versionCol - $idCol).Trim()
                    $id = ($id -replace '^[^A-Za-z0-9]+', '') -replace '[^A-Za-z0-9\._\-+]+$', ''
                } catch { }
            }

            if ([string]::IsNullOrWhiteSpace($id)) { continue }
            if ($id -match '^-+$') { continue }

            if ($id.StartsWith($Prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                $matched += $id
            }
        }

        return ($matched | Sort-Object -Unique)
    } catch {
        return @()
    }
}

# ---- Step 1: Locate winget ----
$winget = Find-WinGet
if ($null -eq $winget) {
    Write-Output "WINGET_UPDATE_RESULT=NOT_FOUND"
    Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
    Write-Output "WINGET_UPDATE_MESSAGE=winget.exe not found on this endpoint"
    exit 1
}

# ---- Step 2: Determine mode (exact match vs prefix wildcard) ----
$isWildcard = $PackageId.EndsWith('.*')

if ($isWildcard) {
    # Strip the trailing .* to get the prefix.
    $prefix = $PackageId.Substring(0, $PackageId.Length - 2)

    # Enumerate matching installed packages.
    $matchedIds = Get-InstalledPackagesByPrefix -WingetExe $winget -Prefix $prefix

    if ($matchedIds.Count -eq 0) {
        # No installed packages match the prefix - nothing to update.
        Write-Output "WINGET_UPDATE_RESULT=SUCCESS"
        Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
        Write-Output "WINGET_UPDATE_MATCHED="
        Write-Output "WINGET_UPDATE_SUCCEEDED=0"
        Write-Output "WINGET_UPDATE_FAILED=0"
        Write-Output "WINGET_UPDATE_MESSAGE=No installed packages match prefix '$prefix' (no action needed)"
        exit 0
    }

    # Update each matched package individually.
    $successCount = 0
    $failCount = 0
    $failedPackages = @()

    foreach ($id in $matchedIds) {
        try {
            $upgradeOutput = & "$winget" upgrade --id $id `
                                --silent `
                                --accept-package-agreements `
                                --accept-source-agreements `
                                --disable-interactivity `
                                2>&1 | Out-String
            $upgradeExit = $LASTEXITCODE
        } catch {
            $failCount++
            $failedPackages += "$id (exception)"
            continue
        }

        if ($upgradeExit -eq 0) {
            $successCount++
        } elseif ($upgradeOutput -match "No available upgrade|No newer version|No applicable update") {
            # Already up to date - count as success
            $successCount++
        } else {
            $failCount++
            $failedPackages += "$id (exit $upgradeExit)"
        }
    }

    # Determine overall result
    $matchedJoined = ($matchedIds -join ',')
    if ($failCount -eq 0) {
        Write-Output "WINGET_UPDATE_RESULT=SUCCESS"
        Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
        Write-Output "WINGET_UPDATE_MATCHED=$matchedJoined"
        Write-Output "WINGET_UPDATE_SUCCEEDED=$successCount"
        Write-Output "WINGET_UPDATE_FAILED=0"
        Write-Output "WINGET_UPDATE_MESSAGE=All $successCount matched packages updated successfully"
        exit 0
    } elseif ($successCount -gt 0) {
        # Partial success
        $failedStr = ($failedPackages -join '; ')
        Write-Output "WINGET_UPDATE_RESULT=PARTIAL"
        Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
        Write-Output "WINGET_UPDATE_MATCHED=$matchedJoined"
        Write-Output "WINGET_UPDATE_SUCCEEDED=$successCount"
        Write-Output "WINGET_UPDATE_FAILED=$failCount"
        Write-Output "WINGET_UPDATE_MESSAGE=$successCount succeeded, $failCount failed: $failedStr"
        exit 2
    } else {
        # All failed
        $failedStr = ($failedPackages -join '; ')
        Write-Output "WINGET_UPDATE_RESULT=FAILED"
        Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
        Write-Output "WINGET_UPDATE_MATCHED=$matchedJoined"
        Write-Output "WINGET_UPDATE_SUCCEEDED=0"
        Write-Output "WINGET_UPDATE_FAILED=$failCount"
        Write-Output "WINGET_UPDATE_MESSAGE=All $failCount matched packages failed: $failedStr"
        exit 2
    }

} else {
    # ---- EXACT MATCH MODE (unchanged from v2 logic) ----

    # Step 2a: Verify the package is installed
    try {
        $listOutput = & "$winget" list --id $PackageId --accept-source-agreements 2>&1 | Out-String
        $listExit = $LASTEXITCODE
    } catch {
        Write-Output "WINGET_UPDATE_RESULT=ERROR"
        Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
        Write-Output "WINGET_UPDATE_EXIT_CODE=3"
        Write-Output "WINGET_UPDATE_MESSAGE=Exception during package check: $($_.Exception.Message)"
        exit 3
    }

    if ($listExit -ne 0) {
        # Package not installed - nothing to update. Treat as success-with-noop.
        Write-Output "WINGET_UPDATE_RESULT=SUCCESS"
        Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
        Write-Output "WINGET_UPDATE_MATCHED="
        Write-Output "WINGET_UPDATE_SUCCEEDED=0"
        Write-Output "WINGET_UPDATE_FAILED=0"
        Write-Output "WINGET_UPDATE_MESSAGE=Package not installed on this endpoint (no action needed)"
        exit 0
    }

    # Step 2b: Run the upgrade for THIS ONE PACKAGE ONLY
    # --id $PackageId targets exactly one package by ID. There is no --all here,
    # and there must never be. See the DESIGN GUARANTEE block at the top.
    try {
        $upgradeOutput = & "$winget" upgrade --id $PackageId `
                            --silent `
                            --accept-package-agreements `
                            --accept-source-agreements `
                            --disable-interactivity `
                            2>&1 | Out-String
        $upgradeExit = $LASTEXITCODE
    } catch {
        Write-Output "WINGET_UPDATE_RESULT=ERROR"
        Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
        Write-Output "WINGET_UPDATE_EXIT_CODE=3"
        Write-Output "WINGET_UPDATE_MESSAGE=Exception during upgrade: $($_.Exception.Message)"
        exit 3
    }

    # Step 2c: Interpret the result
    if ($upgradeExit -eq 0) {
        Write-Output "WINGET_UPDATE_RESULT=SUCCESS"
        Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
        Write-Output "WINGET_UPDATE_MATCHED=$PackageId"
        Write-Output "WINGET_UPDATE_SUCCEEDED=1"
        Write-Output "WINGET_UPDATE_FAILED=0"
        Write-Output "WINGET_UPDATE_MESSAGE=Update applied successfully"
        exit 0
    }

    if ($upgradeOutput -match "No available upgrade|No newer version|No applicable update") {
        Write-Output "WINGET_UPDATE_RESULT=SUCCESS"
        Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
        Write-Output "WINGET_UPDATE_MATCHED=$PackageId"
        Write-Output "WINGET_UPDATE_SUCCEEDED=1"
        Write-Output "WINGET_UPDATE_FAILED=0"
        Write-Output "WINGET_UPDATE_MESSAGE=Package is already up to date"
        exit 0
    }

    # Otherwise, the upgrade attempt actually failed
    $failMsg = ($upgradeOutput -split "`n" | Where-Object { $_ -match '\S' } | Select-Object -Last 1) -replace '\s+', ' '
    if (-not $failMsg) { $failMsg = "Update failed with exit code $upgradeExit" }

    Write-Output "WINGET_UPDATE_RESULT=FAILED"
    Write-Output "WINGET_UPDATE_PACKAGE=$PackageId"
    Write-Output "WINGET_UPDATE_MATCHED=$PackageId"
    Write-Output "WINGET_UPDATE_SUCCEEDED=0"
    Write-Output "WINGET_UPDATE_FAILED=1"
    Write-Output "WINGET_UPDATE_EXIT_CODE=$upgradeExit"
    Write-Output "WINGET_UPDATE_MESSAGE=$failMsg"
    exit 2
}
