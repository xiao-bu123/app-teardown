param(
    [ValidateSet("list", "capture", "click", "rect", "focus")]
    [string]$Action = "list",
    [int]$Hwnd = 0,
    [int]$X = -1,
    [int]$Y = -1,
    [string]$Out = "shot.png",
    [string]$TitleLike = "",
    [switch]$RelativeMove
)

# Windows desktop client capture/click helper.
#   .\win_ctl.ps1 -Action list
#   .\win_ctl.ps1 -Action capture -Hwnd 123456 -Out .\L0_home.png
#   .\win_ctl.ps1 -Action click   -Hwnd 123456 -X 120 -Y 340
# X/Y are relative to the window's top-left corner. Prefer clicking with the
# same privilege level as the target process (see win_admin.ps1), otherwise
# UIPI silently drops the input and nothing happens.

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

if (-not ("Win32" -as [type])) {
    Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public class Win32 {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr p);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT p);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();

    public struct RECT { public int Left, Top, Right, Bottom; }
    public struct POINT { public int X, Y; }
}
"@
}

[void][Win32]::SetProcessDPIAware()

function Get-Rect([IntPtr]$h) {
    $r = New-Object Win32+RECT
    [void][Win32]::GetWindowRect($h, [ref]$r)
    return $r
}

function Test-Offscreen($r) {
    # Minimized windows report -32000/-32000: neither capture nor click can work.
    return ($r.Left -le -30000 -or $r.Top -le -30000)
}

function Get-ClickTarget([IntPtr]$h, [int]$rx, [int]$ry) {
    $r = Get-Rect $h
    return @($r.Left + $rx, $r.Top + $ry)
}

function Move-Cursor([int]$x, [int]$y) {
    if ([Win32]::SetCursorPos($x, $y)) { return $true }
    # Fallback: relative small steps, re-reading the cursor each time.
    $p = New-Object Win32+POINT
    for ($i = 0; $i -lt 40; $i++) {
        [void][Win32]::GetCursorPos([ref]$p)
        $dx = $x - $p.X; $dy = $y - $p.Y
        if ([math]::Abs($dx) -le 1 -and [math]::Abs($dy) -le 1) { return $true }
        $sx = [math]::Sign($dx) * [math]::Min(40, [math]::Abs($dx))
        $sy = [math]::Sign($dy) * [math]::Min(40, [math]::Abs($dy))
        [Win32]::mouse_event(0x0001, $sx, $sy, 0, [IntPtr]::Zero)
        Start-Sleep -Milliseconds 15
    }
    return $false
}

switch ($Action) {
    "list" {
        $rows = New-Object System.Collections.ArrayList
        $cb = [Win32+EnumWindowsProc]{
            param($h, $p)
            if (-not [Win32]::IsWindowVisible($h)) { return $true }
            $sb = New-Object System.Text.StringBuilder 512
            [void][Win32]::GetWindowText($h, $sb, 512)
            $title = $sb.ToString()
            if ([string]::IsNullOrWhiteSpace($title)) { return $true }
            $cb2 = New-Object System.Text.StringBuilder 256
            [void][Win32]::GetClassName($h, $cb2, 256)
            $procId = 0
            [void][Win32]::GetWindowThreadProcessId($h, [ref]$procId)
            $pname = ""
            try { $pname = (Get-Process -Id $procId -ErrorAction Stop).ProcessName } catch {}
            $r = Get-Rect $h
            if ($TitleLike -ne "" -and $title -notlike "*$TitleLike*") { return $true }
            [void]$rows.Add([pscustomobject]@{
                hwnd = $h.ToInt64(); pid = $procId; proc = $pname
                title = $title; cls = $cb2.ToString()
                w = $r.Right - $r.Left; h = $r.Bottom - $r.Top
                left = $r.Left; top = $r.Top
            })
            return $true
        }
        [void][Win32]::EnumWindows($cb, [IntPtr]::Zero)
        $rows | Sort-Object proc, title | Format-Table -AutoSize
    }

    "rect" {
        if ($Hwnd -eq 0) { throw "need -Hwnd" }
        Get-Rect ([IntPtr]$Hwnd) | Format-List
    }

    "focus" {
        if ($Hwnd -eq 0) { throw "need -Hwnd" }
        [void][Win32]::SetForegroundWindow([IntPtr]$Hwnd)
        "focused $Hwnd"
    }

    "click" {
        if ($Hwnd -eq 0 -or $X -lt 0 -or $Y -lt 0) { throw "need -Hwnd -X -Y" }
        $h = [IntPtr]$Hwnd
        $r0 = Get-Rect $h
        if (Test-Offscreen $r0) { throw "window is minimized/offscreen; restore it before clicking" }
        [void][Win32]::SetForegroundWindow($h)
        Start-Sleep -Milliseconds 120
        $t = Get-ClickTarget $h $X $Y
        $ok = Move-Cursor $t[0] $t[1]
        Start-Sleep -Milliseconds 80
        [Win32]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)   # LEFTDOWN
        Start-Sleep -Milliseconds 40
        [Win32]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)   # LEFTUP
        "click at $($t[0]),$($t[1]) moved=$ok"
    }

    "capture" {
        if ($Hwnd -eq 0) { throw "need -Hwnd" }
        $h = [IntPtr]$Hwnd
        $r = Get-Rect $h
        if (Test-Offscreen $r) { throw "window is minimized/offscreen; restore it before capture" }
        $w = $r.Right - $r.Left; $hh = $r.Bottom - $r.Top
        if ($w -le 0 -or $hh -le 0) { throw "window has no area" }
        $bmp = New-Object System.Drawing.Bitmap $w, $hh
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $hdc = $g.GetHdc()
        $done = [Win32]::PrintWindow($h, $hdc, 2)          # PW_RENDERFULLCONTENT
        $g.ReleaseHdc($hdc)
        $g.Dispose()

        # Fallback for windows that render black: copy from screen while on top.
        $bright = 0
        for ($ix = 0; $ix -lt $w; $ix += 60) {
            for ($iy = 0; $iy -lt $hh; $iy += 60) {
                $c = $bmp.GetPixel($ix, $iy)
                $bright += ($c.R + $c.G + $c.B)
            }
        }
        if ((-not $done) -or $bright -lt 30) {
            [void][Win32]::SetForegroundWindow($h)
            Start-Sleep -Milliseconds 250
            $bmp2 = New-Object System.Drawing.Bitmap $w, $hh
            $g2 = [System.Drawing.Graphics]::FromImage($bmp2)
            $g2.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size $w, $hh))
            $g2.Dispose()
            $bmp.Dispose()
            $bmp = $bmp2
        }
        $bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
        $bmp.Dispose()
        "saved $Out ${w}x${hh}"
    }
}
