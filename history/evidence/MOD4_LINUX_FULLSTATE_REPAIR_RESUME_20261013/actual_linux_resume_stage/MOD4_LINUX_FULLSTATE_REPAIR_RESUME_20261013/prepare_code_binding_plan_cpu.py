"""Produce explicit frozen source ABI hashes; no imports of Isaac or GPU."""
from pathlib import Path
import ast,json,hashlib,torch
P=Path(__file__).resolve().parent
R=P.parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def find_timeout():
    import importlib.metadata as m
    d=m.distribution('isaaclab')
    files=[]
    for row in d.files or []:
        if str(row).replace('\\','/').endswith('/mdp/terminations.py'):
            p=Path(d.locate_file(row));files.append(p)
    # Editable package paths are located through their installed direct_url.
    if not files:
        url=json.loads(d.read_text('direct_url.json'))['url'];path=Path(url.removeprefix('file://'))
        files=list(path.rglob('terminations.py'))
    for p in files:
        text=p.read_text();node=next((x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name=='time_out'),None)
        if node:
            returns=[x for x in ast.walk(node) if isinstance(x,ast.Return)]
            assert len(returns)==1 and ast.unparse(returns[0].value)=='env.episode_length_buf >= env.max_episode_length'
            src=ast.get_source_segment(text,node)
            # inspect.getsource includes decorators when present; time_out has none.
            assert not node.decorator_list
            return hashlib.sha256(ast.unparse(ast.parse(src)).encode()).hexdigest(),dict(path=str(p),sha256=H(p),original_timeout_math_exact=True,return_expression=ast.unparse(returns[0].value))
    raise AssertionError('Actual installed native timeout source missing')

def main():
    src=R/'source/WINDOWS512_LAST_COMPLETE_28UPDATES.pt'
    ck=torch.load(src,map_location='cpu',weights_only=False)
    C=R/'runtime/isaac/mod4';timeout,proof=find_timeout()
    plan={key:{} for key in ('E1_terrain_state','E1_WAVE50_entry_reset_identity','E1_WAVE50_episode_direction_state','E1_WAVE50_route_lifecycle_state','E1_WAVE50_episode_lifetime_state')}
    values={'E1_terrain_state':{'entry_runtime_sha256':H(C/'wave50_entry_runtime_v2.py'),'entry_full_pose_sha256':H(C/'wave50_entry_full_pose_reset_v2.py')},'E1_WAVE50_entry_reset_identity':{'entry_runtime_sha256':H(C/'wave50_entry_runtime_v2.py'),'entry_full_pose_sha256':H(C/'wave50_entry_full_pose_reset_v2.py')},'E1_WAVE50_route_lifecycle_state':{'parent_boundary_source_sha256':H(C/'e1_terrain_runtime.py')},'E1_WAVE50_episode_lifetime_state':{'parent_timeout_source_sha256':timeout}}
    for state,fields in values.items():
        for field,new in fields.items():
            old=ck[state][field]
            if old!=new:plan[state][field]=dict(old=old,new=new,explicit_frozen_code_binding_only=True)
    output=P/'LINUX_CODE_BINDING_PLAN.json';assert not output.exists()
    output.write_text(json.dumps(dict(approved_code_changes=plan,timeout_source_CPU_equivalence=proof,source_SHA=H(src),no_GPU_or_physics_pass_claimed=True),indent=2))
    print(json.dumps(dict(path=str(output),changes=sum(len(x) for x in plan.values()),timeout=proof)))
if __name__=='__main__':main()
