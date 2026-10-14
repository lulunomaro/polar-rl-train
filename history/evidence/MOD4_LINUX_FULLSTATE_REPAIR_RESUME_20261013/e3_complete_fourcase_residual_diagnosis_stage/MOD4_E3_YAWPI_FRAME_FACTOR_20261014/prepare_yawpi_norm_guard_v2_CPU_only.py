"""Independent nonflat constructor fixture guard fix; no old source edits."""
from pathlib import Path
import json,time,hashlib,py_compile
D=Path(__file__).resolve().parent;P=D/'payload';R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(name,s):
 p=P/name;assert not p.exists();p.write_text(s,encoding='utf8');py_compile.compile(str(p),doraise=True)
s=(P/'yawpi_same_world_reset_factor_v1.py').read_text()
old=' assert torch.equal(out.square().sum(-1),q.square().sum(-1))'
assert s.count(old)==1
s=s.replace(old," assert torch.allclose(out.square().sum(-1),torch.ones(len(q),device=q.device,dtype=q.dtype),atol=1e-6,rtol=0)\n # Exact component permutation is the factor identity; floating reduction order\n # does not have to remain byteexact during pre-placement nonflat constructor reset.")
emit('yawpi_same_world_reset_factor_v2.py',s)
s=(P/'full80_yawpi_same_world_runtime_v1.py').read_text().replace('from yawpi_same_world_reset_factor_v1 import','from yawpi_same_world_reset_factor_v2 import');emit('full80_yawpi_same_world_runtime_v2.py',s)
s=(P/'paired_full80_yawpi_same_world_v1.py').read_text().replace('full80_yawpi_same_world_runtime_v1','full80_yawpi_same_world_runtime_v2');emit('paired_full80_yawpi_same_world_v2.py',s)
s=(P/'run_full80_yawpi_same_world_parent_v1.py').read_text().replace('paired_full80_yawpi_same_world_v1.py','paired_full80_yawpi_same_world_v2.py').replace('full80_yawpi_same_world_runtime_v1.py','full80_yawpi_same_world_runtime_v2.py');emit('run_full80_yawpi_same_world_parent_v2.py',s)
out=R/'YAWPI_FACTOR_NORM_GUARD_V2_PREPARED_ONLY.json';assert not out.exists();out.write_text(json.dumps(dict(epoch=time.time(),CPU_prepared_only=True,old_V1_preserved=True,why='Constructor before target Wave placement may have legitimate nonflat tangent quaternions. Norm is mathematically preserved but float32 reduction summation can change bitwise under permutation; original unit quaternion tolerance1e-6 retained, exact component permutation required.',original_V1_GPU_never_executed=True,components=[dict(path=str(P/n),relative=n,bytes=(P/n).stat().st_size,sha256=H(P/n)) for n in ('yawpi_same_world_reset_factor_v2.py','full80_yawpi_same_world_runtime_v2.py','paired_full80_yawpi_same_world_v2.py','run_full80_yawpi_same_world_parent_v2.py')],no_SSH_GPU_PPO_budget=True),indent=2),encoding='utf8')
print(str(out))
