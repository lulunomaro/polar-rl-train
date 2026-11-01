"""Independent final286 actor/depth first episodes; reuse existing physics."""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;OLD=T/'LQR_MPC_DEPTH_TEACHER_STUDENT_V286_20261101'
R=N/'reports';R.mkdir(exist_ok=True);S=N/'source';S.mkdir(exist_ok=False)
shutil.copytree(OLD/'source',S,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(T/'MODEL2050_HUMAN_CLOSURE10MM_REGRESSION_V246_20261101/source/wheel_geometry220.py',S/'wheel_geometry220.py')
terrain=(S/'terrain286.py').read_text('utf8').replace('np.random.default_rng(286)','np.random.default_rng(9137)')
(S/'terrain287.py').write_text(terrain,encoding='utf8')
text=(OLD/'source/worker286.py').read_text('utf8');prefix=text[:text.index(' from actual_DR_memory_getter272 import')]
prefix=prefix.replace('from teacher_task286 import validate_task,validate_go','from contract287 import validate_task')
start=prefix.index("go=json.loads");end=prefix.index("assert hashlib.sha256(Path(__file__)",start)
prefix=prefix[:start]+"assert TASK['actual_parent_private_EX_and_authority_admitted'] and os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']\n"+prefix[end:]
prefix=prefix.replace("OUT=P/'production'","OUT=P/'actual_capture'").replace("deadline=go['save_deadline']","deadline=time.time()+TASK['worker_seconds']")
prefix=prefix.replace('terrain286 as sdk','terrain287 as sdk').replace("'--seed','27'","'--seed','9137'").replace('cfg.seed=27','cfg.seed=9137')
worker=prefix+(N/'eval287_tail.py').read_text('utf8');ast.parse(worker);(S/'evaluate287.py').write_text(worker,encoding='utf8')
shutil.copyfile(N/'contract287.py',S/'contract287.py')
normal=json.loads((OLD/'reports/ROOT286_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
cpu=json.loads((OLD/'reports/ROOT286_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes());assert normal['passed_collection']and cpu['passed']
base=json.loads((OLD/'TASK286_FROZEN.json').read_bytes())
task=dict(kind='FROZEN286_FINAL_DEPTH_HELDOUT270_AND_GROUND_EVAL287',source_run=normal['run_id'],
 model_path=normal['roles']['jump_72']['formal']['path'],model_SHA=cpu['SHA'],model_bytes=cpu['bytes'],
 qualified240_package_root=base['qualified240_package_root'],source_full_CPU_receipt_SHA=hashlib.sha256((OLD/'reports/ROOT286_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes()).hexdigest(),
 GPU_UUID=base['GPU_UUID'],num_envs=80,seed=9137,max_controls=400,worker_seconds=900,
 physics_dt=.0025,policy_hz=50,feedback_hz=100,TGS=[32,4],closure_m=.01,mimic_rad=.01,
 sdk_python='/home/lc01/Zonglin Li/zonglin2/run-python.sh',worker_SHA=hashlib.sha256((S/'evaluate287.py').read_bytes()).hexdigest(),
 optimizer_steps=0,model_byte_reads=1,model_decodes=1,account_writes=0,heldout_layout_seed=9137,training_layout_seed=286,
 first_episode_only=True,human_request='Replay final model, evaluate, decide whether to continue; after every round.',
 actual_parent_private_EX_and_authority_admitted=False)
from contract287 import validate_task
validate_task(task);(N/'TASK287_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
for p in S.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
(R/'SOURCE287_PROTOCOL.json').write_text(json.dumps(dict(epoch=time.time(),passed_AST=True,
 cases='72heldout270 firstepisodes max8s;8flat alternatingstanding,+.3,-.3m/s',original_physics_reward_DR_unchanged=True,
 previous_once_replayed=False,physics_tick_measurement=True,pose_replay_selected_cases=True,
 strict='first airborne/upward, both full authored wheel bounds cross270, loaded top footprint/stable.5s; no contact manifold identity claim'),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,source_files=len(list(S.rglob('*.py'))),model_SHA=task['model_SHA'])))
