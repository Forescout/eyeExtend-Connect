for /F "tokens=3" %%A in ('reg query  "HKLM\SOFTWARE\Wow6432Node\AdventNet\DesktopCentral\DCAgent\SystemDetails" /v "DCAgentResourceID"') DO (Echo %%A)
