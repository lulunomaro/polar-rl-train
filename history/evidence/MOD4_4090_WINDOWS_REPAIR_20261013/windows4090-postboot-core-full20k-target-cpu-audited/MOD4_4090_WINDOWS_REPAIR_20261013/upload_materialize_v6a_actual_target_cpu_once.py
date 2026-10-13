from pathlib import Path
import hashlib,json,time,traceback,base64
from windows4090_native_transport import connect,powershell,upload
D=Path(__file__).resolve().parent
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    receipt=D/'reports/V6A_ACTUAL_REMOTE_TARGET_CPU_DISPATCH_RECEIPT.json';assert not receipt.exists()
    p=D/'WINDOWS4090_TARGET_V6A_AUDITED_CPU_PREPARED_20261013.zip'
    remote=R+'/packages/'+p.name;s=connect()
    pre=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$r='"+R+"';@{scope_exists=Test-Path -LiteralPath ($r+'/training_scope_full20k_left_repair_audited_v6a_20261013');payload_exists=Test-Path -LiteralPath ($r+'/repair_payload_v6a');ready=Test-Path -LiteralPath ($r+'/install_reports/BOUNDED_HEADLESS_CORE_CPU_ADMISSION_EXPLICIT_WEB_PIN_EXCEPTION.json');package_present=Test-Path -LiteralPath '"+remote+"'}|ConvertTo-Json -Compress",timeout=30))
    assert pre['ready'] and not pre['scope_exists'] and not pre['payload_exists'] and not pre['package_present']
    upload(p,remote,timeout=60)
    assert powershell(s,"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",timeout=30)==H(p)
    result=dict(epoch=time.time(),pre=pre,package=dict(path=str(p),remote=remote,bytes=p.stat().st_size,sha256=H(p)),no_GPU_or_old_once_replay=True)
    receipt.write_text(json.dumps(result,indent=2),encoding='utf8')
    code="""from pathlib import Path,PurePosixPath
import json,zipfile,hashlib,os,subprocess,sys
r=Path('"""+R+"""');p=r/'packages/"""+p.name+"""'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='"""+H(p)+"""'
with zipfile.ZipFile(p) as z:
 m=json.loads(z.read('V6A_AUDITED_CPU_BUNDLE_MANIFEST.json'))
 assert z.testzip() is None and len(m['file_rows'])==62
 for row in m['file_rows']:
  n=PurePosixPath(row['archive']);assert n.parts[0]=='repair_payload_v6a' and '..' not in n.parts and not n.is_absolute() and ':' not in row['archive']
  b=z.read(row['archive']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
  q=(r/Path(*n.parts)).resolve();assert q.is_relative_to(r.resolve());q.parent.mkdir(parents=True,exist_ok=True)
  with q.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 q=r/'repair_payload_v6a/V6A_AUDITED_CPU_BUNDLE_MANIFEST.json';q.write_text(json.dumps(m,indent=2),encoding='utf8')
helper=r/'repair_payload_v6a/materialize_windows20k_target_audited_v6_cpu_once.py'
out=[]
for op in ['materialize','verify-targetCPU']:
 args=[sys.executable,str(helper),'--operation',op]
 child=subprocess.run(args,capture_output=True,text=True,encoding='utf8',timeout=180)
 out.append(dict(operation=op,exit_code=child.returncode,stdout=child.stdout,stderr=child.stderr))
 assert child.returncode==0,out[-1]
print(json.dumps(dict(passed=True,CPU_only=True,operations=out)))
"""
    b=base64.b64encode(code.encode()).decode()
    actual=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",timeout=240))
    assert actual['passed'];result['actual']=actual
    receipt.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(dict(report=str(receipt),actual_target_CPU_passed=True,actual_GPU_started=False)))
if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports'/('V6A_TARGET_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_read_actual_no_operation_replay=True),indent=2),encoding='utf8')
        raise
