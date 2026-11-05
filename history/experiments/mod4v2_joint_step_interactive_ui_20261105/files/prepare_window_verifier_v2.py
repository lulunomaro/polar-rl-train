"""Resolve the owned Windows venv redirector child; do not relaunch or alter GUI."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent;p=D/'verify_window_v2.ps1';assert not p.exists();s=(D/'verify_window.ps1').read_text(encoding='utf8')
s=s.replace('param([Parameter(Mandatory=$true)][int]$TargetPid,','param([Parameter(Mandatory=$true)][int]$LauncherPid,[Parameter(Mandatory=$true)][int]$TargetPid,')
a="$p=Get-Process -Id $TargetPid";assert s.count(a)==1;s=s.replace(a,"$owned=Get-CimInstance Win32_Process -Filter \"ProcessId=$TargetPid\"\nif($owned.ParentProcessId -ne $LauncherPid -or $owned.CommandLine -notlike '*mod4v2_joint_step_probe_20261105*joint_step_viewer.py*'){throw 'Target is not the exact owned GUI redirector child'}\n$p=Get-Process -Id $TargetPid")
a='pid=$TargetPid;title=';assert s.count(a)==1;s=s.replace(a,'pid=$TargetPid;launcher_pid=$LauncherPid;owned_redirector_child_verified=$true;title=');p.write_text(s,encoding='utf8',newline='\n')
(D/'WINDOW_VERIFIER_V1_REDIRECTOR_ERRATUM.json').write_text(json.dumps(dict(epoch=time.time(),original_verifier='verify_window.ps1',error='Owned GUI process has no visible main window yet',launcher_pid=73384,actual_own_GUI_child_pid=75688,reason='Windows venv pythonw redirector starts an owned base-runtime pythonw child; window belongs to child, not launcher',GUI_failed=False,GUI_source_or_pose_changed=False,relaunches=0,fix='New verifier checks exact child ParentProcessId+script then captures only that window'),indent=2),encoding='utf8')
print('Prepared child-aware verifier only; no GUI restart or pose changes')
