"""RetainV1/V2; use root-directed original4090 resource floor and compute-only exclusion."""
from pathlib import Path
import ast,copy,hashlib,json,time
HERE=Path(__file__).resolve().parent
def H(raw):return hashlib.sha256(raw).hexdigest()
def main():
 old=HERE/'E0_PPO50_gas400_finite_worker_v2_disk8_exact.py';new=HERE/'E0_PPO50_gas400_finite_worker_v3_original_resource_exact.py'
 before=old.read_bytes();assert H(before)=='123f34f6f684c3603eb503411c0833dde5716c27265c59d90759fa4615163fec'
 a=b'int(free)>=22000';b=b'int(free)>15669';c=b' and int(util)<=5'
 assert before.count(a)==1 and before.count(c)==1
 after=before.replace(a,b).replace(c,b'');assert not new.exists()
 oldline=next(x for x in before.decode().splitlines() if a.decode() in x);newline=next(x for x in after.decode().splitlines() if b.decode() in x)
 assert after.replace(newline.encode(),oldline.encode())==before
 oldtree=ast.parse(before);newtree=ast.parse(after);expected=copy.deepcopy(oldtree)
 oldassert=next(n for n in ast.walk(expected) if isinstance(n,ast.Assert) and ast.get_source_segment(before.decode(),n)==oldline.strip())
 newassert=ast.parse(newline.strip()).body[0]
 oldassert.test=newassert.test
 assert ast.dump(expected,include_attributes=False)==ast.dump(newtree,include_attributes=False)
 new.write_bytes(after)
 report=dict(attempt_id='E0_UNSOLICITED_RESOURCE_FLOORS_REJECTED_EXACT_ORIGINAL4090_V3_20261027',epoch=time.time(),
  issue='Root rejected V1/V2 added22000MiB/5percent worker conditions before target GO; use original4090 lower bound15669MiB and strict zero selected compute UUID rows.',
  retained_V2=dict(path=str(old),bytes=len(before),SHA=H(before)),V3=dict(path=str(new),bytes=len(after),SHA=H(after)),
  requested_exact_replacements=[dict(before=a.decode(),after=b.decode(),count=1),dict(before=c.decode(),after='',count=1)],
  old_resource_assertion=oldline,new_resource_assertion=newline,
  inverse_entire_original_bytes_exact=True,AST_only_one_resource_assertion_changed=True,AST_compilation_passed=True,
  zero_selected_compute_UUID_preserved=True,fresh_UUID_memory_utilization_observation_preserved=True,
  runtime_disk_floor8GiB_unchanged=True,all_other_source_and_restore_GOs_reward_physics_save_bytes_unchanged=True,
  no_GPU_remote_GO_or_account_write=True,Git_status='pending_root_ordinary_supplement')
 p=HERE/'reports/E0_WORKER_V3_ORIGINAL4090_RESOURCE_EXACT_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8')
 (HERE/'E0_WORKER_V3_ORIGINAL4090_RESOURCE_HANDOFF.md').write_text('''# E0 V3 preserves the original resource bounds

V1/V2 are retained. Their newly added worker checks free≥22000MiB and utilization≤5percent were rejected by root before target GO. V3 changes only `int(free)>=22000` to `int(free)>15669` and removes ` and int(util)<=5`. It retains zero selected compute UUID rows, fresh UUID/memory/utilization observation, and the corrected original8GiB runtime disk floor. The inverse changed-line replacement reconstructs V2 byte-for-byte; full AST comparison changes only the one resource assertion as specified.

Use E0_PPO50_gas400_finite_worker_v3_original_resource_exact.py as new stage source. Bind TASK.worker_SHA and the actual executed bytes to the V3 SHA. The unchanged SDK CPU admission script may read these V3 bytes at its fixed root v1 basename; record this honestly as V3 content. Original actor35/critic38/STD/Adam/LR/D1-D7 restore,50Hz/400N physics, finite3900/3600save/300exit, and sole72 accounting remain unchanged. No GPU, remote operation, GO or canonical write was performed by this source correction. Pending root Git ordinary supplementation.
''',encoding='utf8')
 print(json.dumps(dict(worker=str(new),SHA=H(after),bytes=len(after),exact_replacements=2,AST_single_assertion_change=True,report=str(p))))
if __name__=='__main__':main()
