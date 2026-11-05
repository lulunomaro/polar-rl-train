param([Parameter(Mandatory=$true)][int]$TargetPid,[Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference='Stop'
$p=Get-Process -Id $TargetPid
if($p.MainWindowHandle -eq 0){throw 'Owned GUI process has no visible main window yet'}
if($p.MainWindowTitle -notlike '*MOD4v2*'){throw 'Owned main-window title does not identify MOD4v2'}
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class OwnedProbeWindow {
 [StructLayout(LayoutKind.Sequential)] public struct RECT {public int Left;public int Top;public int Right;public int Bottom;}
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd,out RECT rect);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd,int cmd);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd,IntPtr hdc,uint flags);
}
'@
$handle=$p.MainWindowHandle
[void][OwnedProbeWindow]::ShowWindow($handle,9)
$front=[OwnedProbeWindow]::SetForegroundWindow($handle)
$rect=New-Object OwnedProbeWindow+RECT
if(-not [OwnedProbeWindow]::GetWindowRect($handle,[ref]$rect)){throw 'Owned window rectangle unavailable'}
$width=$rect.Right-$rect.Left;$height=$rect.Bottom-$rect.Top
if($width -lt 400 -or $height -lt 300){throw 'Unexpectedly small owned GUI window'}
$picture=Join-Path $OutputDirectory 'WINDOW_PREVIEW.png'
$bmp=New-Object System.Drawing.Bitmap($width,$height)
$graphics=[System.Drawing.Graphics]::FromImage($bmp);$dc=$graphics.GetHdc()
try {$captured=[OwnedProbeWindow]::PrintWindow($handle,$dc,2)} finally {$graphics.ReleaseHdc($dc);$graphics.Dispose()}
if($captured){$bmp.Save($picture,[System.Drawing.Imaging.ImageFormat]::Png)}
$bmp.Dispose()
$r=[ordered]@{epoch=(Get-Date -UFormat %s);pid=$TargetPid;title=$p.MainWindowTitle;window_handle=$handle.ToInt64();visible=[OwnedProbeWindow]::IsWindowVisible($handle);width=$width;height=$height;foreground_requested=$front;own_window_print_capture=$captured;capture_path=if($captured){$picture}else{$null};source_assets_modified=$false;training_started=$false;unrelated_window_or_desktop_capture=$false}
if($captured){$r['capture_sha256']=(Get-FileHash -LiteralPath $picture -Algorithm SHA256).Hash.ToLowerInvariant()}
$r|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $OutputDirectory 'WINDOW_VERIFICATION.json') -Encoding utf8
$r|ConvertTo-Json -Depth 6
