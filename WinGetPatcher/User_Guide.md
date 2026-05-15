# WinGet Patcher — User Guide

A day-to-day walkthrough for Forescout administrators using the WinGet Patcher Connect app. This guide assumes the app is already installed (see `README.md`).

---

## Mental model

WinGet Patcher is **one Connect app with two cascading subfolders** in the Policy Wizard:

```
Policy → Add → Custom

  WinGet Patcher        (briefcase top-level icon)
  ├── Software Updating  (briefcase subfolder icon)
  │   ├── 1.1-WinGet Discovery
  │   ├── 1.2-WinGet Update - Google Chrome
  │   ├── 1.3-WinGet Update - Notepad++
  │   ├── 1.4-WinGet Update - Adobe Acrobat (all variants)
  │   ├── 1.5-WinGet Update - Microsoft VCRedist (all variants)
  │   └── 1.6-WinGet Update - Custom (Paste Package ID)
  │
  └── Software Removal   (trash can subfolder icon)
      ├── 2.1-WinGet Inventory - Find Package ID
      ├── 2.2-WinGet Uninstall - Mozilla Firefox
      ├── 2.3-WinGet Uninstall - Adobe Flash Player
      ├── 2.4-WinGet Uninstall - Adobe Shockwave Player
      ├── 2.5-WinGet Uninstall - Spotify
      └── 2.6-WinGet Uninstall - Custom (Paste Package ID)
```

You don't have to use both halves. If you only want patching, the Software Updating subfolder is all you need. If you only want removal, the Software Removal subfolder works independently — it does not require the Discovery template to be active.

---

## Before you start: prerequisites check

None of these workflows will work unless **all** of the following are true:

### 1. Connect Plugin version is 2.0.4 or higher

The cascading subfolder feature this app uses requires Connect Plugin 2.0.4+. Check at **Tools → Options → Plugins** for "Connect Plugin" version. If older, upgrade the plugin first or the templates will all appear flat under "WinGet Patcher" (still functional, just not organized).

### 2. The PowerShell scripts are registered in the console

Templates reference four scripts by exact filename. These have to be registered in **two separate places** before any template can do anything.

**Registered in "Windows Expected Script Result"** (used as conditions):

| Script (exact filename) | Used by which template(s) |
|---|---|
| `WingetDiscover_v3.ps1` | 1.1 WinGet Discovery |
| `WingetInventory.ps1` | 2.1 WinGet Inventory - Find Package ID |

**Registered in "Run Script on Windows"** (used as actions):

| Script (exact filename) | Used by which template(s) |
|---|---|
| `WingetUpdate.ps1` | 1.2, 1.3, 1.4, 1.5, 1.6 (all update templates) |
| `WingetUninstall.ps1` | 2.2, 2.3, 2.4, 2.5, 2.6 (all uninstall templates) |

**How to check:** open any existing custom policy. Add a Windows Expected Script Result condition (or a Run Script on Windows action) and click the `...` browse button next to "Command or Script file" — your scripts should appear in the dropdown. If they don't, see the README, Installation, Step 1.

**Filename matters.** If a script is registered as `WingetUpdate_v3.ps1` or `WingetUpdate-final.ps1` instead of `WingetUpdate.ps1`, the templates won't find it. The one exception is `WingetDiscover_v3.ps1` — that one keeps its `_v3` suffix.

### 3. The Connect app is installed and running

Open **Tools → Options → Connect**. You should see `WinGetPatcher` with **Status: Running**. If missing or stopped, see the README, Installation, Step 2.

---

## Workflow 1: See what's out of date on your endpoints

**You want:** a list, per endpoint, of which apps need updating.

**You'll use:** Template 1.1 (WinGet Discovery), under Software Updating.

**Time:** First-time setup ~5 minutes; results appear after the first discovery cycle.

### Steps

1. Policy → Add → Custom → **WinGet Patcher → Software Updating → 1.1-WinGet Discovery** → Next
2. **Scope** to the Windows endpoints you want to inventory. Start small — a test segment, then expand.
3. (Optional) **Rename** the policy to something organization-specific (e.g., "1.1-WinGet Discovery - HQ Win10/11")
4. Finish the wizard, then **enable** the policy
5. Wait for the discovery cycle to fire (default 24 hours; you can decrease for faster initial results)

### What you'll see

On each matching endpoint, open its **Host Details → Profile tab**. Under **WinGet Updates Info** you'll have:

- **Count** — integer, how many apps are out of date (e.g., `8`). `-1` means winget couldn't be located on this endpoint.
- **Out-of-Date Apps** — multi-line list in the format `PackageId (current_version -> available_version)`:
  ```
  Google.Chrome (118.0.5993.118 -> 120.0.6099.71)
  Notepad++.Notepad++ (8.5.6 -> 8.5.8)
  Adobe.Acrobat.Reader.64-bit (23.006.20360 -> 23.008.20458)
  ```

This is the source of truth for everything else in the patching workflow.

### Tuning

- **Discovery interval** — Advanced → Recheck match → adjust the RATE. Default 24 hours. Faster is fine; the cached script_result has a 72-hour TTL so any interval ≤ 72 hours works.
- **Scope expansion** — once happy with the test segment, edit the policy's IP range to cover the full fleet.

---

## Workflow 2: Patch a specific application (built-in template)

**You want:** Chrome (or Notepad++, or Adobe Acrobat, or VCRedist) updated whenever it's out of date.

**Prerequisite:** Workflow 1 done. Discovery must be running.

**You'll use:** Template 1.2, 1.3, 1.4, or 1.5, under Software Updating.

**Time:** ~3 minutes per app.

### Steps (using Chrome as example)

1. Policy → Add → Custom → **WinGet Patcher → Software Updating → 1.2-WinGet Update - Google Chrome** → Next
2. **Scope** to the same endpoints as your Discovery policy (or a subset for testing)
3. (Optional) Rename the policy
4. Finish the wizard
5. **Enable the policy** AND **enable the Run Script action** inside it (both are separately disabled by default — this is intentional safety)

### What happens

- Forescout evaluates each in-scope endpoint
- If `WinGet Updates - Out-of-Date Apps contains "Google.Chrome"`, the policy fires
- The Run Script action invokes `WingetUpdate.ps1 -PackageId "Google.Chrome"` on the endpoint
- Chrome upgrades silently
- Next discovery cycle, Chrome drops off the out-of-date list, the policy stops matching that endpoint

You don't need to do anything else. The policy is self-maintaining.

### When the wildcard variants are useful (1.4, 1.5)

Adobe and Microsoft ship apps as MANY WinGet packages — Adobe alone has Reader 32-bit, Reader 64-bit, Acrobat Pro DC, Acrobat 2020, etc. Microsoft VCRedist has ~12 variants across architectures and years. Use the wildcard templates:

- **1.4 Adobe Acrobat (all variants)** — covers `Adobe.Acrobat.*` packages
- **1.5 Microsoft VCRedist (all variants)** — covers `Microsoft.VCRedist.*` packages

These work the same as the exact-match templates but patch every package family member that's out of date.

---

## Workflow 3: Patch an app NOT in the built-in templates

**You want:** to patch Adobe Photoshop, or 7-Zip, or VLC, or anything else.

**Prerequisite:** Workflow 1 done; you've identified the exact WinGet package ID.

**You'll use:** Template 1.6 (Custom Patcher), under Software Updating.

**Time:** ~5 minutes.

### Step A: Find the exact package ID

1. Find an endpoint that has the app out of date (any will do)
2. Host Details → Profile tab → **WinGet Updates Info → Out-of-Date Apps**
3. Find the line for your app. The package ID is the first field, before the open paren. Example:
   ```
   Adobe.Photoshop (24.7 -> 25.1)
   ```
   The package ID is `Adobe.Photoshop`. Copy it verbatim — exact case, exact punctuation.

### Step B: Configure the custom template

1. Policy → Add → Custom → **WinGet Patcher → Software Updating → 1.6-WinGet Update - Custom (Paste Package ID)** → Next
2. The template ships with `[PASTE-PACKAGE-ID-HERE]` in **two places** — replace BOTH with your package ID:
   - **In the condition:** "WinGet Updates Info contains `[PASTE-PACKAGE-ID-HERE]`" → change the contains value
   - **In the action:** "Run Script: WingetUpdate.ps1 -PackageId `[PASTE-PACKAGE-ID-HERE]`" → edit the command
3. **Rename the policy** to include the app name (e.g., "WinGet Update - Adobe Photoshop"). Future-you will appreciate this.
4. Scope, finish, enable both the policy and the action

### Wildcards for app families

If you're targeting a family (e.g., all Photoshop variants — Photoshop 2024, Photoshop CC, Photoshop 2026), use a trailing wildcard:

- Package ID for condition: `Adobe.Photoshop`  (contains-match catches all)
- Package ID for action: `Adobe.Photoshop.*`  (wildcard upgrade)

The wildcard is bounded:
- ✅ `Adobe.Photoshop.*` — works
- ✅ `Microsoft.OpenJDK.*` — works
- ❌ `*.Photoshop` — rejected (no leading wildcards)
- ❌ `Adobe.*.Reader` — rejected (no middle wildcards)
- ❌ `*` or `.*` — rejected (must have a prefix)

If you forget to replace the placeholder, `WingetUpdate.ps1` will refuse to run — the script's regex validator rejects the literal brackets. Fail-loud by design.

---

## Workflow 4: Find the package ID for software you want to remove

**You want:** the exact WinGet package ID for unwanted software on your endpoints.

**You'll use:** Template 2.1 (WinGet Inventory), under Software Removal.

**Time:** ~5 minutes.

> ⚠️ **REFERENCE USE ONLY.** This template is designed to run on ONE host at a time. It's a helper for finding package IDs, not a continuous monitoring policy. Three independent safety guards are in place:
> 1. The policy is disabled by default
> 2. The Access IP condition is pre-set to `192.0.2.1` (a non-routable documentation IP) so it won't match any real host until you change it
> 3. The script command contains `[INSERT-SOFTWARE-NAME-HERE]` so it won't return useful results until you change it
>
> All three are intentional. **Don't disable safety #2 or #3 without setting them properly first.**

### Steps

1. **Identify ONE host** that has the software you want to find. Note its IP address.
2. Policy → Add → Custom → **WinGet Patcher → Software Removal → 2.1-WinGet Inventory - Find Package ID** → Next
3. Edit the **Access IP** condition: replace `192.0.2.1` with the IP of your one test host
4. Edit the **Script** condition: replace `[INSERT-SOFTWARE-NAME-HERE]` with a partial software name. Examples:
   - `Firefox` — finds Mozilla.Firefox, Mozilla.Firefox.ESR
   - `Shockwave` — finds Adobe.Shockwave
   - `iTunes` — finds Apple.iTunes
   - The match is case-insensitive substring, against BOTH the display name AND the package ID
5. Save → **enable the policy**
6. After a few minutes, open the host's policy detail. Look for lines starting with `WINGET_INVENTORY_MATCH=`:
   ```
   WINGET_INVENTORY_MATCH=Mozilla.Firefox
   WINGET_INVENTORY_MATCH=Mozilla.Firefox.ESR
   ```
7. **Copy the package ID(s)** for use in a removal template (Workflow 5 or 6)
8. **DISABLE this policy** when done. Don't leave it active.

### Why three layers of safety?

This template runs PowerShell on the endpoint. The inventory script itself is read-only — it doesn't modify anything — but running it broadly is wasted execution. The safety pattern enforces "one host, one search term, then disable" as the intended workflow.

---

## Workflow 5: Remove an app using a built-in template

**You want:** Firefox (or Flash, Shockwave, Spotify) gone from your endpoints.

**Prerequisite:** None. Removal templates use Forescout's native "Windows Applications Installed" property for detection — no discovery required.

**You'll use:** Template 2.2, 2.3, 2.4, or 2.5, under Software Removal.

**Time:** ~3 minutes per app.

### Steps (using Firefox as example)

1. Policy → Add → Custom → **WinGet Patcher → Software Removal → 2.2-WinGet Uninstall - Mozilla Firefox** → Next
2. **Scope** to a test segment first — never scope a removal to the whole fleet on the first run
3. (Optional) Rename the policy
4. Finish the wizard
5. **Enable the policy** AND **enable the Run Script action** (both disabled by default)

### What happens

- Forescout evaluates each in-scope endpoint
- If `Windows Applications Installed contains "Firefox"`, the policy fires
- The Run Script action invokes `WingetUninstall.ps1 -PackageId "Mozilla.Firefox"` on the endpoint
- Firefox is removed silently
- Next admission cycle, Firefox is no longer detected, the policy stops matching that endpoint

### Important note on Firefox release vs ESR

The built-in 2.2 template targets `Mozilla.Firefox` (release channel) only. For Firefox ESR, use the 2.6 Custom template with `Mozilla.Firefox.ESR` as the package ID — they're separate WinGet packages.

---

## Workflow 6: Remove an app NOT in the built-in templates

**You want:** to remove some specific software (banned, EOL, or just unwanted).

**Prerequisite:** Workflow 4 done — you've identified the exact package ID via the 2.1 Inventory helper.

**You'll use:** Template 2.6 (Custom Uninstaller), under Software Removal.

**Time:** ~5 minutes.

### Steps

1. Policy → Add → Custom → **WinGet Patcher → Software Removal → 2.6-WinGet Uninstall - Custom (Paste Package ID)** → Next
2. The template ships with `[PASTE-PACKAGE-ID-HERE]` in **two places** — replace BOTH with the package ID you found in Workflow 4:
   - **In the condition:** "Windows Applications Installed contains `[PASTE-PACKAGE-ID-HERE]`" → edit to a recognizable substring of the display name
   - **In the action:** "Run Script: WingetUninstall.ps1 -PackageId `[PASTE-PACKAGE-ID-HERE]`" → edit the command to the exact WinGet package ID
3. **Rename the policy** to include the app name
4. **Scope to a test segment** first
5. Finish, enable both the policy and the action

### Wildcards for app families

Same as for updates: trailing `.*` only. For example:

- Remove all Adobe Flash variants: `Adobe.Flash.*`
- Remove all of a vendor's beta channel: `Vendor.Product.Beta.*`

### Protected packages

The uninstall script has a built-in blocklist that refuses to remove:

- `Microsoft.*` system packages (Windows components, .NET Framework, runtimes)
- `Microsoft.WindowsDefender*`
- `Microsoft.OneDrive` (per policy decision — change in the script if your env wants otherwise)
- Anything that looks like a Windows OS component

If you try to uninstall one of these, the script returns `BLOCKED_NAMESPACE` and exits without touching the endpoint. Fail-safe by design.

---

## Common questions

### "I enabled the policy but nothing happened."

99% of the time: **the Run Script action is still disabled.** Both the policy AND the action have their own enable/disable toggles. Both must be ON.

### "The Discovery property says Count = -1."

`winget.exe` couldn't be located on that endpoint. Most common causes:

- Endpoint doesn't have the Windows App Installer / WinGet installed (older Windows 10 versions)
- Endpoint has WinGet only as a per-user execution alias, and SecureConnector ran as SYSTEM without access (the discovery script's 4-strategy lookup usually handles this, but not always)

Check the endpoint manually with `Get-AppxPackage -Name Microsoft.DesktopAppInstaller`.

### "A patch fired but the app didn't update."

Look at the host's policy detail. The action's output will tell you:

- `WINGET_UPDATE_RESULT=SUCCESS` — succeeded
- `WINGET_UPDATE_RESULT=PARTIAL` — some packages in a wildcard updated, others failed
- `WINGET_UPDATE_RESULT=FAILED` — winget returned a non-zero exit; check `WINGET_UPDATE_MESSAGE`
- `WINGET_UPDATE_RESULT=NOT_FOUND` — winget.exe missing on endpoint

### "The 2.1 Inventory template shows the wrong command (a previous search term)."

You're hitting the Forescout script_result hash cache. Fix:

1. Delete the policy you created from the 2.1 template
2. Remove the WinGet Patcher app (Tools → Options → Connect → Remove)
3. Re-import the WinGet Patcher `.eca`
4. Re-add the 2.1 template fresh

The cache flushes when the app is fully removed.

### "I see all 12 templates flat, no Software Updating / Software Removal subfolders."

Check your Connect Plugin version (Tools → Options → Plugins). The cascading subfolder feature requires **Connect Plugin 2.0.4 or higher**. On older plugin versions everything still works — the templates just appear flat in one list under WinGet Patcher. Upgrade the plugin to get the subfolder layout.

### "I want to patch Office / Edge / system components."

The built-in templates intentionally exclude these. You can use the 1.6 Custom Patcher to target them, but understand the risks:

- **Office:** user data loss risk if a document is open during update
- **Edge:** typically managed by Intune / SCCM / Windows Update
- **System components:** the uninstall script has a hard blocklist; the patcher does not, but be careful

---

## Quick reference card

| Goal | Subfolder → Template | Prereq | Edit before enabling? |
|---|---|---|---|
| See out-of-date apps | Software Updating → 1.1 Discovery | None | Just scope it |
| Patch Chrome | Software Updating → 1.2 | 1.1 running | Just scope it |
| Patch Notepad++ | Software Updating → 1.3 | 1.1 running | Just scope it |
| Patch Acrobat family | Software Updating → 1.4 | 1.1 running | Just scope it |
| Patch VCRedist family | Software Updating → 1.5 | 1.1 running | Just scope it |
| Patch anything else | Software Updating → 1.6 Custom | 1.1 running | Yes — replace placeholder in 2 places |
| Find a package ID for removal | Software Removal → 2.1 Inventory | One test host | Yes — set Access IP and software name |
| Remove Firefox | Software Removal → 2.2 | None | Just scope it |
| Remove Flash | Software Removal → 2.3 | None | Just scope it |
| Remove Shockwave | Software Removal → 2.4 | None | Just scope it |
| Remove Spotify | Software Removal → 2.5 | None | Just scope it |
| Remove anything else | Software Removal → 2.6 Custom | 2.1 done | Yes — replace placeholder in 2 places |

---

## Best practices

1. **Always test in a small scope first.** A 5-host test segment will catch 90% of issues before a fleet-wide rollout.
2. **Watch the first few runs.** Policy detail and host action output will tell you exactly what's happening on each endpoint.
3. **Use the 2.1 Inventory template before custom uninstall.** Don't guess package IDs — verify them.
4. **Disable the 2.1 Inventory policy when you're done with it.** It's a helper, not a monitoring tool.
5. **Don't enable everything at once.** Add templates as needed. Twelve enabled policies that each match dozens of endpoints can saturate HPS in busy environments.
6. **Rename your policies.** "WinGet Update - Custom (Paste Package ID)" is not what you want to see in your policy list three months later. Rename it to the actual app.
