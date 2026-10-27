"""Retain frozenV1; correct only its unsolicited16GiB runtime floor to original8GiB."""
from pathlib import Path
import ast, hashlib, json, time
HERE=Path(__file__).resolve().parent
def H(raw):return hashlib.sha256(raw).hexdigest()
def main():
 old=HERE/'E0_PPO50_gas400_finite_worker_v1.py';new=HERE/'E0_PPO50_gas400_finite_worker_v2_disk8_exact.py'
 before=old.read_bytes();assert H(before)=='502110722556d44c57ae94d1fd523343de7a12b4ddc2108726bd7914294a5466'
 a=b'shutil.disk_usage(job).free<16*1024**3';b=b'shutil.disk_usage(job).free<8*1024**3';assert before.count(a)==1
 after=before.replace(a,b);assert after.replace(b,a)==before and not new.exists();new.write_bytes(after)
 old_tree=ast.parse(before);new_tree=ast.parse(after);changed=[]
 def compare(x,y,path='root'):
  if isinstance(x,ast.AST):
   assert type(x) is type(y)
   for field in x._fields:compare(getattr(x,field),getattr(y,field),path+'.'+field)
  elif isinstance(x,list):
   assert len(x)==len(y)
   for i,(left,right) in enumerate(zip(x,y)):compare(left,right,path+'['+str(i)+']')
  elif x!=y:changed.append(dict(AST_path=path,before=x,after=y))
 compare(old_tree,new_tree);assert len(changed)==1 and changed[0]['before']==16 and changed[0]['after']==8
 line=next(i for i,s in enumerate(before.decode().splitlines(),1) if a.decode() in s)
 report=dict(attempt_id='E0_RUNTIME_DISK16_UNSOLICITED_FLOOR_REJECTED_AND_EXACT8_REPAIRED_20261027_V2',epoch=time.time(),
  issue='V1 introduced runtime16GiB floor although existing contract requires8GiB. Root rejected the new threshold before target GO.',
  frozen_V1_retained=dict(path=str(old),bytes=len(before),SHA=H(before)),
  worker_V2=dict(path=str(new),bytes=len(after),SHA=H(after)),
  only_byte_replacement=dict(before=a.decode(),after=b.decode(),count=1,line=line),
  inverse_replacement_entire_original_bytes_exact=True,AST_only_one_Constant_16_to_8=changed,
  AST_compile_passed=True,original_fullupdate_save_exit_no_other_change=True,no_GPU_remote_GO_or_account_write=True,
  E0_frozen_V1_index_unchanged=True,Git_status='pending_root_ordinary_supplement')
 p=HERE/'reports/E0_WORKER_V2_DISK8_EXACT_ONE_LITERAL_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8')
 handoff=HERE/'E0_WORKER_V2_DISK8_EXACT_HANDOFF.md'
 handoff.write_text('''# E0 V2 uses the original8GiB runtime disk floor

Frozen V1 remains unchanged. Its16GiB runtime stop floor was an unsolicited threshold and was rejected before target GO. V2 changes exactly `shutil.disk_usage(job).free<16*1024**3` to `<8*1024**3`. Inverse byte replacement reconstructs the entire V1 file; AST comparison finds exactly one Constant16→8. All actor/critic/STD/Adam/LR/fullrestore, reward/clock/gas parameters, sourceSHA, GO/accounting requirements and complete-update fullsave/exit behavior stay identical.

Use E0_PPO50_gas400_finite_worker_v2_disk8_exact.py as the new stage source. Bind TASK.worker_SHA and the actual executed file to V2 SHA. The unchanged CPU admission script can read the new bytes installed at its expected root `E0_PPO50_gas400_finite_worker_v1.py` basename; record them explicitly as V2 content and never claim V1 target admission. No target GO/PPO occurred in this correction. E0 V1 frozen index remains historical, while this V2 proof/handoff is pending root ordinary Git supplementation.
''',encoding='utf8')
 print(json.dumps(dict(worker=str(new),SHA=H(after),bytes=len(after),exact_changes=1,AST_changes=changed,report=str(p))))
if __name__=='__main__':main()
