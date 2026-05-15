# WinGet Patcher for Forescout

A Forescout eyeExtend Connect app that uses Windows Package Manager (`winget`) to discover, patch, and remove software on Windows endpoints. Replaces dozens of per-application PowerShell scripts with a small set of reusable policy templates organized in two cascading subfolders in the Policy Wizard.

**Version:** 2.1.1
**Authors:** Travis Matthews / Liz Akridge — Forescout
**Requires:** Forescout eyeSight 8.3.0+, **Connect Plugin 2.0.4 or higher** (Connect Module 2.1.6+). The 2.0.4 minimum is required for the multiple-folder Policy Wizard feature this app uses.

---

## The Problem This Solves

Traditional Forescout deployments accumulate 100+ hand-crafted per-application PowerShell scripts (one per app, one per version), each requiring manual edits when software updates. WinGet Patcher replaces that pattern with a small set of reusable scripts driven by WinGet's package catalog. One source of truth, opt-in remediation, no version numbers hard-coded into Forescout.

---

## What's In This Package

| File | Purpose | Where it goes |
|---|---|---|
| `ForeScout-eca-winget-2.1.1.eca` | Connect app | Forescout Console → Tools → Options → Connect → Import |
| `WingetDiscover_v3.ps1` | Discovery script | Expected Script Results |
| `WingetUpdate.ps1` | Update script | Run Script on Windows |
| `WingetInventory.ps1` | Inventory script | Expected Script Results |
| `WingetUninstall.ps1` | Uninstall script | Run Script on Windows |
| `README.md` | This file | Reference |
| `User_Guide.md` | Day-to-day workflows | Reference |
| `Signing_Review.md` | For signing teams | Reference |

---

## Installation (~15 minutes)

### Step 1: Import the PowerShell scripts into the console

The four `.ps1` files **cannot be bundled** into the `.eca` (Forescout architectural limitation — Connect apps and HPS scripts use separate registration paths). They get registered in two different places depending on how each script is used:

- **Windows Expected Script Result** — for scripts invoked as *conditions* (the script runs, its output is matched against criteria). This is where **Discovery** and **Inventory** scripts go.
- **Run Script on Windows** — for scripts invoked as *actions* (the script just executes on the endpoint). This is where **Update** and **Uninstall** scripts go.

**This step must be completed before importing the `.eca`** — the policy templates reference these scripts by name, and the templates won't resolve correctly if the scripts aren't registered yet.

#### Scripts to register in "Expected Script Results"

| Script | Used by | Register as |
|---|---|---|
| `WingetDiscover_v3.ps1` | 1.1 WinGet Discovery | `WingetDiscover_v3.ps1` |
| `WingetInventory.ps1` | 2.1 WinGet Inventory - Find Package ID | `WingetInventory.ps1` |

To register: open any custom policy, add a condition, choose **Windows Expected Script Result**, click the **...** browse button next to "Command or Script file", and upload the `.ps1`.

#### Scripts to register in "Run Script on Windows"

| Script | Used by | Register as |
|---|---|---|
| `WingetUpdate.ps1` | 1.2–1.6 (all update templates) | `WingetUpdate.ps1` (no version suffix) |
| `WingetUninstall.ps1` | 2.2–2.6 (all uninstall templates) | `WingetUninstall.ps1` |

To register: open any custom policy, add an action, choose **Run Script on Windows**, click the **...** browse button, and upload the `.ps1`.

#### Naming requirements

- ✅ `WingetUpdate.ps1`  ❌ `WingetUpdate_v3.ps1`
- ✅ `WingetUninstall.ps1`  ❌ `WingetUninstall_v2.ps1`
- ✅ `WingetInventory.ps1`  ❌ `WingetInventory_v1.ps1`
- ✅ `WingetDiscover_v3.ps1` ← exception: this one keeps the `_v3` suffix

### Step 2: Import the Connect app

1. Forescout console → **Tools → Options → Connect**
2. Click **Import** → browse to `ForeScout-eca-winget-2.1.1.eca` → Import
3. Wait for "Successfully reloaded system configuration file"
4. Verify the app appears with **Status: Running**

If you get a signature error:
```bash
fstool allow_unsigned_connect_app_install true
```
(Top-level `fstool` command, not under `connect_module`. Setting persists across restarts.)

### Step 3: Verify the cascading folder layout

Open **Policy → Add → Custom**. You should see one new top-level template group with **two cascading subfolders**:

```
WinGet Patcher (briefcase top-level icon)
├── Software Updating (briefcase subfolder icon)
│   ├── 1.1-WinGet Discovery
│   ├── 1.2-WinGet Update - Google Chrome
│   ├── 1.3-WinGet Update - Notepad++
│   ├── 1.4-WinGet Update - Adobe Acrobat (all variants)
│   ├── 1.5-WinGet Update - Microsoft VCRedist (all variants)
│   └── 1.6-WinGet Update - Custom (Paste Package ID)
└── Software Removal (trash can subfolder icon)
    ├── 2.1-WinGet Inventory - Find Package ID
    ├── 2.2-WinGet Uninstall - Mozilla Firefox
    ├── 2.3-WinGet Uninstall - Adobe Flash Player
    ├── 2.4-WinGet Uninstall - Adobe Shockwave Player
    ├── 2.5-WinGet Uninstall - Spotify
    └── 2.6-WinGet Uninstall - Custom (Paste Package ID)
```

If the templates all appear flat (no subfolders), see Troubleshooting below.

### Step 4: Enable WinGet Discovery

The 1.1 Discovery template is the prerequisite for all 1.x update templates.

1. Policy Wizard → **WinGet Patcher → Software Updating → 1.1-WinGet Discovery** → Add
2. Scope to your Windows endpoints (start with a small test segment)
3. Save and enable the policy
4. Wait ~30 minutes for first discovery

After discovery runs, each endpoint's Profile tab will show **WinGet Updates Info**:
- **Count** — integer (e.g., `8`)
- **Out-of-Date Apps** — multi-line list, format `PackageId (current -> available)`

### Step 5: Enable update / removal policies as needed

See the **User Guide** for step-by-step workflows. Quick summary:

- **To patch a specific app** → enable the corresponding 1.x update template under Software Updating
- **To find a package ID for removal** → use 2.1 Inventory (one host only, reference use)
- **To remove an app** → enable 2.x uninstall template under Software Removal, or use 2.6 Custom

---

## What's In Each Subfolder

### Software Updating (1.x templates)

| Template | What it does |
|---|---|
| **1.1-WinGet Discovery** | Required prerequisite. Populates WinGet Updates Info property. 24-hour recheck. |
| **1.2-WinGet Update - Google Chrome** | Patches Chrome only. Disabled by default. |
| **1.3-WinGet Update - Notepad++** | Patches Notepad++ only. Disabled by default. |
| **1.4-WinGet Update - Adobe Acrobat (all variants)** | Patches all `Adobe.Acrobat.*` packages. Disabled by default. |
| **1.5-WinGet Update - Microsoft VCRedist (all variants)** | Patches all `Microsoft.VCRedist.*` packages. Disabled by default. |
| **1.6-WinGet Update - Custom (Paste Package ID)** | Generic — admin pastes any WinGet package ID. Disabled by default. |

### Software Removal (2.x templates)

| Template | What it does |
|---|---|
| **2.1-WinGet Inventory - Find Package ID** | Reference helper. Three safety layers (see User Guide). Disabled by default. |
| **2.2-WinGet Uninstall - Mozilla Firefox** | Removes Firefox release builds. Disabled by default. |
| **2.3-WinGet Uninstall - Adobe Flash Player** | Removes Adobe Flash (EOL). Disabled by default. |
| **2.4-WinGet Uninstall - Adobe Shockwave Player** | Removes Adobe Shockwave (EOL). Disabled by default. |
| **2.5-WinGet Uninstall - Spotify** | Removes Spotify. Disabled by default. |
| **2.6-WinGet Uninstall - Custom (Paste Package ID)** | Generic — admin pastes any WinGet package ID. Disabled by default. |

---

## Safety Design

- **Everything disabled by default.** Every template ships with the policy and any action disabled. An admin must explicitly enable both to do anything.
- **Per-package only.** Update and uninstall scripts validate input via regex. Commands always pass `--id <specific>` — never `--all`.
- **Wildcards are bounded.** Trailing `.*` only. Enumerates installed packages whose ID starts with the prefix, then operates on each one individually by exact ID.
- **System namespace blocklist.** The uninstall script refuses to touch `Microsoft.*` system packages, OS components, and Windows Defender (regardless of policy).
- **Inventory helper has its own three-layer safety.** See User Guide.
- **Discovery is read-only.** `WingetDiscover_v3.ps1` only enumerates — no changes to endpoints.

---

## Apps This Will NOT Patch (Intentionally Excluded)

Pre-built templates exclude:
- **Microsoft Office (`Microsoft.Office`)** — user data loss risk during update
- **Microsoft VSTOR (`Microsoft.VSTOR`)** — bundled with Office
- **Microsoft Edge** — typically managed by Intune / SCCM / Windows Update

You can still patch these via 1.6 Custom if your environment specifically requires it.

---

## Re-installing or Upgrading

**Forescout's Connect Plugin caches aggressively.** When updating the app, the console only honors an in-place "Update" if `property.json` and `system.json` are structurally identical. Any structural change requires:

1. **Remove** the existing app from Tools → Options → Connect
2. **Delete any policies** still referencing the old templates (especially the 2.1 Inventory template)
3. **Re-import** the new `.eca`

### Special note on 2.1 Inventory template re-imports

The 2.1 Inventory template uses Forescout's `script_result.<hash>` mechanism. Forescout maintains a persistent cache mapping these hashes to commands. **If you've previously imported a 2.1 template and created policies from it, delete those policies before re-importing the new app**, or Forescout may show a cached command (e.g., a previous search term) instead of the fresh `[INSERT-SOFTWARE-NAME-HERE]` placeholder.

---

## Troubleshooting

### The Connect Plugin version on my Forescout EM is older than 2.0.4

The multiple-folder Policy Wizard feature this app uses was added in Connect Plugin 2.0.4. On older plugin versions, the app will likely import but show all 12 templates as a flat list under "WinGet Patcher" instead of the two cascading subfolders. The app will still function correctly — only the visual organization is affected. Upgrade the Connect Plugin to 2.0.4+ for the cascading layout.

### The app imports but I don't see the two subfolders

If everything shows flat under "WinGet Patcher" instead of nested under Software Updating / Software Removal:

1. Confirm Connect Plugin version is 2.0.4 or higher (Tools → Options → Plugins). Cascading subfolders require 2.0.4+.
2. Confirm the import completed cleanly — no errors in `python_server.log`
3. Close and reopen the Policy Wizard (UI caches sometimes need a refresh)

### Import fails with "File not found: At least one file with [py] extension is required"

The `.eca` file is corrupted — re-download and re-import.

### Discovery runs but properties don't populate

- Verify `WingetDiscover_v3.ps1` is registered in Windows Expected Script Result
- Confirm the Connect app is in "Running" state under Tools → Options → Connect
- Check the host's policy detail for script execution errors
- Common cause: SecureConnector running as a per-user execution alias. The script's 4-strategy lookup usually handles this; on failure the host's policy detail will say "winget.exe could not be located"

### Update or uninstall policy matches a host but doesn't fire

- Verify BOTH the policy AND the Run Script action are enabled
- Check that the relevant `.ps1` is registered with the exact expected filename (no version suffix)
- Look at host's policy detail for error messages

### 2.1 Inventory shows the wrong command after re-import

Forescout's `script_result.<hash>` cache is holding an old binding. Fix:
1. Delete any policies created from the 2.1 template
2. Remove the Connect app
3. Re-import the `.eca`
4. Re-add the 2.1 template to a new policy

### Custom template's package ID isn't matching

- Confirm you replaced ALL occurrences of the placeholder (condition AND action — two places)
- Copy the package ID verbatim from an actual host's Profile tab — typos are the #1 cause
- For wildcards: prefix must end with `.*` (period-asterisk)

---

## Support

Internally developed.

- Functional questions → consult the User Guide
- Architectural / build questions → see `WinGetPatcher_Handoff_v4.2.md`
- Production issues → contact your Forescout administrator
