"""Verify117 console within its real interactive session, not SSH's session0.
One short no-trigger diagnostic task; does not restart the dashboard or touch jobs.
"""
from pathlib import Path
import base64,json,runpy,time,traceback
HERE=Path(__file__).resolve().parent
ns=runpy.run_path(str(HERE/'refresh_serial_dashboard_v5.py'),run_name='definitions_only')['ns']
R=HERE/'reports/selected_v5';marker=R/'INTERACTIVE_SESSION_CONSOLE_VERIFY_CONSUMED.json';assert not marker.exists()
marker.write_text(json.dumps(dict(epoch=time.time(),no_dashboard_task_restart=True,only_known117_window=True)),encoding='utf8')
source=r'''from pathlib import Path
import ctypes,json,time,psutil
p=Path(__file__).resolve().parent;r=json.loads((p/'TERMINAL_ACTUAL_STARTED.json').read_bytes())
proc=psutil.Process(r['pid']);assert proc.create_time()==r['creation'] and proc.exe()==r['exe'] and proc.cmdline()==r['argv'] and proc.cwd()==r['cwd']
u=ctypes.WinDLL('user32');k=ctypes.WinDLL('kernel32');u.IsWindowVisible.argtypes=[ctypes.c_void_p];u.GetClassNameW.argtypes=[ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_int];u.GetWindowTextW.argtypes=[ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_int]
hwnd=r['own_console_handle'];title=ctypes.create_unicode_buffer(2048);klass=ctypes.create_unicode_buffer(256);u.GetClassNameW(hwnd,klass,256);u.GetWindowTextW(hwnd,title,2048)
session=ctypes.c_ulong();assert k.ProcessIdToSessionId(psutil.Process().pid,ctypes.byref(session))
out=dict(epoch=time.time(),same_interactive_session=session.value==r['session_id'],verifier_session=session.value,terminal_session=r['session_id'],original_terminal_identity_exact=True,known_console_handle=hwnd,known_console_visible=bool(u.IsWindowVisible(hwnd)),known_console_title=title.value,known_console_class=klass.value,no_window_mutation=True,no_training_action=True)
(p/'ACTUAL_INTERACTIVE_SESSION_CONSOLE_VISIBILITY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
'''
_,secret,_=ns['credentials']();c=ns['connect249'](secret)
try:
    sf=c.open_sftp()
    try:
        with sf.open(ns['DEST']+'/verify_same_interactive_session.py','wb') as f:f.write(source.encode())
    finally:sf.close()
    name=ns['TASK']+'_VerifySession'
    setup="$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue';$name='"+name+"';if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Own verifier already consumed'};$a=New-ScheduledTaskAction -Execute 'D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe' -Argument '-B -X utf8 \""+ns['DEST']+"/verify_same_interactive_session.py\"' -WorkingDirectory '"+ns['DEST']+"';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::FromMinutes(1)) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $name -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $name;[PSCustomObject]@{started=$true;no_dashboard_restart=$true}|ConvertTo-Json -Compress"
    actual=ns['ps249'](c,setup);sf=c.open_sftp()
    try:
        for _ in range(25):
            try:
                with sf.open(ns['DEST']+'/ACTUAL_INTERACTIVE_SESSION_CONSOLE_VISIBILITY.json','rb') as f:result=json.loads(f.read())
                break
            except FileNotFoundError:time.sleep(1)
        else:raise TimeoutError('Own short verifier did not publish; no automatic relaunch')
    finally:sf.close()
    result['oneoff_verifier_task']=dict(name=name,**actual);ns['put']('ACTUAL3060_TERMINAL_VISIBLE_IN_INTERACTIVE_SESSION.json',result);print(json.dumps(result,ensure_ascii=False))
finally:c.close();secret=None
