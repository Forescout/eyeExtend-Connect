@echo off
setlocal
set "CONNECTAD_COLLECTOR_PATH=%~f0"
powershell.exe -NoLogo -NoProfile -NonInteractive -Command "$ErrorActionPreference='Stop';$text=[IO.File]::ReadAllText($env:CONNECTAD_COLLECTOR_PATH);$marker='#'+' CONNECTAD_POWERSHELL'; & ([ScriptBlock]::Create($text.Substring($text.IndexOf($marker)+$marker.Length)))"
exit /b %errorlevel%
# CONNECTAD_POWERSHELL
# Windows PowerShell 5.1, Windows endpoints only. No RSAT or stored credentials.
# Dot-source with -LibraryOnly for local tests; normal execution prints one JSON line.
param([switch]$LibraryOnly)
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Initialize-ConnectADWts {
    if (-not ('ConnectAD.Wts' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Runtime.InteropServices;
namespace ConnectAD {
    public static class Wts {
        [StructLayout(LayoutKind.Sequential)]
        private struct Session { public int Id; public IntPtr Station; public int State; }
        [DllImport("wtsapi32.dll", CharSet=CharSet.Unicode, ExactSpelling=true, SetLastError=true)]
        private static extern bool WTSEnumerateSessionsW(IntPtr server, int reserved,
            int version, out IntPtr sessions, out int count);
        [DllImport("wtsapi32.dll", CharSet=CharSet.Unicode, ExactSpelling=true, SetLastError=true)]
        private static extern bool WTSQuerySessionInformationW(IntPtr server, int id,
            int info, out IntPtr buffer, out int bytes);
        [DllImport("wtsapi32.dll")]
        private static extern void WTSFreeMemory(IntPtr memory);
        private static string Query(int id, int info) {
            IntPtr buffer; int bytes;
            if (!WTSQuerySessionInformationW(IntPtr.Zero, id, info, out buffer, out bytes))
                throw new Win32Exception(Marshal.GetLastWin32Error());
            try { return bytes > 2 ? Marshal.PtrToStringUni(buffer) : ""; }
            finally { WTSFreeMemory(buffer); }
        }
        public static bool IsLoggedOnSession(int id, int state) {
            // Disconnected RDP/locked sessions remain signed in until logoff.
            // WTSActive=0, WTSDisconnected=4; never include service session 0.
            return id != 0 && (state == 0 || state == 4);
        }
        public static string[] LoggedOnUsers() {
            IntPtr sessions; int count;
            if (!WTSEnumerateSessionsW(IntPtr.Zero, 0, 1, out sessions, out count))
                throw new Win32Exception(Marshal.GetLastWin32Error());
            var users = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            try {
                int size = Marshal.SizeOf(typeof(Session));
                for (int i=0; i<count; i++) {
                    var session = (Session)Marshal.PtrToStructure(IntPtr.Add(sessions, i*size), typeof(Session));
                    if (!IsLoggedOnSession(session.Id, session.State)) continue;
                    string user = Query(session.Id, 5); // WTSUserName
                    string domain = Query(session.Id, 7); // WTSDomainName
                    if (user.Length == 0) continue;
                    if (domain.Length == 0) throw new InvalidOperationException("Missing session domain");
                    users.Add(domain + "\\" + user);
                }
            } finally { WTSFreeMemory(sessions); }
            var result = new string[users.Count]; users.CopyTo(result); Array.Sort(result);
            return result;
        }
    }
    public static class DomainLocator {
        [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
        private struct ControllerInfo {
            public string ControllerName; public string ControllerAddress;
            public uint AddressType; public Guid DomainGuid;
            public string DomainName; public string ForestName; public uint Flags;
            public string SiteName; public string ClientSiteName;
        }
        [DllImport("netapi32.dll", CharSet=CharSet.Unicode, ExactSpelling=true)]
        private static extern int DsGetDcNameW(string computer, string domain, IntPtr guid,
            string site, uint flags, out IntPtr info);
        [DllImport("netapi32.dll", ExactSpelling=true)]
        private static extern int NetApiBufferFree(IntPtr buffer);
        public static string DnsName(string domain) {
            IntPtr info;
            // DS_RETURN_DNS_NAME | DS_DIRECTORY_SERVICE_REQUIRED; explicitly flat for NetBIOS input.
            uint flags = 0x40000010;
            if (domain.IndexOf('.') < 0) flags |= 0x00010000; // DS_IS_FLAT_NAME
            int status = DsGetDcNameW(null, domain, IntPtr.Zero, null, flags, out info);
            if (status != 0) throw new Win32Exception(status);
            try {
                var data = (ControllerInfo)Marshal.PtrToStructure(info, typeof(ControllerInfo));
                if (String.IsNullOrEmpty(data.DomainName)) throw new InvalidOperationException("Missing DNS domain");
                return data.DomainName;
            } finally { NetApiBufferFree(info); }
        }
    }
}
'@
    }
}

function Get-ConnectADLoggedOnUsers {
    Initialize-ConnectADWts
    [ConnectAD.Wts]::LoggedOnUsers()
}

function ConvertTo-ConnectADFilterValue([string]$Value) {
    # Escape every UTF-8 byte: no LDAP-filter metacharacter or Unicode ambiguity.
    -join ([Text.Encoding]::UTF8.GetBytes($Value) | ForEach-Object { '\{0:x2}' -f $_ })
}

function Get-ConnectADDomain([string]$Name) {
    Add-Type -AssemblyName System.DirectoryServices
    if ([string]::IsNullOrEmpty($Name)) {
        # Machine's joined domain, independent of the script's service identity.
        return [DirectoryServices.ActiveDirectory.Domain]::GetComputerDomain()
    }
    # WTS reports a NetBIOS domain; DirectoryContext expects a DNS domain name.
    Initialize-ConnectADWts
    $dnsDomain = [ConnectAD.DomainLocator]::DnsName($Name)
    $context = New-Object DirectoryServices.ActiveDirectory.DirectoryContext('Domain', $dnsDomain)
    [DirectoryServices.ActiveDirectory.Domain]::GetDomain($context)
}

function Find-ConnectADAccount($Domain, [string]$Filter) {
    $root = $null; $search = $null; $rows = $null
    try {
        $root = $Domain.GetDirectoryEntry()
        # Windows integrated authentication, with signing and sealing. No simple bind.
        $root.AuthenticationType = [DirectoryServices.AuthenticationTypes]::Secure -bor
            [DirectoryServices.AuthenticationTypes]::Signing -bor [DirectoryServices.AuthenticationTypes]::Sealing
        $search = New-Object DirectoryServices.DirectorySearcher($root)
        $search.Filter = $Filter
        $search.ReferralChasing = [DirectoryServices.ReferralChasingOption]::None
        $search.SizeLimit = 2
        $search.ClientTimeout = [TimeSpan]::FromSeconds(10)
        $search.ServerTimeLimit = [TimeSpan]::FromSeconds(10)
        foreach ($property in @('objectGUID', 'sAMAccountName', 'userPrincipalName')) {
            [void]$search.PropertiesToLoad.Add($property)
        }
        $rows = $search.FindAll()
        if ($rows.Count -ne 1) { throw 'AD account missing or ambiguous' }
        $properties = $rows[0].Properties
        if ($properties['objectguid'].Count -ne 1) { throw 'AD objectGUID missing' }
        $bytes = [byte[]]$properties['objectguid'][0]
        if ($bytes.Length -ne 16) { throw 'AD objectGUID is not 16 bytes' }
        $guid = New-Object Guid (,$bytes)
        if ($guid -eq [Guid]::Empty) { throw 'AD objectGUID is empty' }
        $upn = ''
        if ($properties['userprincipalname'].Count -eq 1) { $upn = [string]$properties['userprincipalname'][0] }
        return @{status='ok'; guid=$guid.ToString('D'); domain=$Domain.Name;
            sam=[string]$properties['samaccountname'][0]; upn=$upn}
    } finally {
        if ($null -ne $rows) { $rows.Dispose() }
        if ($null -ne $search) { $search.Dispose() }
        if ($null -ne $root) { $root.Dispose() }
    }
}

function Get-ConnectADComputerRecord {
    $domain = $null
    try {
        $system = Get-CimInstance -ClassName Win32_ComputerSystem
        if (-not $system.PartOfDomain) { return @{status='not_domain_joined'; guid=''} }
        $domain = Get-ConnectADDomain ''
        $sam = ConvertTo-ConnectADFilterValue ($system.Name + '$')
        $record = Find-ConnectADAccount $domain ('(&(objectCategory=computer)(sAMAccountName=' + $sam + '))')
        # UPN/session identity describe the user evidence, not this computer.
        [void]$record.Remove('upn')
        return $record
    } catch {
        # Stable status on stdout, no exceptions/credentials leaking into the result.
        return @{status='error'; guid=''}
    } finally {
        if ($null -ne $domain) { $domain.Dispose() }
    }
}

function Get-ConnectADUserSidFilter([string]$DomainName, [string]$UserName) {
    $account = New-Object Security.Principal.NTAccount($DomainName, $UserName)
    $sid = $account.Translate([Security.Principal.SecurityIdentifier])
    if (-not $sid.IsAccountSid()) { throw 'Session identity is not an account SID' }
    $bytes = New-Object byte[] $sid.BinaryLength
    $sid.GetBinaryForm($bytes, 0)
    -join ($bytes | ForEach-Object { '\{0:x2}' -f $_ })
}

function Get-ConnectADUserRecord {
    $domain = $null
    try {
        $users = @(Get-ConnectADLoggedOnUsers)
        if ($users.Count -eq 0) { return @{status='no_active_user'; guid=''} }
        if ($users.Count -ne 1) { return @{status='multiple_active_users'; guid=''} }
        $identity = $users[0]
        $parts = $identity.Split('\')
        if ($parts.Length -ne 2 -or [string]::IsNullOrEmpty($parts[1])) { throw 'Invalid session identity' }
        if ($parts[0] -ieq [Environment]::MachineName -or $parts[0] -eq '.' -or
            $parts[0] -in @('AzureAD', 'MicrosoftAccount', 'NT AUTHORITY', 'Window Manager', 'Font Driver Host')) {
            return @{status='not_ad_user'; guid=''; identity=$identity}
        }
        # Resolve the actual session account SID, not USERNAME/USERDOMAIN or the process token.
        $filterSid = Get-ConnectADUserSidFilter $parts[0] $parts[1]
        $domain = Get-ConnectADDomain $parts[0]
        $record = Find-ConnectADAccount $domain ('(&(objectCategory=person)(objectClass=user)(objectSid=' + $filterSid + '))')
        $record.identity = $identity
        # Refuse a logoff/switch while the directory request was in flight.
        $after = @(Get-ConnectADLoggedOnUsers)
        if ($after.Count -ne 1 -or $after[0] -ine $identity) { return @{status='session_changed'; guid=''} }
        return $record
    } catch {
        return @{status='error'; guid=''}
    } finally {
        if ($null -ne $domain) { $domain.Dispose() }
    }
}

function Get-ConnectADGuidResult {
    # Timestamp the beginning: slow collection cannot make old evidence appear new.
    $observed = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    $computer = Get-ConnectADComputerRecord
    $user = Get-ConnectADUserRecord
    [ordered]@{schema='connectad-guid-v1'; collected_at=$observed; computer=$computer; user=$user} |
        ConvertTo-Json -Depth 4 -Compress
}

if (-not $LibraryOnly) { Get-ConnectADGuidResult }
