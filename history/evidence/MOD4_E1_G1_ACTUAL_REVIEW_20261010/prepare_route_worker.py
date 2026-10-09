from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
p=W/'MOD4_S3_E1_FULL_DR_TERRAIN_PREPARE_20261009/eval_worker_e1_curriculum_interface_review.py';b=p.read_bytes()
assert hashlib.sha256(b).hexdigest()=='39965b7a0e55a8469535c6c4d97f950432fa0c7a7de7e76478935066e7840f7d'
s=b.decode().replace('E1_CURRICULUM_INTERFACE','E1_FULL_ROUTE_REVIEW')
needle="PAUSED_SHALLOW_JOBS=";assert s.count(needle)==1
s=s.replace(needle,"RETIRED=RETIRED+('clk2500-closure-episode-d3-119-e1-g1-fullroute-anchor32053-flat','clk2500-closure-episode-d3-119-e1-g1-fullroute-candidate32098-flat')\n"+needle)
ast.parse(s);out=D/'eval_worker_e1_full_route_review.py';assert not out.exists();out.write_text(s,encoding='utf8')
(R/'ROUTE_WORKER_CPU_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-ROUTE-WORKER-PREPARE-01',new_source_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),old_source_sha256=hashlib.sha256(b).hexdigest(),only_namespace_and_two_exact_failed_neverrun_IDs_changed=True,normal_errors_still_attention=True,shared_original_lock_and_bridge=True,no_canonical_or_training_authority=True),indent=2),encoding='utf8')
