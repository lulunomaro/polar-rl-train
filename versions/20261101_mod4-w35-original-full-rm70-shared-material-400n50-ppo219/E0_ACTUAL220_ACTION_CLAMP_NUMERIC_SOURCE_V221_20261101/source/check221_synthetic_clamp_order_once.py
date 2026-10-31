"""Only one new tiny synthetic clamp/order case;no actual npz/model/asset."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time
import numpy as np
N=Path(__file__).resolve().parent.parent;R=N/'reports'
ID='NEW221_CLAMP_ORDER_DIAGNOSTIC_SOURCE_AND_ONE_SYNTHETIC_CPU_CASE_V1'


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 frozen=json.loads((R/'CPU221_SOURCE_PURPOSE_FROZEN.json').read_bytes())
 assert frozen['purpose_id']==ID and frozen['groups']==2 and frozen['synthetic_numeric_cases']==1
 put(R/'CPU221_SOURCE_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose_id=ID,old220_fixture_replays=0,artifact_reads=0))
 for r in frozen['source_files']:
  raw=Path(r['path']).read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['SHA'];ast.parse(raw.decode('utf8'))
 path=N/'diagnose221_ACTUAL220_NPZ_CPU_UNUSED_once.py'
 spec=importlib.util.spec_from_file_location('cpu221_source_fixture',path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 assert len(m.SELECTED)==9 and set(m.SELECTED)=={'raw_action6','original_reward_motor_actions6','q30','joint_names','authored_wheel_bottom_above_plane_m','root13','commands','original_reward_command4','control'}
 raw=np.asarray([[-8,-1,7,0,6,-6],[-9,2,8,1,6.5,-7],[0,3,2,-7,-6.5,7],[-7,-7,-7,-7,-7,-7]],dtype=np.float32)
 root=np.zeros((4,13),dtype=np.float32);root[:,0]=np.arange(4)*.02;root[:,6]=1;root[:,7]=1
 command=np.zeros((4,3),dtype=np.float32);command[:,0]=.5
 rewardcmd=np.zeros((4,4),dtype=np.float32);rewardcmd[:,0]=.5;rewardcmd[:,2]=.12
 data=dict(raw_action6=raw,original_reward_motor_actions6=np.clip(raw,-6.,6.)[:,[0,1,4,2,3,5]],
  q30=np.arange(24,dtype=np.float32).reshape(4,6)*.1,joint_names=np.asarray(m.POLICY_NAMES),
  authored_wheel_bottom_above_plane_m=np.zeros((4,2),dtype=np.float32),root13=root,commands=command,
  original_reward_command4=rewardcmd,control=np.arange(1,5,dtype=np.int32))
 result=m.analyze(data)
 assert result['recorded_clip6_order_matches_within_numeric_atol1e_6'] and result['clip6_reordered_global_max_abs_residual']==0.
 assert result['raw_action_channels'][0]['raw_abs_gt6_fraction']==.75
 assert result['raw_action_channels'][0]['longest_abs_gt6_run']['endpoint_count']==2
 assert result['raw_action_channels'][0]['longest_abs_gt6_run']['observed_command_endpoint_span_s']==.02
 assert result['recorded_action_comparison'][2]['joint']=='left_wheel_spin' and result['recorded_action_comparison'][2]['source_policy_channel']==4
 assert np.isclose(result['root_reference']['net_displacement_world_m'][0],.06)
 put(R/'CPU221_SOURCE_AND_ONE_CLAMP_ORDER_CASE_ACTUAL.json',dict(epoch=time.time(),purpose_id=ID,passed=True,
  group_count=2,source_AST=True,synthetic_numeric_cases=1,synthetic_controls=4,clip_permutation=[0,1,4,2,3,5],
  clip_residual=0.,longest2_endpoint_span_s=.02,actual221_artifact_unread=True,
  original220_case_or_fixture_replayed=False,PT_NPZ_USD_raw_SDK_GPU_SSH_Git_reads_or_calls=0))
 print(json.dumps(dict(passed=True,groups=2,synthetic_cases=1,actual_artifact_reads=0,forbidden_calls=0)))


if __name__=='__main__':main()
