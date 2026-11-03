"""One NEW bounded CPU-only purpose for complete pinned codec/fixture.
No actor/model/replay/SDK/static bank/canonical/locks/native task or old purpose.
"""
from pathlib import Path
import ast,hashlib,json,shlex,sys,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_TYPED_CODEC_ACTUAL_REAL_CPU_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_TYPED_CODEC_REAL_CPU_V1_STARTED_ONCE.json';assert not out.exists()and not marker.exists();H=lambda b:hashlib.sha256(b).hexdigest();payload={};seals=[]
for folder,size,sha,entry,alias in [('source_phase1_typed_capture_codec_v1',1427,'2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219','typed_capture_codec.py','typed_capture_codec.py'),('source_phase1_codec_real_cpu_fixture_v1',1295,'3cd0b48ea885f1161e7d841aa5f6e8dd9d99c82eb9575b36bd8d297cf43b032a','cpu_fixture.py','cpu_fixture.py')]:
 d=R/folder;b=(d/'SOURCE_SEAL.json').read_bytes();assert(len(b),H(b))==(size,sha);s=json.loads(b);assert s['Gate1']=='UNKNOWN'and not s['stage2_GO'];before={}
 for name,pin in s['files'].items():
  z=(d/name).read_bytes();assert(len(z),H(z))==(pin['bytes'],pin['sha256']);before[name]=H(z)
  if name==entry:payload[alias]=z;ast.parse(z)
 seals.append(dict(folder=folder,seal_SHA256=sha,members=before))
pins={Path(k).stem:dict(bytes=len(b),SHA256=H(b))for k,b in payload.items()};payload['INPUT_PINS.json']=json.dumps(pins,indent=2).encode();p=R/'phase1_typed_codec_real_cpu_program_v1.py';b=p.read_bytes();ast.parse(b);payload[p.name]=b;B='/home/lc01/Zonglin Li/zonglin2';root=B+'/tasks/PHASE1_TYPED_CODEC_REAL_CPU_V1_'+str(time.time_ns());config=dict(kind='NEW_TYPED_CODEC_REAL_CPU_PURPOSE_NO_SDK_OR_NATIVE',epoch=time.time(),root=root,source_seals=seals,uploaded=[dict(name=k,bytes=len(b),SHA256=H(b))for k,b in payload.items()],actual_selected_model_or_raw_or_SDK_C_or_lock_or_GPU_or_parent_operations=0)
with marker.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(root)
 except FileNotFoundError:pass
 else:raise AssertionError('new CPU purpose exists')
 s.mkdir(root)
 for name,b in payload.items():
  with s.open(root+'/'+name,'wx')as f:f.write(b)
 code='import sys,runpy;sys.path.insert(0,%r);runpy.run_path(%r,run_name="__main__")'%(root,root+'/phase1_typed_codec_real_cpu_program_v1.py');i,o,e=c.exec_command('PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= '+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=300);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status()
 with s.open(root+'/RESULT.json','rb')as f:r=f.read(262145)
 assert len(r)<=262144;receipt=json.loads(r)
 after=[]
 for seal in seals:
  after.append(all(H((R/seal['folder']/k).read_bytes())==sha for k,sha in seal['members'].items())and H((R/seal['folder']/'SOURCE_SEAL.json').read_bytes())==seal['seal_SHA256'])
 v=dict(config,returncode=rc,stdout=stdout,stderr=stderr,receipt=receipt,source_seals_unchanged=all(after),result_bytes=len(r),result_SHA256=H(r))
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
 print(json.dumps(dict(returncode=rc,receipt=receipt,source_seals_unchanged=all(after)),indent=2));assert rc==0 and receipt['status']=='PASS'and all(after),stderr
finally:s.close();c.close()
