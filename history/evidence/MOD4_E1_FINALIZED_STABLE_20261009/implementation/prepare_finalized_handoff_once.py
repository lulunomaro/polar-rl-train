from pathlib import Path
import ast,json,shutil
D=Path(__file__).resolve().parent;B=D.parent
N=B/'MOD4_S3_E1_FINALIZED_BEHAVIOR_HANDOFF_20261009';assert not N.exists();(N/'reports').mkdir(parents=True)
controller=(D/'supervise_e1_behavior_stable_continuation.py').read_text()
controller=controller.replace('len(f)==311','len(f)==312')
ast.parse(controller);(N/'supervise_e1_finalized_behavior_continuation.py').write_text(controller,encoding='utf8')
for name in ('E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json'):
 shutil.copyfile(D/'reports'/name,N/'reports'/name)
cpu=(D/'cpu_behavior_admission.py').read_text()
cpu=cpu.replace('MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009/reports','MOD4_S3_E1_FINALIZED_BEHAVIOR_HANDOFF_20261009/reports')
cpu=cpu.replace('rows={};pending=[]','rows={};pending=[]')
cpu=cpu.replace("   if not (folder/n).exists():pending.append(j);continue\n    if not (dest/n).exists():shutil.copyfile(folder/n,dest/n)\n    assert hashlib.sha256((dest/n).read_bytes()).hexdigest()==p['full_route_raw']['sha256'];row['raw_SHA_exact']=True", "   if not (folder/n).exists():pending.append(j);continue\n    # The result JSON can arrive before the separate bounded raw upload.\n    # Only SHA-finalized bytes are copied and admitted; stale local copies are never reused.\n    digest=hashlib.sha256((folder/n).read_bytes()).hexdigest()\n    if digest!=p['full_route_raw']['sha256']:\n     since=mismatch_since.setdefault(j,time.time())\n     write(R/'RAW_TRANSFER_PENDING.json',dict(epoch=time.time(),job_id=j,observed_sha256=digest,expected_sha256=p['full_route_raw']['sha256'],seconds=time.time()-since,no_pass_written=True))\n     if time.time()-since>600:raise AssertionError(('Raw transfer did not finalize within bounded admission wait',j,digest))\n     pending.append(j);continue\n    if not (dest/n).exists():shutil.copyfile(folder/n,dest/n)\n    assert hashlib.sha256((dest/n).read_bytes()).hexdigest()==p['full_route_raw']['sha256'];row['raw_SHA_exact']=True")
assert 'mismatch_since.setdefault' in cpu
cpu=cpu.replace(' while True:\n  rows=', ' mismatch_since={}\n while True:\n  rows=')
ast.parse(cpu);(N/'cpu_behavior_finalized_admission.py').write_text(cpu,encoding='utf8')
review=(D/'cpu_review_completed_behavior.py').read_text().replace('MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009/isaac/mod4','MOD4_S3_E1_FINALIZED_BEHAVIOR_HANDOFF_20261009/isaac/mod4')
ast.parse(review);(N/'review_completed_behavior.py').write_text(review,encoding='utf8')
reader=(D/'read_stable_actual.py').read_text().replace('supervise_e1_behavior_stable_continuation','supervise_e1_finalized_behavior_continuation')
(N/'read_stable_actual.py').write_text(reader,encoding='utf8')
print('Independent finalized handoff prepared; all old source and failed CPU evidence retained')
