from pathlib import Path
import importlib.util
import json

spec=importlib.util.find_spec('isaaclab')
base=Path(next(iter(spec.submodule_search_locations)))
print(json.dumps({'isaaclab':str(base)}))
for relative,patterns in [('envs/mdp/events.py',['class _RandomizeRigidBodyMaterialPhysx']),
                         ('assets/articulation/base_articulation.py',['def set_masses_index','def set_inertias_index','def set_material']),
                         ('assets/articulation/articulation_data.py',['body_inertia','body_mass'])]:
    path=base/relative
    lines=path.read_text().splitlines()
    for index,line in enumerate(lines):
        if any(pattern in line for pattern in patterns):
            if relative.endswith('_data.py'):continue
            count=230 if 'class randomize' in line else 60
            print(str(path)+':'+str(index+1)+'\n'+'\n'.join(lines[index:index+count]))
