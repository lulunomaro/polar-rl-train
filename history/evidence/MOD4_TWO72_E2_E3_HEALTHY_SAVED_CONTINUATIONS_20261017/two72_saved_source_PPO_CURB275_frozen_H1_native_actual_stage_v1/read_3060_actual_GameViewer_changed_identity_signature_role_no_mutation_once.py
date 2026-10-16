from pathlib import Path
import sys,json,time,os,traceback
N=Path(__file__).resolve().parent;E=N/'curb275_final87_frozen3060_v1';R=N/'reports';sys.path.insert(0,str(E));import transport_249_exact_desktop_role_stdin_fresh2233_v7 as t
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('GAMEVIEWER_CHANGED_ACTUAL_READONLY_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True));c=None
 try:
  c=t.connect();v=t.py(c,"from pathlib import Path;import json,time,psutil,subprocess,hashlib;rows=[];apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)\nfor line in apps.splitlines():\n if not line.strip():continue\n p=psutil.Process(int(line.split(',')[0]));exe=p.exe();children=[dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),name=q.name()) for q in p.children(recursive=True)];row=dict(pid=p.pid,creation=p.create_time(),exe=exe,argv=p.cmdline(),parent=p.ppid(),children=children)\n if Path(exe).name.lower()=='gameviewerserver.exe':\n  row['binary_SHA']=hashlib.sha256(Path(exe).read_bytes()).hexdigest();cmd=\"Get-AuthenticodeSignature -LiteralPath '\"+exe.replace(\"'\",\"''\")+\"'|Select-Object Status,@{n='Subject';e={$_.SignerCertificate.Subject}},@{n='Thumbprint';e={$_.SignerCertificate.Thumbprint}}|ConvertTo-Json -Compress\";sig=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,check=True);row['authenticode']=json.loads(sig.stdout)\n rows.append(row)\nprint(json.dumps(dict(epoch=time.time(),GPU_processes=rows,no_process_UI_Guard_or_runtime_mutation=True)))",90);put('ACTUAL_3060_GAMEVIEWER_FRESH_PID_SIGNATURE_GRAPHICS_ROLE_READONLY.json',v);print(json.dumps(v),flush=True)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('GAMEVIEWER_ROLE_READONLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
