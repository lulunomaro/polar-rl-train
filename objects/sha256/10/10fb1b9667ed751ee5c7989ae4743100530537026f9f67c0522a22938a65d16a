import importlib.util
from pathlib import Path
for module in ['isaaclab','isaaclab_physx']:
    base=Path(next(iter(importlib.util.find_spec(module).submodule_search_locations)))
    for p in (base/'assets').rglob('*.py'):
        lines=p.read_text().splitlines()
        for i,line in enumerate(lines):
            if ('def get_coms' in line or 'def body_com_pose_b' in line or 'def body_com_pos_b' in line
                or 'get_coms =' in line):
                print(str(p)+':'+str(i+1)+'\n'+'\n'.join(lines[i:i+38]))
