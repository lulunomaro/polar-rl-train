from pathlib import Path
import json,shutil,hashlib
D=Path(__file__).resolve().parent;repo=D.parent/'polar-rl-train';dest=repo/'sources/local/MOD4_LOCAL_MUJOCO_DRIVE_20261008'
dest.mkdir(parents=True,exist_ok=True)
names=['build_playground.py','current_sim.py','drive_latest.py','sim_runtime.py','policy_runtime.py','smoke_playground.py','pull_latest.py','START_WASD.bat','README.md','runtime_config.json','BUILD_RECEIPT.json','SMOKE_REVIEW.json','playground.xml']
for name in names:shutil.copyfile(D/name,dest/name)
receipt=json.loads((D/'DOWNLOAD_RECEIPT.json').read_text());started=json.loads((D/'INTERACTIVE_STARTED.json').read_text())
index={key:receipt[key] for key in ['epoch','role','root','run','checkpoint','checkpoint_sha256','checkpoint_bytes','snapshot_count','floating_tensors_finite','actual_child','no_training_interruption','no_GPU_or_budget_write']}
index['downloaded_checkpoint_periodic_not_behavior_reviewed']=True;index['training_source_freeze_sha256']=hashlib.sha256((D/'SOURCE_FREEZE.remote.json').read_bytes()).hexdigest();index['frozen_import_contract_sha256']=receipt['files']['src_snapshot/import_contract.json'];index['interactive_started']=started
index['large_artifacts_only_SHA']={name:hashlib.sha256((D/name).read_bytes()).hexdigest() for name in ['model_30900.pt','model_30900.onnx','terrain.npz']}
(dest/'DELIVERY_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf8')
note='''Human requested the latest complete 4090 checkpoint for local WASD driving in MuJoCo, with mild uneven terrain. Downloaded active D5 block2 trainer own model30900 (SHA039d3a8e8740a3ef33d5ddc3054159bacc6cf679572d4486e2be65ca0189355b), verified 255 source manifest, all31 snapshots and89 finite floating tensors, without interrupting learning, launching remote GPU work or mutating the budget.

Exported exact deterministic35-256-128-64-6 ELU actor with identity deployment action order.64 float32 export fixtures max action error0.000671387 on arbitrary random inputs. Preserved authored6 closures/4 mimics/8 free rollers and restored current import-contract nominal masses/inertias, limits, armatures, passive damping and gas spring parameters in an isolated MuJoCo model. Matched60/2 leg PD, wheel0.6, action scales, CAD target projection, torque-speed limits,35D inputs and actual closed-loop reset bank. No yaw/stabilization assistance. Added0-2.5cm green rolling track and0-8cm gentle blue ramp. MuJoCo uses its own0.5ms Newton integration/100Hz actor and clean nominal inputs, not equivalent to2.5ms PhysX or the entire D1-D5 randomization recipe.

Six actual headless local behavior cases stood/forward/reversed/turned/traversed ripples and ramp with finite upright state. Interface opened live Tk driver+MuJoCo viewer with focus-scoped hold-WASD, release-to-zero, speed control, stop, pause, reset and spawn selection. Own live startup receipt and subsequent actual telemetry were read back. These are local sim-to-sim smoke results, not Isaac retention graduation or hardware certification. Downloaded periodic30900 is not yet formally behavior-reviewed. Checkpoint/ONNX/heightfield arrays remain local and are indexed by SHA, no binary policy assets committed. Existing projects, training and3060 worker unchanged.
'''
(D/'EXPERIMENT_NOTE.md').write_text(note,encoding='utf8')
print(json.dumps({'files':[str((dest/n).relative_to(repo)).replace('\\','/') for n in names+['DELIVERY_INDEX.json']],'note':str(D/'EXPERIMENT_NOTE.md')},ensure_ascii=False))
