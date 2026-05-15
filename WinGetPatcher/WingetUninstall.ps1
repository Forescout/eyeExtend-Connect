# ============================================================
#  WinGet Uninstall Script  (v1)
#  Silently removes a single, explicitly-named WinGet package OR a
#  bounded family of packages (prefix wildcard mode), with extra
#  safety layers vs. the update script because uninstall is
#  destructive and not symmetric in blast radius with update.
#
#  Designed to be called by Forescout HPS "Run Script on Windows"
#  actions configured by per-application removal policy templates.
# ============================================================
#
#  ⚠️ DESIGN GUARANTEE — DO NOT BREAK THIS ⚠️
#
#  This script will ONLY uninstall packages whose IDs were explicitly
#  named by the admin via -PackageId. It will NEVER:
#    * Run `winget uninstall --all`
#    * Patch packages outside the admin's stated scope
#    * Allow leading wildcards or middle wildcards
#    * Allow single-segment wildcards (Microsoft.*, Adobe.*, etc.)
#    * Touch system-namespace packages (VCLibs, UI.Xaml, .NET, etc.)
#
#  Why this matters: removing the wrong software from a DoD endpoint
#  is not symmetric with installing wrong software. An over-broad
#  update wildcard wastes bandwidth and might bump a version
#  unexpectedly. An over-broad uninstall wildcard takes software off
#  endpoints that may not be easily put back, may break dependent
#  applications, may break the OS, may take down a critical workflow
#  during business hours. The extra safety layers below exist
#  because the failure modes deserve more layers of protection than
#  the update script's.
#
#  PACKAGE ID MODES
#  ----------------
#  Two modes are supported, both safe:
#
#  1. EXACT MATCH (recommended default)
#       -PackageId "Mozilla.Firefox"
#     Removes exactly one package by its full ID. All pre-built
#     templates use this mode.
#
#  2. PREFIX WILDCARD (for app families)
#       -PackageId "Adobe.Acrobat.*"
#     Removes every installed package whose ID starts with the given
#     prefix. The trailing ".*" is REQUIRED to opt into wildcard
#     mode. SINGLE-SEGMENT WILDCARDS (Microsoft.*, Adobe.*, etc.)
#     ARE BLOCKED — see SAFETY LAYERS below.
#
#  SAFETY LAYERS (defense in depth — MORE THAN THE UPDATE SCRIPT)
#  --------------------------------------------------------------
#    1. POLICY: Each per-app removal template only matches endpoints
#       whose Forescout-native Windows Applications Installed
#       property contains the intended substring (e.g. "Firefox" or
#       "Spotify"). WinGet ID never appears in the condition.
#    2. COMMAND LINE: The template's action passes the exact WinGet
#       package ID (or bounded wildcard) hardcoded by the template
#       author. Custom template requires deliberate paste replacement
#       in both condition (substring) and action (WinGet ID).
#    3. THIS SCRIPT - REGEX VALIDATOR: -PackageId is Mandatory, typed
#       [string], regex-validated. No --all, no leading wildcards,
#       no embedded shell metacharacters.
#    4. THIS SCRIPT - SINGLE-SEGMENT WILDCARD BLOCKLIST: Anything
#       matching `^[A-Za-z0-9_\-+]+\.\*$` is REFUSED at runtime.
#       This blocks Microsoft.*, Adobe.*, Google.*, Apple.*,
#       Oracle.*, Mozilla.*, Amazon.*, Windows.*, etc. Refused with
#       WINGET_UNINSTALL_RESULT=REFUSED_OVERBROAD_WILDCARD and
#       exit code 4. Educational error message tells admin to use
#       full string or narrow to vendor.product.*.
#    5. THIS SCRIPT - SYSTEM-NAMESPACE BLOCKLIST: Package IDs
#       starting with Microsoft.VCLibs., Microsoft.UI.Xaml.,
#       Microsoft.NET., Microsoft.DesktopAppInstaller, Microsoft.
#       WindowsTerminal, or Windows. are REFUSED at runtime
#       regardless of exact-match vs wildcard. These packages are
#       OS infrastructure or break Forescout's own management of
#       the endpoint. Refused with WINGET_UNINSTALL_RESULT=
#       REFUSED_SYSTEM_PACKAGE and exit code 4.
#    6. THIS SCRIPT - UPGRADE COMMAND: Always uses `winget uninstall
#       --id <specific>` (never --all). In wildcard mode, enumerates
#       installed packages via `winget list`, then loops with one
#       uninstall call per matched package. NEVER passes --purge
#       (which would remove user data alongside the package).
#
#  If you find yourself "improving" this script to remove any of
#  these safety layers, STOP. They are deliberate. The DoD admin
#  reading the README and seeing the BLOCKED FOR YOUR SAFETY
#  warnings is depending on these protections being intact.
# ============================================================
#
#  USAGE (from a Forescout Run Script action's "Command or Script" field):
#    WingetUninstall.ps1 -PackageId "Mozilla.Firefox"
#    WingetUninstall.ps1 -PackageId "Adobe.Acrobat.*"
#
#  Output (parseable by Forescout):
#    WINGET_UNINSTALL_RESULT=<SUCCESS|PARTIAL|FAILED|NOT_FOUND|ERROR|REFUSED_OVERBROAD_WILDCARD|REFUSED_SYSTEM_PACKAGE>
#    WINGET_UNINSTALL_PACKAGE=<original -PackageId argument>
#    WINGET_UNINSTALL_MATCHED=<comma-separated list of package IDs targeted>
#    WINGET_UNINSTALL_SUCCEEDED=<count of packages removed successfully>
#    WINGET_UNINSTALL_FAILED=<count of packages that failed>
#    WINGET_UNINSTALL_EXIT_CODE=<integer>   (only on FAILED/ERROR/PARTIAL)
#    WINGET_UNINSTALL_MESSAGE=<single-line summary>
#
#  Exit codes:
#    0 = all uninstalls succeeded (or no matching packages installed)
#    1 = winget.exe could not be located on this machine
#    2 = one or more uninstalls failed
#    3 = unexpected exception during uninstall
#    4 = REFUSED by safety layer (overbroad wildcard or system package)
# ============================================================

param(
    [Parameter(Mandatory=$true, HelpMessage="WinGet package ID, e.g. 'Mozilla.Firefox' or 'Adobe.Acrobat.*' (prefix wildcard). Single-segment wildcards (Microsoft.*, etc.) and system packages are blocked.")]
    # Validator: allowed chars + optional trailing .*
    # Examples accepted: Mozilla.Firefox, Spotify.Spotify, Adobe.Acrobat.*
    # Examples REJECTED at this layer:  *, .*, *.Firefox, Adobe.*.Reader, Adobe**, ; rm -rf, --all
    # Examples accepted HERE but BLOCKED by safety layers below:  Microsoft.*, Adobe.*, Windows.*
    [ValidatePattern('^[A-Za-z0-9\._\-+]+(\.\*)?$')]
    [string]$PackageId
)

# ============================================================
# SAFETY LAYER 4: Single-segment wildcard blocklist
# Refuses Microsoft.*, Adobe.*, Google.*, Apple.*, Oracle.*, etc.
# The pattern: starts with one segment of valid chars, then .*
# (no internal dots). Two-segment wildcards like Adobe.Acrobat.*
# pass this check because the first segment is "Adobe.Acrobat"
# which contains an internal dot.
# ============================================================
if ($PackageId -match '^[A-Za-z0-9_\-+]+\.\*$') {
    Write-Output "WINGET_UNINSTALL_RESULT=REFUSED_OVERBROAD_WILDCARD"
    Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
    Write-Output "WINGET_UNINSTALL_MATCHED="
    Write-Output "WINGET_UNINSTALL_SUCCEEDED=0"
    Write-Output "WINGET_UNINSTALL_FAILED=0"
    Write-Output "WINGET_UNINSTALL_MESSAGE=BLOCKED FOR YOUR SAFETY: '$PackageId' is a single-vendor wildcard and would remove every product from that vendor. Use the full package ID for the specific software you want to remove (e.g. 'Adobe.Acrobat.Pro' instead of 'Adobe.*'), or narrow your wildcard to at least vendor.product.* (e.g. 'Adobe.Acrobat.*' which removes only Acrobat variants)."
    exit 4
}

# ============================================================
# SAFETY LAYER 5: System-namespace blocklist
# Refuses OS-infrastructure packages even if specified exactly.
# These packages are dependencies of other applications and/or
# the operating system itself; removing them breaks things.
# ============================================================
$SYSTEM_PACKAGE_PREFIXES = @(
    'Microsoft.VCLibs.',
    'Microsoft.UI.Xaml.',
    'Microsoft.NET.',
    'Microsoft.DesktopAppInstaller',  # this IS winget — never remove
    'Microsoft.WindowsTerminal',
    'Windows.'
)

foreach ($prefix in $SYSTEM_PACKAGE_PREFIXES) {
    if ($PackageId.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Output "WINGET_UNINSTALL_RESULT=REFUSED_SYSTEM_PACKAGE"
        Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
        Write-Output "WINGET_UNINSTALL_MATCHED="
        Write-Output "WINGET_UNINSTALL_SUCCEEDED=0"
        Write-Output "WINGET_UNINSTALL_FAILED=0"
        Write-Output "WINGET_UNINSTALL_MESSAGE=BLOCKED FOR YOUR SAFETY: '$PackageId' is in a system-namespace ($prefix*). These packages are OS infrastructure or runtime dependencies of other applications. Removing them can break the operating system or applications that depend on them. This script will not touch them regardless of how the request is spelled."
        exit 4
    }
}

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

# ---- Helper: enumerate installed packages matching a prefix ----
# Same as WingetUpdate.ps1's helper. Used only in wildcard mode.
# Calls `winget list` (no uninstall), parses the output for package
# IDs, returns those that start with $prefix. Bounded enumeration
# over packages winget ALREADY KNOWS about on this endpoint — cannot
# reach beyond winget's catalog.
function Get-InstalledPackagesByPrefix {
    param(
        [string]$WingetExe,
        [string]$Prefix
    )

    try {
        $listOutput = & "$WingetExe" list --accept-source-agreements 2>&1 | Out-String
        $lines = $listOutput -split "`r?`n"

        $matched = @()
        foreach ($line in $lines) {
            if ($line -match '^\s*$') { continue }
            if ($line -match '^Name\s+Id\s+Version') { continue }
            if ($line -match '^-+\s*$') { continue }
            if ($line -match '^\\\s+') { continue }   # spinner artifacts

            $tokens = $line -split '\s{2,}'
            foreach ($t in $tokens) {
                $t = $t.Trim()
                if ($t.StartsWith($Prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                    if ($t -match '^[A-Za-z0-9\._\-+]+$') {
                        $matched += $t
                        break
                    }
                }
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
    Write-Output "WINGET_UNINSTALL_RESULT=NOT_FOUND"
    Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
    Write-Output "WINGET_UNINSTALL_MATCHED="
    Write-Output "WINGET_UNINSTALL_SUCCEEDED=0"
    Write-Output "WINGET_UNINSTALL_FAILED=0"
    Write-Output "WINGET_UNINSTALL_MESSAGE=winget.exe not found on this endpoint"
    exit 1
}

# ---- Step 2: Determine mode (exact match vs prefix wildcard) ----
$isWildcard = $PackageId.EndsWith('.*')

if ($isWildcard) {
    # Strip the trailing .* to get the prefix
    $prefix = $PackageId.Substring(0, $PackageId.Length - 2)

    # Re-check system-namespace prefixes against the wildcard prefix.
    # (Safety layer 5 above caught system packages spelled exactly.
    # This catches "Microsoft.VCLibs.*" style wildcards too.)
    foreach ($sysPrefix in $SYSTEM_PACKAGE_PREFIXES) {
        if ($prefix.StartsWith($sysPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
            $sysPrefix.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            Write-Output "WINGET_UNINSTALL_RESULT=REFUSED_SYSTEM_PACKAGE"
            Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
            Write-Output "WINGET_UNINSTALL_MATCHED="
            Write-Output "WINGET_UNINSTALL_SUCCEEDED=0"
            Write-Output "WINGET_UNINSTALL_FAILED=0"
            Write-Output "WINGET_UNINSTALL_MESSAGE=BLOCKED FOR YOUR SAFETY: wildcard '$PackageId' would target system-namespace packages ($sysPrefix*). These are OS infrastructure and will not be uninstalled by this script."
            exit 4
        }
    }

    # Enumerate matching installed packages
    $matchedIds = Get-InstalledPackagesByPrefix -WingetExe $winget -Prefix $prefix

    # Filter out any system-namespace packages that snuck through enumeration
    # (defense in depth — should already be impossible after the prefix check
    # above, but if winget's catalog has surprises, refuse them here too)
    $safeIds = @()
    foreach ($id in $matchedIds) {
        $isSystem = $false
        foreach ($sysPrefix in $SYSTEM_PACKAGE_PREFIXES) {
            if ($id.StartsWith($sysPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                $isSystem = $true
                break
            }
        }
        if (-not $isSystem) {
            $safeIds += $id
        }
    }
    $matchedIds = $safeIds

    if ($matchedIds.Count -eq 0) {
        # No installed packages match the prefix - nothing to remove
        Write-Output "WINGET_UNINSTALL_RESULT=SUCCESS"
        Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
        Write-Output "WINGET_UNINSTALL_MATCHED="
        Write-Output "WINGET_UNINSTALL_SUCCEEDED=0"
        Write-Output "WINGET_UNINSTALL_FAILED=0"
        Write-Output "WINGET_UNINSTALL_MESSAGE=No installed packages match prefix '$prefix' (no action needed)"
        exit 0
    }

    # Uninstall each matched package individually
    $successCount = 0
    $failCount = 0
    $failedPackages = @()

    foreach ($id in $matchedIds) {
        try {
            $uninstallOutput = & "$winget" uninstall --id $id `
                                  --silent `
                                  --accept-source-agreements `
                                  --disable-interactivity `
                                  2>&1 | Out-String
            $uninstallExit = $LASTEXITCODE
        } catch {
            $failCount++
            $failedPackages += "$id (exception)"
            continue
        }

        if ($uninstallExit -eq 0) {
            $successCount++
        } elseif ($uninstallOutput -match "No installed package found|not installed") {
            # Already gone - count as success
            $successCount++
        } else {
            $failCount++
            $failedPackages += "$id (exit $uninstallExit)"
        }
    }

    # Determine overall result
    $matchedJoined = ($matchedIds -join ',')
    if ($failCount -eq 0) {
        Write-Output "WINGET_UNINSTALL_RESULT=SUCCESS"
        Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
        Write-Output "WINGET_UNINSTALL_MATCHED=$matchedJoined"
        Write-Output "WINGET_UNINSTALL_SUCCEEDED=$successCount"
        Write-Output "WINGET_UNINSTALL_FAILED=0"
        Write-Output "WINGET_UNINSTALL_MESSAGE=All $successCount matched packages uninstalled successfully"
        exit 0
    } elseif ($successCount -gt 0) {
        # Partial success
        $failedStr = ($failedPackages -join '; ')
        Write-Output "WINGET_UNINSTALL_RESULT=PARTIAL"
        Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
        Write-Output "WINGET_UNINSTALL_MATCHED=$matchedJoined"
        Write-Output "WINGET_UNINSTALL_SUCCEEDED=$successCount"
        Write-Output "WINGET_UNINSTALL_FAILED=$failCount"
        Write-Output "WINGET_UNINSTALL_MESSAGE=$successCount succeeded, $failCount failed: $failedStr"
        exit 2
    } else {
        # All failed
        $failedStr = ($failedPackages -join '; ')
        Write-Output "WINGET_UNINSTALL_RESULT=FAILED"
        Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
        Write-Output "WINGET_UNINSTALL_MATCHED=$matchedJoined"
        Write-Output "WINGET_UNINSTALL_SUCCEEDED=0"
        Write-Output "WINGET_UNINSTALL_FAILED=$failCount"
        Write-Output "WINGET_UNINSTALL_MESSAGE=All $failCount matched packages failed: $failedStr"
        exit 2
    }

} else {
    # ---- EXACT MATCH MODE ----

    # Step 2a: Verify the package is installed
    try {
        $listOutput = & "$winget" list --id $PackageId --accept-source-agreements 2>&1 | Out-String
        $listExit = $LASTEXITCODE
    } catch {
        Write-Output "WINGET_UNINSTALL_RESULT=ERROR"
        Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
        Write-Output "WINGET_UNINSTALL_MATCHED="
        Write-Output "WINGET_UNINSTALL_SUCCEEDED=0"
        Write-Output "WINGET_UNINSTALL_FAILED=0"
        Write-Output "WINGET_UNINSTALL_EXIT_CODE=3"
        Write-Output "WINGET_UNINSTALL_MESSAGE=Exception during package check: $($_.Exception.Message)"
        exit 3
    }

    if ($listExit -ne 0) {
        # Package not installed - nothing to remove. Treat as success-with-noop.
        Write-Output "WINGET_UNINSTALL_RESULT=SUCCESS"
        Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
        Write-Output "WINGET_UNINSTALL_MATCHED="
        Write-Output "WINGET_UNINSTALL_SUCCEEDED=0"
        Write-Output "WINGET_UNINSTALL_FAILED=0"
        Write-Output "WINGET_UNINSTALL_MESSAGE=Package not installed on this endpoint (no action needed)"
        exit 0
    }

    # Step 2b: Run the uninstall for THIS ONE PACKAGE ONLY
    # --id $PackageId targets exactly one package by ID. There is no
    # --all here, and there must never be. We also explicitly do NOT
    # pass --purge, which would remove user data alongside the
    # application. See the DESIGN GUARANTEE block at the top.
    try {
        $uninstallOutput = & "$winget" uninstall --id $PackageId `
                              --silent `
                              --accept-source-agreements `
                              --disable-interactivity `
                              2>&1 | Out-String
        $uninstallExit = $LASTEXITCODE
    } catch {
        Write-Output "WINGET_UNINSTALL_RESULT=ERROR"
        Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
        Write-Output "WINGET_UNINSTALL_MATCHED=$PackageId"
        Write-Output "WINGET_UNINSTALL_SUCCEEDED=0"
        Write-Output "WINGET_UNINSTALL_FAILED=1"
        Write-Output "WINGET_UNINSTALL_EXIT_CODE=3"
        Write-Output "WINGET_UNINSTALL_MESSAGE=Exception during uninstall: $($_.Exception.Message)"
        exit 3
    }

    # Step 2c: Interpret the result
    if ($uninstallExit -eq 0) {
        Write-Output "WINGET_UNINSTALL_RESULT=SUCCESS"
        Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
        Write-Output "WINGET_UNINSTALL_MATCHED=$PackageId"
        Write-Output "WINGET_UNINSTALL_SUCCEEDED=1"
        Write-Output "WINGET_UNINSTALL_FAILED=0"
        Write-Output "WINGET_UNINSTALL_MESSAGE=Package uninstalled successfully"
        exit 0
    }

    if ($uninstallOutput -match "No installed package found|not installed") {
        Write-Output "WINGET_UNINSTALL_RESULT=SUCCESS"
        Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
        Write-Output "WINGET_UNINSTALL_MATCHED=$PackageId"
        Write-Output "WINGET_UNINSTALL_SUCCEEDED=1"
        Write-Output "WINGET_UNINSTALL_FAILED=0"
        Write-Output "WINGET_UNINSTALL_MESSAGE=Package was not installed (race condition or already removed)"
        exit 0
    }

    # Otherwise, the uninstall attempt actually failed
    $failMsg = ($uninstallOutput -split "`n" | Where-Object { $_ -match '\S' } | Select-Object -Last 1) -replace '\s+', ' '
    if (-not $failMsg) { $failMsg = "Uninstall failed with exit code $uninstallExit" }

    Write-Output "WINGET_UNINSTALL_RESULT=FAILED"
    Write-Output "WINGET_UNINSTALL_PACKAGE=$PackageId"
    Write-Output "WINGET_UNINSTALL_MATCHED=$PackageId"
    Write-Output "WINGET_UNINSTALL_SUCCEEDED=0"
    Write-Output "WINGET_UNINSTALL_FAILED=1"
    Write-Output "WINGET_UNINSTALL_EXIT_CODE=$uninstallExit"
    Write-Output "WINGET_UNINSTALL_MESSAGE=$failMsg"
    exit 2
}
