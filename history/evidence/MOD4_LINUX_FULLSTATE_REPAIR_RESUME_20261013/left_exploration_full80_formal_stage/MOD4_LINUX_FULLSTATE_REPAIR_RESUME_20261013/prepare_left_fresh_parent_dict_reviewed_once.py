"""Continue only the not-created parent after a retained pre-GPU builder assertion."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent
old=D/'prepare_left_fresh_samebranch_consumers_once.py';worker=D/'left_exploration_worker_v2.py';assert worker.exists()
assert not (D/'left_fresh_samebranch_parent_v1.py').exists()
tree=ast.parse(old.read_text());node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='replacements' for t in n.targets))
changes=ast.literal_eval(node.value)
error=D/'reports/LEFT_FRESH_ORIGINAL_BUILDER_PRE_GPU_ASSERTION.json'
assert not error.exists();error.write_text(json.dumps(dict(epoch=time.time(),original_source=str(old),original_source_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),error='AssertionError: actor_optimizer_unchanged_during_physics_probe',classification='CPU builder expected a worker-only receipt field inside parent source',workerV2_already_saved=True,parent_and_GPU_NOT_created=True,no_oldonce_or_GPU_replayed=True),indent=2),encoding='utf8')
changes.pop('actor_optimizer_unchanged_during_physics_probe')
s=(D/'left_exploration_native_parent_v1.py').read_text()
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
q=D/'left_fresh_samebranch_parent_dict_reviewed_v2.py';assert not q.exists();compile(s,str(q),'exec');q.write_text(s,encoding='utf8')
compile(worker.read_text(),str(worker),'exec')
(D/'reports/LEFT_FRESH_CONSUMERS_CPU_DICT_REVIEWED_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),CPU_compiled=True,parent=str(q),parent_SHA=hashlib.sha256(q.read_bytes()).hexdigest(),already_saved_workerV2_SHA=hashlib.sha256(worker.read_bytes()).hexdigest(),only_unexecuted_parent_preparation_continued=True,original_builder_error_preserved=True,zero_controls_zero_PPO_explicit_fresh_same20k_branch=True,source_own1e_no_discard_warmstart=True,initializer_will_not_repeat=True,actual13_CPUCUDA_and_source_episode_plus_one_STILL_pending=True,fresh_GPU_NOT_dispatched=True,qualified50=False),indent=2),encoding='utf8')
print(str(q))
