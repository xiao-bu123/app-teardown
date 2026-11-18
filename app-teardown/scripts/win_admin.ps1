param(
    [Parameter(Mandatory = $true)][string]$Script,
    [string]$OutLog = ""
)

# Launch another PowerShell script elevated, so its input reaches an
# admin-privileged client (UIPI otherwise silently drops clicks/keys).
#
#   .\win_admin.ps1 -Script .\capture.ps1 -OutLog .\admin.log
#
# Elevated processes cannot write to your console, so the child redirects its
# own output to OutLog; this script waits for the file to settle and prints it.

if ($OutLog -eq "") {
    $OutLog = Join-Path (Split-Path -Parent $Script) ("admin_" + [guid]::NewGuid().ToString("N").Substring(0, 8) + ".log")
}
$OutLog = [System.IO.Path]::GetFullPath($OutLog)
if (Test-Path $OutLog) { Remove-Item $OutLog -Force }

$child = @"
& '$([System.IO.Path]::GetFullPath($Script))' *> '$OutLog'
"@
$enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($child))

Start-Process powershell -Verb RunAs -ArgumentList @(
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $enc
) | Out-Null

$deadline = (Get-Date).AddSeconds(120)
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 500
    if (Test-Path $OutLog) {
        $len = (Get-Item $OutLog).Length
        Start-Sleep -Milliseconds 400
        if ((Get-Item $OutLog).Length -eq $len) { break }
    }
}

if (Test-Path $OutLog) { Get-Content $OutLog } else { "no output at $OutLog" }
