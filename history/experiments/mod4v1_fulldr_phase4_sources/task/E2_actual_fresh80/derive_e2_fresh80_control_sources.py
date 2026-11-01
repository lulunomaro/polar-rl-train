"""Reuse only bounded control scaffold; the environment/trainer/base are strict E2."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
pairs=[
 ('prepare_e0_remote_stage_once.py','prepare_e2_remote_stage_once.py'),
 ('probe_e0_fresh80_no_pt_v1.py','probe_e2_fresh80_no_pt_v1.py'),
 ('supervise_e0_fresh80_v1.py','supervise_e2_fresh80_v1.py'),
 ('dispatch_e0_fresh80_v1_once.py','dispatch_e2_fresh80_v1_once.py'),
]
for old,new in pairs:
 text=(ROOT/'E0_actual_fresh80'/old).read_text(encoding='utf-8').replace('E0','E2').replace('e0','e2')
 text=text.replace('MOD4_E2_PPO50_GAS400_2610v89d','MOD4_E2_PPO50_GAS400_2610v93')
 text=text.replace("staged_sources/E2_MOD4V1_SOURCE_FINAL","staged_sources/E2_MOD4V1_SOURCE_V1")
 text=text.replace('1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1','ad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f')
 if old.startswith('prepare_'):
  anchor="B.mkdir();shutil.copytree(S/'runtime',B/'runtime',ignore=ignore)"
  assert anchor in text
  text=text.replace(anchor,anchor+"\nif (S/'lib').is_dir():shutil.copytree(S/'lib',B/'lib',ignore=ignore)")
 if old.startswith('probe_'):
  anchor="    storage=job/'kit_isolation'"
  assert anchor in text
  text=text.replace(anchor,"    os.environ.update(OWN_E2_H1_KIND='E2_WORLD_MOVING_SIGNED4',RM_SPAWN_GRACE_STEPS='5',RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')\n"+anchor)
  text=text.replace("sys.path[:0]=[str(mod),str(job/'runtime')]","sys.path[:0]=[str(mod),str(job/'runtime'),str(job/'lib')]")
  anchor="        env=ns['build_env']();robot=env.scene['robot'];identity=ns['E2_IDENTITY']"
  assert anchor in text
  text=text.replace(anchor,anchor+"\n        term=env.command_manager.get_term('twist');assert type(term).__module__=='e2_directional_spin_runtime_v1' and term._dt==.02\n        assert os.environ['OWN_E2_H1_KIND']=='E2_WORLD_MOVING_SIGNED4'")
  text=text.replace("scope='E2 original flat fresh80 noPT timing/finiteness/D0-D7 component validation only'","scope='Original E2 WORLD_MOVING_SIGNED4 fresh80 noPT integration only'")
 ast.parse(text)
 with (HERE/new).open('x',encoding='utf-8') as f:f.write(text)
print(json.dumps({'E2_new_control_sources':[new for old,new in pairs],'E2_base':'original93 runtime plus E2_COMPLETE_INSTALL_MANIFEST and E2_FINAL source overlay','E2_environment':'E2H1FlatEnv pinnedE2_WORLD_MOVING_SIGNED4; not E0/H1jump','PT_or_SDK_started_by_derivation':False},indent=2))
