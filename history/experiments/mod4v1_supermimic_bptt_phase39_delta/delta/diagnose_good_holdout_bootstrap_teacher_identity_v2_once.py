"""NEW functional metadata diagnosis of D5's actual failed teacher equality.
Two bounded original producer FINAL reads only; never stat/open a checkpoint.
"""
from pathlib import Path
import hashlib,json,shlex,sys,time
R=Path(__file__).resolve().parent;out=R/'reports/GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V2.json';mark=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V2_STARTED_ONCE.json';assert not out.exists()and not mark.exists();old=json.loads((R/'reports/GOOD_HOLDOUT_D5_SEED20260929_ACTUAL_PREFLIGHT_V1.json').read_bytes());assert old['returncode']==1 and 'source-container/motherteacher identity distinction required'in old['stderr'];d=json.loads((R/'reports/GOOD_HOLDOUT_CONCENTRATED_ACTUAL_SOURCE_INPUT_DIAGNOSTIC_V1.json').read_bytes())['receipt'];ev=d['native_closed_boundary']['producer_evidence'];root=d['native_root'];assert root.endswith('MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000')
code="""import json,hashlib,time
ROOT=ROOT_VALUE
PINS=PINS_VALUE
result={}
for role,pin in PINS.items():
 path=ROOT+'/roles/'+role+'/production/FINAL.json'
 with open(path,'rb')as f:raw=f.read(262145)
 assert len(raw)<=262144 and len(raw)==pin['FINAL_bytes']and hashlib.sha256(raw).hexdigest()==pin['FINAL_SHA']
 final=json.loads(raw);teacher=final['teacher'];cpteacher=final['checkpoint']['teacher_source'];assert type(teacher)is dict and type(cpteacher)is dict
 keys=('source_path','source_SHA','source_bytes','teacher_frozen');projected={k:teacher.get(k)for k in keys}
 diffs=[]
 for k in sorted(set(teacher)|set(cpteacher)):
  if k not in teacher or k not in cpteacher or teacher.get(k)!=cpteacher.get(k):diffs.append(dict(key=k,final_type=type(teacher.get(k)).__name__,checkpoint_type=type(cpteacher.get(k)).__name__,missing_from_final=k not in teacher,missing_from_checkpoint=k not in cpteacher))
 result[role]=dict(path=path,original_bytes=len(raw),original_SHA256=hashlib.sha256(raw).hexdigest(),physical_reads=1,hashes=1,decodes=1,actual_BPTT_policy_steps=final['actual_BPTT_policy_steps'],final_teacher=teacher,checkpoint_teacher_source=cpteacher,current_stager_original_bootstrap_teacher=projected,checkpoint_teacher_equals_final_teacher=cpteacher==teacher,current_row_bootstrap_equals_final_teacher=projected==teacher,teacher_frozen_is_true=teacher.get('teacher_frozen')is True,strict_identity_four_fields_equal=all(type(teacher.get(k))is type(cpteacher.get(k))and teacher.get(k)==cpteacher.get(k)for k in keys),object_difference_fields=diffs,final_vs_projection_extra_keys=sorted(set(teacher)-set(projected)))
print(json.dumps(dict(kind='ACTUAL_GOOD_HOLDOUT_TEACHER_METADATA_SCHEMA_DIAGNOSIS_V2_NOT_MODEL_OR_NEW_PREFLIGHT',epoch=time.time(),roles=result,projection_is_source_expression_not_executed_stager=True,original_validator_or_prepare_stage_parent_SDK_model_C_lock_operations=0),indent=2))
""".replace('ROOT_VALUE',repr(root)).replace('PINS_VALUE',repr(ev))
with mark.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),purpose='functional equality/schema failure, not status labels or Git',old_failed_root=old['root'],original_FINAL_files=2),f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,e=c.exec_command('PYTHONDONTWRITEBYTECODE=1 '+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();v=dict(returncode=rc,stdout=stdout,stderr=stderr,purpose='NEW_FUNCTIONAL_TEACHER_IDENTITY_SCHEMA_COMPARISON',old_failed_root=old['root'])
 if rc==0:v['receipt']=json.loads(stdout)
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
 print(json.dumps(v.get('receipt',v),indent=2));assert rc==0,stderr
finally:c.close()
