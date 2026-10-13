from pathlib import Path
import time,json,sys,hashlib,zipfile,traceback
F=Path(__file__).resolve().parent;W=F.parents[1];sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';p=W/'MOD4_4090_WINDOWS_REPAIR_20261013/repair_payload/WINDOWS4090_TARGET_MATERIALIZER_V5_CPU_PREPARED.zip';h='a6dfeccdce21b5ff60ef246dccabb81071ee4fe4e52ffc953ade13884ec05a90';assert p.stat().st_size==384877 and hashlib.sha256(p.read_bytes()).hexdigest()==h
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for n in z.namelist():assert not n.startswith('/') and '..' not in Path(n).parts and ':' not in n
helper=F/'windows4090_extract_target_materializer_v5_cpu_only_once.py'
assert not helper.exists()
helper.write_text('''from pathlib import Path
import zipfile,json,time,hashlib
R=Path(__file__).resolve().parent
p=R/'packages/WINDOWS4090_TARGET_MATERIALIZER_V5_CPU_PREPARED.zip'
assert p.stat().st_size==384877 and hashlib.sha256(p.read_bytes()).hexdigest()=='a6dfeccdce21b5ff60ef246dccabb81071ee4fe4e52ffc953ade13884ec05a90'
out=R/'install_reports/TARGET_MATERIALIZER_V5_CPU_ONLY_EXTRACTED_ACTUAL.json';assert not out.exists()
assert not (R/'repair_payload_materializer_v5').exists()
rows=[]
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for n in z.namelist():
  rel=Path(n);assert not rel.is_absolute() and '..' not in rel.parts and ':' not in n
  target=(R/rel).resolve();assert target.is_relative_to(R.resolve())
  assert n.startswith('repair_payload_materializer_v5/') or n=='TARGET_MATERIALIZER_V5_BUNDLE_MANIFEST.json'
  assert not target.exists()
  target.parent.mkdir(parents=True,exist_ok=True);b=z.read(n)
  with target.open('xb') as f:f.write(b)
  sha=hashlib.sha256(target.read_bytes()).hexdigest();assert sha==hashlib.sha256(b).hexdigest()
  rows.append(dict(path=str(target),bytes=len(b),sha256=sha))
j=dict(epoch=time.time(),archive=str(p),bytes=384877,sha256='a6dfeccdce21b5ff60ef246dccabb81071ee4fe4e52ffc953ade13884ec05a90',files=rows,only_CPU_plain_archive_extraction=True,no_module_import_GPU_Task_or_targetCPU_execution=True,old34304byte_package_not_consumed=True)
out.write_text(json.dumps(j,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),filecount=len(rows))))
''',encoding='utf8')
out=F/('WINDOWS4090_TARGET_MATERIALIZER_V5_UPLOAD_CPU_EXTRACT_ACTUAL_'+str(time.time_ns())+'.json');j=dict(epoch=time.time(),package=str(p),bytes=384877,sha256=h,no_GPU_Task_or_targetCPU_launch=True)
try:
 s=connect();remote=R+'/packages/'+p.name;hs=hashlib.sha256(helper.read_bytes()).hexdigest()
 pre=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();@{zip_present=Test-Path -LiteralPath '"+remote+"';target_present=Test-Path -LiteralPath '"+R+"/repair_payload_materializer_v5';helper_present=Test-Path -LiteralPath '"+R+'/'+helper.name+"'}|ConvertTo-Json",timeout=25));j['pre']=pre;out.write_text(json.dumps(j,indent=2),encoding='utf8');assert not any(pre.values())
 upload(p,remote,timeout=60);upload(helper,R+'/'+helper.name,timeout=60)
 code="$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();if((Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()-ne'"+h+"'){throw 'package SHA'};if((Get-FileHash -LiteralPath '"+R+'/'+helper.name+"' -Algorithm SHA256).Hash.ToLower()-ne'"+hs+"'){throw 'helper SHA'};& '"+R+"/env/python.exe' '"+R+'/'+helper.name+"';if($LASTEXITCODE-ne0){throw 'targetpackage extract CPU rejected'}"
 j['actual']=json.loads(powershell(s,code,timeout=35));j['helper_source_sha256']=hs;j['remote_byte_SHA_exact']=True;s.close();out.write_text(json.dumps(j,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),actual=j['actual']),ensure_ascii=True))
except Exception as e:j.update(error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());out.write_text(json.dumps(j,indent=2),encoding='utf8');raise
