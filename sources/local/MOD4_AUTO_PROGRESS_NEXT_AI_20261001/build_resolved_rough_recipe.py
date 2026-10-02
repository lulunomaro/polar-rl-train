"""Resolve active V14 v1 terrain definitions from verified source, without imports."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).parent
PINNED = ROOT/'rough_pinned_source'
TERRAIN = PINNED/'source/agent_tasks/agent_tasks/manager/mdp/isaaclab/terrains.py'
source = TERRAIN.read_text(encoding='utf8')
assignments = {node.targets[0].id: node for node in ast.parse(source).body
               if isinstance(node, ast.Assign) and len(node.targets) == 1
               and isinstance(node.targets[0], ast.Name)}
generator = assignments['RM_ROUGH_TERRAINS_CFG'].value
settings = {kw.arg: ast.literal_eval(kw.value) for kw in generator.keywords
            if kw.arg not in ('sub_terrains',)}
sub = next(kw.value for kw in generator.keywords if kw.arg == 'sub_terrains')
entries = []
for key, name in zip(sub.keys, sub.values):
    node = assignments[name.id]
    call = node.value
    entries.append({'key': ast.literal_eval(key), 'definition': name.id,
                    'class': ast.unparse(call.func), 'source_line': node.lineno,
                    'parameters': {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords},
                    'source': ast.get_source_segment(source, node)})
assert len(entries) == 11, len(entries)
result = {'commit': 'b8ff79f3df855faf9dc92f4a282bd80c42649466',
          'active_resolution': 'manager/mdp/__init__ -> isaaclab/__init__ -> terrains.py; terrains_ref.py is not the active exported default.',
          'generator_definition': 'RM_ROUGH_TERRAINS_CFG', 'generator_source_settings': settings,
          'runtime_overrides': {'curriculum': True, 'terrain_material_combine': 'multiply',
                                'terrain_material_static_friction': 1.0, 'terrain_material_dynamic_friction': 1.0},
          'active_terrain_definitions': entries,
          'important_curriculum_note': 'Low difficulty does not make every family a tiny step: low/high-speed stair minima are 0.15 m. Do not describe the entire upstream set as only low steps.',
          'stage': 'verified_recipe_only_not_a_runtime_adapter', 'production_modified': False}
(ROOT/'ROUGH_V1_RESOLVED_RECIPE.json').write_text(json.dumps(result, ensure_ascii=True, indent=2))
print(json.dumps({'terrain_count': len(entries), 'active_keys': [x['key'] for x in entries]}))
