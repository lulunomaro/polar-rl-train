"""NEW remote CPU real metadata import/alias check. No SDK/plan/admission/PT/locks."""
from pathlib import Path,PurePosixPath
import sys,json,hashlib,ast,time,shlex
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_worker_v1';out=R/'reports/PHASE1_CAPTURE_METADATA_IMPORT_CPU_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/CAPTURE_METADATA_IMPORT_CPU_V1_STARTED_ONCE.json';assert not out.exists()and not marker.exists();payload={};pins={}
def add(alias,raw,sha):
 p=PurePosixPath(alias);assert not p.is_absolute()and not any(x in('..','.')for x in p.parts);assert hashlib.sha256(raw).hexdigest()==sha
 if alias in payload:assert payload[alias]==raw
 payload[alias]=raw;pins[alias]=dict(bytes=len(raw),SHA256=sha)
sealraw=(D/'SOURCE_SEAL.json').read_bytes();assert hashlib.sha256(sealraw).hexdigest()=='3f713457c5d66c44ad1fe962ff954e6f65f87afedfef1d6e5bb7fa608e76bea7';seal=json.loads(sealraw);assert len(seal['files'])==13;add('SOURCE_SEAL.json',sealraw,hashlib.sha256(sealraw).hexdigest())
for m in seal['files']:
 p=(D/m['relative']).resolve();assert p.is_relative_to(D);raw=p.read_bytes();assert len(raw)==m['bytes'];add(m['relative'],raw,m['sha256'])
index=json.loads(payload['CAPTURE_SOURCE_INDEX.json']);rows=index['original17']+index['new_sources']+index['dependency_sources'];assert len(rows)==27
for row in rows:
 path=Path(row['path']).resolve();assert path.is_relative_to(R)and path.suffix.lower()in{'.py','.json','.md','.txt'};raw=path.read_bytes();assert len(raw)==row['bytes'];add(row['install_relative'],raw,row['SHA256'])
controller=R/'source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py';raw=controller.read_bytes();add(controller.name,raw,'95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831')
name='phase1_capture_metadata_import_cpu_v1.py';raw=(R/'PAPER_ALIGNED_REBUILD_20261103'/name).read_bytes();ast.parse(raw);add(name,raw,hashlib.sha256(raw).hexdigest());B='/home/lc01/Zonglin Li/zonglin2';job=B+'/tasks/PHASE1_CAPTURE_METADATA_IMPORT_CPU_V1_'+str(time.time_ns());script=job+'/'+name;result=job+'/METADATA_IMPORT_RESULT_V1.json';marker.write_text(json.dumps(dict(kind='NEW_PHASE1_REAL_METADATA_IMPORT_CPU_PURPOSE',epoch=time.time(),remote_root=job,source_pins=pins,SDK_model_GPU_canonical_operations=0),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('New metadata import CPU root exists')
 s.mkdir(job);parents=set()
 for alias in payload:
  pp=PurePosixPath(alias).parent
  while str(pp)!='.':parents.add(pp);pp=pp.parent
 for pp in sorted(parents,key=lambda x:(len(x.parts),str(x))):s.mkdir(job+'/'+str(pp))
 for alias,raw in payload.items():
  with s.open(job+'/'+alias,'wb')as f:f.write(raw)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(job,[script,'--root',job,'--output',result],script)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=180);i.close();stdout=o.read().decode('utf-8','replace');stderr=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();value=dict(kind='ACTUAL_PHASE1_CAPTURE_METADATA_IMPORT_CPU_V1',remote_root=job,source_pins=pins,returncode=rc,stdout=stdout,stderr=stderr,SDK_model_raw_GPU_canonical_operations=0);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,stderr
 with s.open(result,'rb')as f:value['receipt']=json.loads(f.read())
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');r=value['receipt'];assert r['status']=='PASS'and not r['forbidden_modules_loaded']and r['full_AppV6_and_Base_imported_not_stubbed']and not r['actual_resource_admission'];print(json.dumps(dict(report=str(out),status=r['status'],sources=r['source_rows'],full_App_and_Base_real_import=r['full_AppV6_and_Base_imported_not_stubbed'],forbidden_modules_loaded=r['forbidden_modules_loaded'],gate=r['gate1']),indent=2))
finally:s.close();c.close()
