"""NEW H1 exact452 nonPT+overlay+assets bundle, GPU1 fresh80 dispatch only.
No PT path is stat/read/copied/hashed. No canonical, othercase/GPU0 or training.
"""
from pathlib import Path
import ast,datetime,hashlib,json,shlex,sys,time,zipfile,traceback
B=Path(__file__).resolve().parent;T=B.parent;O=T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V1'
sys.path.insert(0,str(T));from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'
ASSETS=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets')
GETTER=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\REFERENCE_TRACKING_BPTT_V300_20261101\source\actual_DR_memory_getter272.py')
NO={'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc'}

def main():
 assert not (B/'CURRENT_FRESH80_CASE.json').exists()
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root=BASE+'/tasks/MOD4V1_H1_NORMAL_FRESH80_'+stamp
 src=(T/'E3_actual_fresh80/supervise_e3_fresh80_v1.py').read_text(encoding='utf-8')
 src=src.replace('E3','H1_NORMAL').replace('e3','h1_normal').replace('MOD4V1_H1_NORMAL_FRESH80_D0_D7_NO_PT','MOD4V1_H1_NORMAL_FRESH80_NO_PT_V1').replace('H1_NORMAL_FRESH80_NATIVE34_COMPLETE.json','H1_FRESH80_COMPLETE.json').replace('H1_NORMAL_FRESH80_ORIGINAL_ERROR.json','H1_FRESH80_ORIGINAL_ERROR.json')
 src=src.replace("['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid'","['/usr/bin/nvidia-smi','-i',uuid,'--query-compute-apps=gpu_uuid,pid'")
 supervisor=B/'supervise_h1_normal_fresh80_v1.py'
 with supervisor.open('x',encoding='utf-8') as f:f.write(src)
 ast.parse(src);ast.parse((B/'probe_h1_normal_fresh80_v1.py').read_text(encoding='utf-8'))
 verified=json.loads((B/'LOCAL_NONPT453_DEPENDENCIES_VERIFIED.json').read_text(encoding='utf-8'));assert not verified['missing'] and verified['nonPT_verified']==452
 entries={r['relative']:Path(r['local_path']) for r in verified['files']}
 for p in O.rglob('*'):
  if p.suffix.lower() in NO:raise ValueError('Model in source-only overlay')
  if p.is_file():entries[p.relative_to(O).as_posix()]=p
 for p in ASSETS.rglob('*'):
  if p.suffix.lower() in NO:raise ValueError('Model in declared asset dependency tree')
  if p.is_file():entries['new_assets/'+p.relative_to(ASSETS).as_posix()]=p
 entries.update({'job0/runtime/isaac/mod4/actual_DR_memory_getter272.py':GETTER,'probe_h1_normal_fresh80.py':B/'probe_h1_normal_fresh80_v1.py','supervise_h1_normal_fresh80.py':supervisor})
 archive=B/('H1_EXACT453_NONPT_BUNDLE_'+stamp+'.zip');rows=[]
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=2) as z:
  for rel,p in sorted(entries.items()):
   assert p.suffix.lower() not in NO and not p.name.upper().startswith('TRAINING_BUDGET')
   raw=p.read_bytes();z.writestr(rel,raw);rows.append(dict(relative=rel,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
 archiveSHA=hashlib.sha256(archive.read_bytes()).hexdigest()
 report=dict(kind='H1_FRESH80_EXACT452_NONPT_NEW_STAGE_DISPATCH',remote_root=root,source453_manifest_SHA='97cdcde4a891359a5f1209fdad1614bf87629e0c3d3a40ce9018dc1fe9e2426b',source_PT_reads_stats_hashes=0,canonical_access=False,bundle=dict(path=str(archive),bytes=archive.stat().st_size,SHA=archiveSHA),files=rows)
 client=sf=None
 try:
  client=connect72();sf=client.open_sftp()
  # Parent tasks directory already exists; create only this exact unused child.
  sf.mkdir(root);sf.put(str(archive),root+'/NONPT_STAGE_BUNDLE.zip')
  with sf.open(root+'/H1_NONPT_STAGE_INDEX.json','wx') as f:f.write(json.dumps(dict(files=rows,archive_SHA=archiveSHA,source_PT_opens=0),indent=2))
  code="""from pathlib import Path
import hashlib,json,zipfile
B=Path(%r);index=json.loads((B/'H1_NONPT_STAGE_INDEX.json').read_bytes());raw=(B/'NONPT_STAGE_BUNDLE.zip').read_bytes();assert hashlib.sha256(raw).hexdigest()==index['archive_SHA']
with zipfile.ZipFile(B/'NONPT_STAGE_BUNDLE.zip') as z:
 for r in index['files']:
  rel=Path(r['relative']);assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix.lower() not in {'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc'}
  p=B/rel;p.parent.mkdir(parents=True,exist_ok=True);data=z.read(r['relative']);assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
  with p.open('xb') as f:f.write(data)
print(json.dumps({'staged':True,'root':str(B),'files':len(index['files']),'models':0,'SDK_started':False}))
"""%root
  i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(stage_rc=rc,stage_stdout=stdout,stage_stderr=stderr);assert rc==0,'ExactH1nonPT stage failed; preserve report'
  query="import subprocess,json;v=subprocess.check_output(['/usr/bin/nvidia-smi','-i','1','--query-gpu=index,uuid,name','--format=csv,noheader,nounits'],text=True).strip().split(',');assert v[0].strip()=='1' and v[2].strip()=='NVIDIA GeForce RTX 4090';print(json.dumps({'uuid':v[1].strip()}))"
  i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(query),timeout=60);i.close();q=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);gpu=json.loads(q)['uuid']
  plan=dict(kind='MOD4V1_H1_NORMAL_FRESH80_PLAN',GPU_index=1,GPU_UUID=gpu,num_envs=80,controls=24,parent_limit_s=720,files=rows,asset_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',worker_SHA=hashlib.sha256((B/'probe_h1_normal_fresh80_v1.py').read_bytes()).hexdigest(),no_production_GO=True,canonical_access=False)
  with sf.open(root+'/H1_NORMAL_FRESH80_PLAN.json','wx') as f:f.write(json.dumps(plan,indent=2))
  start="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);assert not(B/'PARENT_STARTED.json').exists();log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'supervise_h1_normal_fresh80.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();print(json.dumps({'pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'dispatched_only':True}))"%(root,BASE+'/run-python.sh')
  i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(start),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr);report.update(status='FRESH80_SUPERVISOR_DISPATCHED_ONCE',parent=json.loads(stdout),GPU_UUID=gpu)
  with (B/'CURRENT_FRESH80_CASE.json').open('x',encoding='utf-8') as f:json.dump(dict(remote_root=root,parent=report['parent'],GPU_UUID=gpu),f,indent=2)
 except BaseException:
  report.update(status='STAGE_OR_DISPATCH_ERROR',error=traceback.format_exc());raise
 finally:
  if sf:sf.close()
  if client:client.close()
  dest=T/'reports'/('H1_fresh80_stage_dispatch_'+stamp+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=report.get('status'),root=root,parent=report.get('parent'),report=str(dest)),indent=2))
if __name__=='__main__':main()
