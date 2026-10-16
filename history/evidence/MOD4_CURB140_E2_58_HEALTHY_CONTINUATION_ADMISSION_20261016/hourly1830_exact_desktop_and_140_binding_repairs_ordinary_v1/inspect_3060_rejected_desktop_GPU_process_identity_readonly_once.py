"""Resolve actual WDDM GPU process role without touching the application."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';s=importlib.util.spec_from_file_location('guardtransport',W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014/transport_249_bodyframe_current_terminal_role_v3.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
READ=r'''
from pathlib import Path
import json,time,psutil,hashlib
p=psutil.Process(38888);assert abs(p.create_time()-1792128107.6247945)<1e-4;exe=Path(p.exe());assert str(exe).casefold()==r'C:\Users\lulunomaro\AppData\Local\Programs\DeepSeek Harness\DeepSeek Harness.exe'.casefold();args=p.cmdline();assert '--type=gpu-process' in args
def row(p):return dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),exe=p.exe(),parent=p.ppid())
parent=p.parent();assert parent and Path(parent.exe()).resolve()==exe.resolve() and not any(x.startswith('--type=') for x in parent.cmdline());children=parent.children(recursive=True);desc=[]
for c in children:
 v=row(c);assert Path(c.exe()).resolve()==exe.resolve() or c.name().lower()=='crashpad_handler.exe';desc.append(v)
raw=exe.read_bytes();print(json.dumps(dict(epoch=time.time(),GPU_process=row(p),parent=row(parent),children=desc,binary_path=str(exe),binary_bytes=len(raw),binary_SHA=hashlib.sha256(raw).hexdigest(),actual_Electron_GPU_child_of_same_desktop_main=True,no_Python_Kit_or_training_child=True,no_process_GPU_or_UI_mutation=True,classification_scope='Exact currently observed process identities and binary only, not a wildcard allowlist')))
'''
def main():
 p=R/'ACTUAL_3060_DEEPSEEK_ELECTRON_GPU_ROLE_IDENTITY_READONLY.json';assert not p.exists();c=None
 try:
  c=t.connect();v=t.py(c,READ,90);v['authenticode']=t.ps(c,"$s=Get-AuthenticodeSignature -LiteralPath 'C:\Users\lulunomaro\AppData\Local\Programs\DeepSeek Harness\DeepSeek Harness.exe';[PSCustomObject]@{Status=[string]$s.Status;SignerSubject=[string]$s.SignerCertificate.Subject;SignerThumbprint=[string]$s.SignerCertificate.Thumbprint}|ConvertTo-Json -Compress");p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(actual_Electron_desktop_role=v['actual_Electron_GPU_child_of_same_desktop_main'],process=v['GPU_process']['pid'],parent=v['parent']['pid'],binary_SHA=v['binary_SHA'],signature=v['authenticode'],no_mutation=True)),flush=True)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:(R/('DESKTOP_ROLE_INSPECT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_process_change=True),indent=2),encoding='utf8');raise
