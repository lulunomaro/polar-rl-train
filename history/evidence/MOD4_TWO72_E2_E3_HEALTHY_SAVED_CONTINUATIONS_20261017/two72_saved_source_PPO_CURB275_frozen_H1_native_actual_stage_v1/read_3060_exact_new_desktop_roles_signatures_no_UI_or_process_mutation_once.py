from pathlib import Path
import sys,os,json,time,traceback
N=Path(__file__).resolve().parent;E=N/'curb275_final87_frozen3060_v1';R=N/'reports';sys.path.insert(0,str(E));import transport_249_exact_desktop_role_stdin_fresh2233_v7 as t
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import json,time,psutil,subprocess,hashlib
names={'gameviewerserver.exe','gameviewer.exe','deepseek harness.exe','workbuddy.exe','qq.exe','copilotapp.exe','copilotapphost.exe'};rows=[];apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
def ident(p):return dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),parent=p.ppid())
for line in apps.splitlines():
 if not line.strip():continue
 p=psutil.Process(int(line.split(',')[0]));name=Path(p.exe()).name.lower()
 if name not in names:continue
 exe=p.exe();cmd="[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false);Get-AuthenticodeSignature -LiteralPath '"+exe.replace("'","''")+"'|Select-Object @{n='Status';e={$_.Status.ToString()}},@{n='Subject';e={$_.SignerCertificate.Subject}},@{n='Thumbprint';e={$_.SignerCertificate.Thumbprint}}|ConvertTo-Json -Compress";sig=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,check=True);parent=p.parent();row=dict(name=name,process=ident(p),parent=ident(parent) if parent else None,binary_SHA=hashlib.sha256(Path(exe).read_bytes()).hexdigest(),authenticode=json.loads(sig.stdout.decode('utf-8-sig')),children=[ident(q) for q in p.children(recursive=True)],parent_children=[ident(q) for q in parent.children(recursive=True)] if parent and '--type=gpu-process' in p.cmdline() else [])
 rows.append(row)
print(json.dumps(dict(epoch=time.time(),exact_new_desktop_roles=rows,read_only_process_metadata_no_UI_and_no_signal=True)))
'''
def main():
 put('FRESH_ALL_NEW_DESKTOP_ROLES_READONLY_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True));c=None
 try:c=t.connect();v=t.py(c,CODE,120);put('ACTUAL_3060_FRESH_EXACT_DESKTOP_ROLE_SIGNATURES_0109_READONLY.json',v);print(json.dumps([dict(name=r['name'],pid=r['process']['pid'],creation=r['process']['creation'],SHA=r['binary_SHA'],signature=r['authenticode'],GPUflag='--type=gpu-process' in r['process']['argv'],argv=r['process']['argv'] if r['name']=='copilotapphost.exe' else None) for r in v['exact_new_desktop_roles']]),flush=True)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('FRESH_ALL_DESKTOP_ROLES_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
