Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class WindowHelper {
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
'@

function Show-OpenFileDialog {
    <#
    .SYNOPSIS
    Shows the Windows OpenFileDialog and returns the user-selected file path(s).

    .DESCRIPTION
    For detailed information on the available parameters, see the OpenFileDialog
    class documentation online at https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.openfiledialog?view=netframework-4.8.1
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param (
        [Parameter()]
        [bool]
        $AddExtension = $true,

        [Parameter()]
        [bool]
        $AutoUpgradeEnabled = $true,

        [Parameter()]
        [bool]
        $CheckFileExists = $true,

        [Parameter()]
        [bool]
        $CheckPathExists = $true,

        [Parameter()]
        [string]
        $DefaultExt,

        [Parameter()]
        [bool]
        $DereferenceLinks = $true,

        # Filter for specific file types. Example syntax: 'Excel files (*.xlsx)|*.xlsx|All files (*.*)|*.*'
        [Parameter()]
        [string]
        $Filter,

        [Parameter()]
        [string]
        $InitialDirectory,

        [Parameter()]
        [bool]
        $Multiselect,

        [Parameter()]
        [bool]
        $ReadOnlyChecked,

        [Parameter()]
        [bool]
        $RestoreDirectory,

        [Parameter()]
        [bool]
        $ShowHelp,

        [Parameter()]
        [bool]
        $ShowReadOnly,

        [Parameter()]
        [bool]
        $SupportMultiDottedExtensions,

        [Parameter()]
        [string]
        $Title,

        [Parameter()]
        [bool]
        $ValidateNames
    )

    process {
        $params = @{
            AddExtension                 = $AddExtension
            AutoUpgradeEnabled           = $AutoUpgradeEnabled
            CheckFileExists              = $CheckFileExists
            CheckPathExists              = $CheckPathExists
            DefaultExt                   = $DefaultExt
            DereferenceLinks             = $DereferenceLinks
            Filter                       = $Filter
            InitialDirectory             = $InitialDirectory
            Multiselect                  = $Multiselect
            ReadOnlyChecked              = $ReadOnlyChecked
            RestoreDirectory             = $RestoreDirectory
            ShowHelp                     = $ShowHelp
            ShowReadOnly                 = $ShowReadOnly
            SupportMultiDottedExtensions = $SupportMultiDottedExtensions
            Title                        = $Title
            ValidateNames                = $ValidateNames
        }

        [System.Windows.Forms.Form]$form = $null
        [System.Windows.Forms.OpenFileDialog]$dialog = $null
        try {
            $form = [System.Windows.Forms.Form]@{ TopMost = $true }
            $dialog = [System.Windows.Forms.OpenFileDialog]$params
            $CustomPlaces | ForEach-Object {
                if ($null -eq $_) {
                    return
                }
                if (($id = $_ -as [guid])) {
                    $dialog.CustomPlaces.Add($id)
                } else {
                    $dialog.CustomPlaces.Add($_)
                }
            }
            $null = [WindowHelper]::SetForegroundWindow($form.Handle)
            if ($dialog.ShowDialog($form) -eq 'OK') {
                if ($MultiSelect) {
                    $dialog.FileNames
                } else {
                    $dialog.FileName
                }
            } else {
                Write-Error -Message 'No file(s) selected.'
            }
        } finally {
            if ($dialog) {
                $dialog.Dispose()
            }
            if ($form) {
                $form.Dispose()
            }
        }
    }
}

function Show-SaveFileDialog {
    <#
    .SYNOPSIS
    Shows the Windows SaveFileDialog and returns the user-provided file path.

    .DESCRIPTION
    For detailed information on the available parameters, see the SaveFileDialog
    class documentation online at https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.savefiledialog?view=netframework-4.8.1
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param (
        [Parameter()]
        [bool]
        $AddExtension = $true,

        [Parameter()]
        [bool]
        $AutoUpgradeEnabled = $true,

        [Parameter()]
        [bool]
        $CheckFileExists = $false,

        [Parameter()]
        [bool]
        $CheckPathExists = $true,

        [Parameter()]
        [bool]
        $CreatePrompt,

        [Parameter()]
        [string[]]
        $CustomPlaces,

        [Parameter()]
        [string]
        $DefaultExt,

        [Parameter()]
        [bool]
        $DereferenceLinks = $true,

        # Filter for specific file types. Example syntax: 'Excel files (*.xlsx)|*.xlsx|All files (*.*)|*.*'
        [Parameter()]
        [string]
        $Filter,

        [Parameter()]
        [string]
        $InitialDirectory,

        [Parameter()]
        [bool]
        $OverwritePrompt = $true,

        [Parameter()]
        [bool]
        $RestoreDirectory,

        [Parameter()]
        [bool]
        $ShowHelp,

        [Parameter()]
        [bool]
        $SupportMultiDottedExtensions,

        [Parameter()]
        [string]
        $Title,

        [Parameter()]
        [bool]
        $ValidateNames = $true
    )

    process {
        $params = @{
            AddExtension                 = $AddExtension
            AutoUpgradeEnabled           = $AutoUpgradeEnabled
            CheckFileExists              = $CheckFileExists
            CheckPathExists              = $CheckPathExists
            CreatePrompt                 = $CreatePrompt
            DefaultExt                   = $DefaultExt
            DereferenceLinks             = $DereferenceLinks
            Filter                       = $Filter
            InitialDirectory             = $InitialDirectory
            OverwritePrompt              = $OverwritePrompt
            RestoreDirectory             = $RestoreDirectory
            ShowHelp                     = $ShowHelp
            SupportMultiDottedExtensions = $SupportMultiDottedExtensions
            Title                        = $Title
            ValidateNames                = $ValidateNames
        }

        [System.Windows.Forms.Form]$form = $null
        [System.Windows.Forms.SaveFileDialog]$dialog = $null
        try {
            $form = [System.Windows.Forms.Form]@{ TopMost = $true }
            $dialog = [System.Windows.Forms.SaveFileDialog]$params
            $CustomPlaces | ForEach-Object {
                if ($null -eq $_) {
                    return
                }
                if (($id = $_ -as [guid])) {
                    $dialog.CustomPlaces.Add($id)
                } else {
                    $dialog.CustomPlaces.Add($_)
                }
            }

            $null = [WindowHelper]::SetForegroundWindow($form.Handle)
            if (($dialogResult = $dialog.ShowDialog($form)) -eq 'OK') {
                $dialog.FileName
            } else {
                Write-Error -Message "DialogResult: $dialogResult"
            }
        } finally {
            if ($dialog) {
                $dialog.Dispose()
            }
            if ($form) {
                $form.Dispose()
            }
        }
    }
}

# Ask user for powershell script to turn into One Liner BAT
$openPath = Show-OpenFileDialog -Title ‘Select Powershell Script to Encode to One-Liner’ -Filter ‘Powershell Script (*.ps1)|*.ps1’

# Get contents and convert to one liner
$s = Get-Content $openPath | Out-String
$j = [PSCustomObject]@{
  "Script" =  [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($s))
} | ConvertTo-Json -Compress
$oneline = "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(('" + $j + "' | ConvertFrom-Json).Script)) | iex"
$c = [convert]::ToBase64String([System.Text.encoding]::Unicode.GetBytes($oneline))

# Ask user where they want to save the bat
$savePath = Show-SaveFileDialog -Title ‘Select where to save One-Liner BAT file’ -Filter ‘BAT Script (*.bat)|*.bat’

# Save bat file
("Powershell -NoLogo -NonInteractive -NoProfile -ExecutionPolicy Bypass -Encoded " + $c) | Out-File -Encoding Default $savePath