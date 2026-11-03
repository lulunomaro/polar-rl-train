"""File materialization after own actual preflight; no parent, resource or SDK."""
from pathlib import Path
import sys,json,hashlib,time,shlex
R=Path(__file__).resolve().parent;report=R/'reports/PHASE1_E3_CAPTURE_V4_ADMISSION2_ACTUAL_STAGE.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_E3_CAPTURE_V4_ADMISSION2_STAGE_STARTED_ONCE.json'
assert not report.exists()and not marker.exists(),'Stage purpose already consumed'
p=json.loads((R/'reports/PHASE1_E3_CAPTURE_V4_ADMISSION2_ACTUAL_PREFLIGHT.json').read_bytes());r=p['receipt'];assert p['returncode']==0 and r['materialized']is False and r['parent_launches']==0 and r['metadata_validation']['passed'] and r['source_pins']['source_mappings']==27
argv=list(p['argv']);assert argv[-1]=='--preflight-only';argv[-1]='--stage';root=p['group_root'];stager=p['stager'];B='/home/lc01/Zonglin Li/zonglin2';expected='f3059d24444c40873f2d55aeb22fd82e32284e761db96250ec985314080c6507'
with marker.open('x',encoding='utf-8')as f:json.dump(dict(kind='NEW_PHASE1_CAPTURE_EXPLICIT_FILE_STAGE_PURPOSE',epoch=time.time(),group_root=root,input_root=p['input_root'],argv=argv,parent_launches=0),f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 with s.open(stager,'rb')as f:raw=f.read()
 assert(len(raw),hashlib.sha256(raw).hexdigest())==(45850,expected)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(str(Path(stager).parent).replace('\\','/'),argv,stager)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=600);i.close();stdout=o.read().decode('utf-8','replace');stderr=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();value=dict(kind='ACTUAL_PHASE1_CAPTURE_FILE_MATERIALIZATION_NOT_ADMISSION_V4_ADMISSION2',epoch=time.time(),group_id=p['group_id'],group_root=root,input_root=p['input_root'],GPU_UUID=p['GPU_UUID'],controls=p['controls'],returncode=rc,stdout=stdout,stderr=stderr,parent_launches=0,actual_SDK_executed=False)
 if rc==0:
  receipt_path=root+'/STAGE_COMPLETE_PHASE1_CAPTURE_V1.json'
  with s.open(receipt_path,'rb')as f:receipt_raw=f.read()
  value.update(receipt=json.loads(receipt_raw),stage_receipt_bytes=len(receipt_raw),stage_receipt_SHA256=hashlib.sha256(receipt_raw).hexdigest())
 with report.open('x',encoding='utf-8')as f:json.dump(value,f,indent=2)
 assert rc==0,stderr
 r=value['receipt'];assert r['materialized']is True and r['parent_launches']==0 and r['metadata_validation']['passed'] and not r['actual_SDK_executed']
 print(json.dumps(dict(report=str(report),group_root=root,files=r['files'],materialized=True,parent_launches=0,stage_receipt_SHA256=value['stage_receipt_SHA256'],gate1=r['gate1']),indent=2))
finally:s.close();c.close()
