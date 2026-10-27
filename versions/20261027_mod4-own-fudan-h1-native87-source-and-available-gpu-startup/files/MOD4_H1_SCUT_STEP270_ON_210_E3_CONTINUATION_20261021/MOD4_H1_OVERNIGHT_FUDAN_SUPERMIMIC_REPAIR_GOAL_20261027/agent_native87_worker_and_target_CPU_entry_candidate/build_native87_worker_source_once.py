"""Exact old-worker source adaptation, never executes the generated worker."""
from pathlib import Path
import hashlib,json,ast
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
OLD=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/h1_unisupermimic_step270_worker_v1.py'
raw=OLD.read_bytes();(D/'ORIGINAL_NATIVE86B_WORKER_BYTES.txt').write_bytes(raw);s=raw.decode()
oldline=next(x for x in s.splitlines() if x.startswith(' p=argparse.ArgumentParser();'))
new=" p=argparse.ArgumentParser();p.add_argument('--job',type=int,default=0);p.add_argument('--slot',choices=('h1','e2','recovery'),required=True);p.add_argument('--phase',choices=('production',),required=True);p.add_argument('--num-envs',type=int,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--source-scope',choices=('policy_only_fresh_environment',),required=True);args=p.parse_args();phase=args.phase;assert args.job==0 and args.num_envs==4096;task=json.loads((J/'TASK.json').read_bytes());go=json.loads((J/'GO_PRODUCTION.json').read_bytes());assert args.slot==task['key'] and args.seed==task['native_seed'];from native87_source_guard_v1 import check_payload,validate_task_go;checked=check_payload(B);validate_task_go(task,go,checked['manifest_SHA']);assert time.time()<go['save_deadline'];src=J/'source'/task['source_filename'];assert H(src)==go['bootstrap_SHA'];assert not (J/phase).exists();out=J/phase;out.mkdir();fresh=False;N=4096"
s=s.replace(oldline,new,1)
changes=[
 ("sys.path.insert(0,str(B/'source'))","sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps')]") ,
 ("'--seed','20260928'","'--seed',str(args.seed)"),
 ("c=original_cfg();assert c.scene.num_envs==20000 or N==20000;c.scene.num_envs=20000;c.seed=20260928;", "c=original_cfg();c.scene.num_envs=N;c.seed=args.seed;c.episode_length_s=5.;"),
 ("env._physics_action_delay.queue.control_us=10000;assert env.num_envs==20000", "assert env._physics_action_delay.queue.control_us==10000;assert env.num_envs==4096"),
 ("from h1_step270_fullstate_checkpoint_candidate_uninstalled import resume_step270_new_episode,install_step270_save_contract", "from h1_step270_fullstate_checkpoint_candidate_uninstalled import install_step270_save_contract\n from fresh_policy_only_bootstrap87_v1 import resume_policy_only_fresh4096"),
 ("checkpoint_API.resume_h1_new_episode=resume_step270_new_episode", "checkpoint_API.resume_h1_new_episode=resume_policy_only_fresh4096"),
 ("  from h1_supermimic_bridge_v1 import run", "  from native87_source_guard_v1 import validate_precontrol_actual\n  put(out/'NATIVE87_ACTUAL_BEFORE_FIRST_CONTROL_ADMISSION.json',validate_precontrol_actual(runner,created[0],task,go,B))\n  from native_own_fudan87_training import run")]
for old,new in changes:
    assert s.count(old)==1,old;s=s.replace(old,new,1)
ast.parse(s);destination=D/'h1_native_own87_worker_v1.py';destination.write_bytes(s.encode())
with (D/'WORKER_EXACT_ADAPTATION_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(original_path=str(OLD),original_SHA=hashlib.sha256(raw).hexdigest(),
    candidate_path=str(destination),candidate_SHA=hashlib.sha256(destination.read_bytes()).hexdigest(),exact_substitutions=len(changes)+1,
    no_original_runtime_modified=True,actual_source_worker_executed=False,actual_GPU_precontrol_required=True),f,indent=2)
# New preGO schema preserves original frozen protocol in its own directory.
P=L/'agent_three_H1_native87_sole72_protocol_candidate/native87_protocol_v1.py';text=P.read_text()
text=text.replace("KIND='MOD4_H1_NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU'","KIND='MOD4_H1_NATIVE87_POLICY_ONLY_SOURCE_SDK_CPU_PRECONTROL_V2'")
text=text.replace("'actual_fresh4096_environment_CPU_passed','actual_fresh_D0_D7_reset_CPU_passed'","'factory4096_timeout5_source_CPU_passed','fresh_policy_only_scope_source_CPU_passed'")
text=text.replace("'actual_runtime30joint_order_passed'","'expected_runtime30joint_order_source_CPU_passed','actual_GPU_precontrol_admission_required'")
text=text.replace("v.get('actual_environment_count')==4096","v.get('configured_environment_count')==4096 and v.get('actual_environment_count') is None and v.get('actual_GPU_runtime_readback_passed') is False and v.get('actual_GPU_fresh4096_DR_readback_passed') is False")
ast.parse(text);(D/'native87_protocol_v1.py').write_text(text,encoding='utf8')
print(json.dumps(dict(worker_source_only=True,protocol_preGO_scope_corrected=True)))
