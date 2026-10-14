from pathlib import Path
import json,time
D=Path(__file__).resolve().parent
err=D/'reports/V2_FIXTURE_SHELL_QUOTING_ORIGINAL_ERROR.json'
assert not err.exists();err.write_text(json.dumps(dict(epoch=time.time(),stage='local CPU fixture preparation, before file write or GPU/SSH',error='Python -c triple quoted multiline snippet was truncated by PowerShell quote boundary: SyntaxError unterminated triple-quoted string literal. Subsequent v2 fixture path was absent. No fixture executed. Independent saved script now prepares only not-yet-written v2 fixture.',no_GPU_SSH_PPO=True),indent=2),encoding='utf8')
s=(D/'review_yawpi_factor_CPU_fixture_only.py').read_text()
s=s.replace('import yawpi_same_world_reset_factor_v1 as f','import yawpi_same_world_reset_factor_v2 as f').replace('full80_yawpi_same_world_runtime_v1.py','full80_yawpi_same_world_runtime_v2.py').replace('yawpi_same_world_reset_factor_v1.py','yawpi_same_world_reset_factor_v2.py').replace('YAWPI_FACTOR_FULLBANK_ACTUAL_SOURCE_CPU_FIXTURE_PASSED.json','YAWPI_FACTOR_V2_FULLBANK_ACTUAL_SOURCE_CPU_FIXTURE_PASSED.json')
insert='''# Additional legitimate nonflat pre-placement constructor fixture, deterministic.
angles=np.stack((np.linspace(-1.,1.,80),np.linspace(-.4,.4,80),np.linspace(.3,-.3,80)),1)
root[:,3:7]=torch.tensor(Rotation.from_euler('ZYX',angles).as_quat(),dtype=torch.float32)
f.full_reset_yawpi_same_world(env,None)
nonflat=robot.data.root_state_w.clone();assert torch.equal(nonflat[:,3:7],torch.stack((-root[:,4],root[:,3],root[:,6],-root[:,5]),-1))
assert torch.equal(torch.get_rng_state(),rng) and torch.equal(robot.data.joint_pos,q)
'''
assert s.count('out=R/')==1;s=s.replace('out=R/',insert+'out=R/').replace('synthetic_flat_query_only=True','synthetic_flat_query_only=True,synthetic_nonflat_constructor80_quaternions_exact=True')
o=D/'review_yawpi_factor_v2_CPU_fixture_only.py';assert not o.exists();o.write_text(s,encoding='utf8')
