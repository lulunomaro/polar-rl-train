"""Copy original207 AppLauncher PY and freeze a NEW minimal local CPU purpose."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent.parent;T=N.parent;R=N/'reports'


def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 R.mkdir(exist_ok=True)
 app=T/'QUALIFIED_PRIMARY_E0_ZERO_YAW_EVAL_V207_20261031/e0/zonglin2_app_launcher.py'
 with (N/'zonglin2_app_launcher.py').open('xb') as f:f.write(app.read_bytes())
 put(R/'APP220_ORIGINAL207_SOURCE_COPY.json',dict(source=ref(app),copy=ref(N/'zonglin2_app_launcher.py'),
  source_only=True,SDK_import=False,asset_or_model_reads=0))
 files=list(N.rglob('*.py'))+[T/'QUALIFIED_PRIMARY_E0_ZERO_YAW_EVAL_V207_20261031/evaluate207_qualified_actor_zero_yaw_once.py',
  T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/package/jump194_sdk.py']
 put(R/'CPU220_PURPOSE_FROZEN.json',dict(purpose_id='NEW220_NEW210_MODEL_CURRENT219_BINDING_AND_AUTHORED_PLANE_ENDPOINT_EVIDENCE_CPU_V1',
  frozen_epoch=time.time(),groups=3,expected_refusals=11,source_files=[ref(p) for p in sorted(files)],
  scope='Source AST/no new physics path;synthetic F32 xyzw support/two-endpoint/contact/censored math;new formal/current exact owner JSON binding.',
  PT_NPZ_USD_raw_SDK_GPU_SSH_Git_reads_or_calls=0,old207_218_fixture_replays=0,execution='ONCE_NO_REENTRY',
  synthetic_points_not_used_as_real_robot_or_scene_geometry=True,new_training_gate=False))
 print(json.dumps(dict(purpose_frozen=True,groups=3,refusals=11,source_rows=len(files),forbidden_calls=0)))


if __name__=='__main__':main()
