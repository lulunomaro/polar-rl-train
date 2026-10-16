from pathlib import Path
import sys,json,time,traceback,importlib.util
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;s=importlib.util.spec_from_file_location('readonly249',W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014/transport_249_bodyframe_current_terminal_role_v3.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
READ=r'''
from pathlib import Path
import json,time,psutil,hashlib
found=[]
for p in psutil.process_iter(['name','cmdline']):
 try:
  if p.info['name'].casefold()=='deepseek harness.exe' and '--type=gpu-process' in (p.info['cmdline'] or []):found.append(p)
 except psutil.Error:pass
assert len(found)==1; p=found[0];exe=Path(p.exe());assert str(exe).casefold()==r'C:\Users\lulunomaro\AppData\Local\Programs\DeepSeek Harness\DeepSeek Harness.exe'.casefold()
def row(p):return dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),exe=p.exe(),parent=p.ppid())
parent=p.parent();assert parent and Path(parent.exe()).resolve()==exe.resolve() and not any(x.startswith('--type=') for x in parent.cmdline());desc=[]
for c in parent.children(recursive=True):
 v=row(c);assert Path(c.exe()).resolve()==exe.resolve() or c.name().lower()=='crashpad_handler.exe';desc.append(v)
raw=exe.read_bytes();print(json.dumps(dict(epoch=time.time(),GPU_process=row(p),parent=row(parent),children=desc,binary_path=str(exe),binary_bytes=len(raw),binary_SHA=hashlib.sha256(raw).hexdigest(),actual_Electron_GPU_child_of_same_desktop_main=True,no_Python_Kit_or_training_child=True,no_process_GPU_or_UI_mutation=True,classification_scope='Exact fresh identities with previous actual same binary and signer, no wildcard or process changes')))
'''
def main():
 p=R/'ACTUAL_3060_DEEPSEEK_SAME_BINARY_FRESH_GPU_ROLE_2233_READONLY.json';assert not p.exists();c=None
 try:
  c=t.connect();v=t.py(c,READ,90);v['authenticode']=t.ps(c,r"$s=Get-AuthenticodeSignature -LiteralPath 'C:\Users\lulunomaro\AppData\Local\Programs\DeepSeek Harness\DeepSeek Harness.exe';[PSCustomObject]@{Status=[string]$s.Status;SignerSubject=[string]$s.SignerCertificate.Subject;SignerThumbprint=[string]$s.SignerCertificate.Thumbprint}|ConvertTo-Json -Compress");old=json.loads((R/'ACTUAL_3060_DEEPSEEK_ELECTRON_GPU_ROLE_IDENTITY_READONLY.json').read_bytes());assert v['authenticode']['Status']=='Valid' and v['authenticode']==old['authenticode'] and v['binary_SHA']==old['binary_SHA'];p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(same_binary_and_signer=True,fresh_GPU_process=v['GPU_process']['pid'],fresh_parent=v['parent']['pid'],no_mutation=True)))
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:(R/('DESKTOP2233_READONLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_process_change=True),indent=2),encoding='utf8');raise
