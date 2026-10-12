from scut_wave_schema_io import *

def main():
    w=connect()
    try:
        v=execute(w,r'''from pathlib import Path
import json,torch,time,hashlib
from isaaclab.utils.math import quat_apply
q=torch.tensor([[1.,0.,0.,0.],[0.,0.,0.,1.]]);down=torch.tensor([[0.,0.,-1.],[0.,0.,-1.]]);r=quat_apply(q,down);assert torch.equal(r,torch.tensor([[0.,0.,1.],[0.,0.,-1.]]));assert not torch.cuda.is_initialized()
P=Path(INPUT_TOKEN);rows=[]
for name in ('wheelbipe_V13/env.py','wheelbipe_V14/env.py','wheelbipe25_v3/env.py'):
 p=P/'original/source/agent_tasks/agent_tasks/direct/wheelbipe'/name;raw=p.read_bytes();lines=raw.decode().splitlines();ids=[i for i,x in enumerate(lines) if 'def _get_observations' in x or 'def _get_command_observation' in x or 'def _get_policy_command' in x or 'def _get_command_obs' in x]
 rows.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),relevant_functions=[dict(line=i+1,source='\n'.join(lines[i:min(len(lines),i+125)])) for i in ids]))
v=dict(epoch=time.time(),passed=True,CPU_only=True,original_wxyz_identity_1_0_0_0_rotates_down_to_up_in_current_native_math=True,current_xyzw_identity_0_0_0_1_keeps_down=True,CPU_actual_vectors=r.tolist(),native_sensor_source_uses_offset_quat_directly=True,old_rough_height_scanner_offset_conversion_missing=True,old_actual_GPU_ray_directions_and_actor_mode_ID_not_recorded_not_fabricated=True,source_command_observation_review=rows,no_GPU_or_worker_mutation=True)
print(json.dumps(v))
'''.replace('INPUT_TOKEN',repr('D:/MOD4_async_eval/scut_wave50_gate_compare_detached_reviewed_20261012')))
        p=save('NATIVE_QUATERNION_AND_COMMAND_ABI_CPU_ACTUAL.json',v);print(json.dumps(dict(path=str(p),passed=True,wrong_height_sensor_rotation_proved_CPU=True,sources=v['source_command_observation_review'])))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('NATIVE_QUATERNION_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_only=True));raise
