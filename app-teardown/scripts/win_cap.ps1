param(
  [string]$out = "shot.png",
  [string]$class = "",
  [switch]$full,
  [switch]$list
)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;using System.Text;using System.Collections.Generic;using System.Runtime.InteropServices;
public class WC {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
  [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h,StringBuilder s,int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetSystemMetrics(int i);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
  public static IntPtr Find(string cls) {
    IntPtr f = IntPtr.Zero;
    EnumWindows((h,l) => {
      if (!IsWindowVisible(h)) return true;
      var c = new StringBuilder(256); GetClassName(h,c,256);
      if (c.ToString().IndexOf(cls, StringComparison.OrdinalIgnoreCase) >= 0) {
        var t = new StringBuilder(512); GetWindowText(h,t,512);
        if (t.ToString().Length > 0) { f = h; return false; }
      }
      return true;
    }, IntPtr.Zero);
    return f;
  }
  public static int[] Rect(IntPtr h) { RECT r; GetWindowRect(h, out r); return new int[]{r.L,r.T,r.R,r.B}; }
  public static List<string> All() {
    var res = new List<string>();
    EnumWindows((h,l) => {
      if (!IsWindowVisible(h)) return true;
      var t = new StringBuilder(512); GetWindowText(h,t,512);
      var c = new StringBuilder(256); GetClassName(h,c,256);
      RECT r; GetWindowRect(h, out r);
      string title = t.ToString();
      if (title.Length > 0 || c.ToString().IndexOf("FLUTTER", StringComparison.OrdinalIgnoreCase) >= 0)
        res.Add(string.Format("{0}|{1}|{2}|{3},{4},{5},{6}", h.ToInt64(), c, title, r.L,r.T,r.R,r.B));
      return true;
    }, IntPtr.Zero);
    return res;
  }
}
"@
[void][WC]::SetProcessDPIAware()

if ($list) { [WC]::All() | ForEach-Object { $_ }; exit 0 }

if ($full) {
  $w = [WC]::GetSystemMetrics(0); $hgt = [WC]::GetSystemMetrics(1)
  $bmp = New-Object System.Drawing.Bitmap($w, $hgt)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size($w, $hgt)))
} else {
  if ($class -eq "") { Write-Error "need -class or -full"; exit 1 }
  $h = [WC]::Find($class)
  if ($h -eq [IntPtr]::Zero) { Write-Error "window not found: $class"; exit 1 }
  [void][WC]::SetForegroundWindow($h); [void][WC]::BringWindowToTop($h)
  Start-Sleep -Milliseconds 300
  $r = [WC]::Rect($h)
  $w = $r[2] - $r[0]; $hgt = $r[3] - $r[1]
  if ($w -le 0 -or $hgt -le 0) { Write-Error "bad rect $($r -join ',')"; exit 1 }
  $bmp = New-Object System.Drawing.Bitmap($w, $hgt)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($r[0], $r[1], 0, 0, (New-Object System.Drawing.Size($w, $hgt)))
}
$g.Dispose()
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output ("SAVED {0} {1}x{2}" -f $out, $w, $hgt)
