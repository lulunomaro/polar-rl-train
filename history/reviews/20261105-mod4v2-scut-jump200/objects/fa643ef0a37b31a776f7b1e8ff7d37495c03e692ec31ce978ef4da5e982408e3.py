"""Exercise the v2 configure wrapper without importing SDK or a checkpoint."""
from pathlib import Path
from types import SimpleNamespace
import ast, hashlib, json, time

root = Path(__file__).resolve().parent
path = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/project/isaac/mod4v2_scut/sdk.py')
raw = path.read_bytes()
function = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'configure')
calls = []
source = SimpleNamespace(MESH='/World/ground/scut_step270')
def configure_original(cfg, n, profile, contract):
    source.MESH = '/World/ground/scut_jump200'
    calls.append((n, profile, contract))
source.configure = configure_original
reset = object()
namespace = dict(_source=source, MESH='/World/ground/scut_step270', consistent_reset_v2=reset)
exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), namespace)
cfg = SimpleNamespace(events=SimpleNamespace(consistent_start=SimpleNamespace(func=None)),
                      sim=SimpleNamespace(physics=SimpleNamespace(solver_type=None)))
namespace['configure'](cfg, 80, 'jump200', 'unchanged-contract')
assert namespace['MESH'] == source.MESH == '/World/ground/scut_jump200'
assert calls == [(80, 'jump200', 'unchanged-contract')]
assert cfg.events.consistent_start.func is reset and cfg.sim.physics.solver_type == 1
result = dict(epoch=time.time(), passed=True, source_path=str(path),
              source_SHA=hashlib.sha256(raw).hexdigest(),
              actual_configure_function_exercised=True, selected_mesh=namespace['MESH'],
              source_configure_calls=len(calls), SDK_imports=0, model_reads=0, physics_steps=0,
              reset_and_solver_configuration_preserved=True)
with (root/'attempt03/reports/MESH_BINDING_CPU.json').open('x', encoding='utf8') as stream:
    json.dump(result, stream, indent=2)
print(json.dumps(result))
