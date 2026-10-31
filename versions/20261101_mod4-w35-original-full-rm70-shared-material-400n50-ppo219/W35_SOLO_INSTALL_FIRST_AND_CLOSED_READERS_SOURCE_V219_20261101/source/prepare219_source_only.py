"""Generate independent219 source/control/readers from frozen sources. No assets."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent.parent;T=N.parent
P218=T/'W35_SHARED_MATERIAL_NEXT_SOLO_SOURCE_V218_20261101'
P210=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031'


def ref(p):
 p=Path(p);assert p.suffix in ('.py','.json','.md','.txt');b=p.read_bytes()
 return dict(local_path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def write(p,s):
 with p.open('xb') as f:f.write(s)
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)


def main():
 (N/'reports').mkdir(exist_ok=True);(N/'control219').mkdir(exist_ok=False)
 for name in ['contract218.py','solo218_protocol.py']:
  raw=(P218/'source'/name).read_bytes();write(N/'source'/name,raw);write(N/'control219'/name,raw)
 changes=[]
 control=P210/'control';dest=N/'control219'
 owner=(control/'mixed210_finite_owner_authority72.py').read_bytes().decode('utf8')
 for a,b in [('from owner210_protocol import validate_schedule,flat_go_fields','from solo218_protocol import validate_schedule,flat_go_fields'),
  ("set(specs)=={'e0_72'}","set(specs)=={'w35_72'}"),
  ('human_requested_E0_latest_branch_mixed_three_hour','human_requested_W35_shared_material_one_hour'),
  ('Linux_MIX210_E0_GROUND10_JUMP90_THREE_HOUR_','Linux_W35_SHARED214_SOLO219_ONE_HOUR_')]:
  owner=replace(owner,a,b);changes.append(dict(file='solo219_finite_owner_authority72.py',old=a,new=b))
 write(dest/'solo219_finite_owner_authority72.py',owner.encode())
 common=(control/'three_slot_common_v1.py').read_bytes().decode('utf8')
 common=replace(common,'from owner210_protocol import valid_ready','from solo218_protocol import valid_ready')
 write(dest/'three_slot_common_v1.py',common.encode())
 node=(P210/'control_v2/parallel210_fullstate_slot_node.py').read_bytes().decode('utf8')
 node=replace(node,'ADMISSION210_READY.json','ADMISSION218_READY.json')
 write(dest/'solo219_fullstate_slot_node.py',node.encode())
 for name in ['single_writer72_authority_V85M_source.py','forwarded_original_owner_control_v1.py']:
  write(dest/name,(control/name).read_bytes())
 control_rows=[dict(**ref(p),relative=p.name) for p in sorted(dest.glob('*.py'))]
 put(N/'reports/CONTROL219_FROZEN_MANIFEST.json',dict(kind='ROOT219_DERIVED_ORIGINAL_SOLO_SOURCE_ONLY',files=control_rows,
  changes=changes+[dict(file='three_slot_common_v1.py',change='valid_ready protocol import only'),dict(file='solo219_fullstate_slot_node.py',change='Ready filename only;original W35 branch/worker spec/wait unchanged')],
  original_HMAC_charge_twofcntl_authority_STOP_Appclose_wait_terminal_logic_preserved=True))
 bindings=json.loads((P218/'reports/INSTALL218_FROZEN_SOURCE_BINDINGS.json').read_bytes())
 source_input=json.loads(Path(bindings['base_install_metadata']['path']).read_bytes())
 files={r['installed_relative']:dict(relative=r['installed_relative'],local_path=r['local_path'],bytes=r['bytes'],SHA=r['SHA']) for r in source_input['base_rows']}
 for r in source_input['all_binaries_metadata_only']:
  files[r['installed_relative']]=dict(relative=r['installed_relative'],local_path=r['local_path'],bytes=r['bytes'],SHA=r['SHA'])
 for r in bindings['overlay']:
  files[r['installed_relative']]=dict(relative=r['installed_relative'],local_path=r['path'],bytes=r['bytes'],SHA=r['SHA'])
 old=json.loads((P210/'PACKAGE210_W35_MANIFEST.json').read_bytes())
 for r in old['files']:
  if r['relative']=='original_run_manifest.json' or 'asset_relative' in r:
   files[r['relative']]={k:v for k,v in r.items() if k in ('relative','local_path','bytes','SHA','asset_relative')}
 assert all(not k.endswith('.pt') for k in files)
 assert files['original_run_manifest.json']['SHA']=='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
 put(N/'reports/INSTALL219_SOURCE_ROWS_FROZEN.json',dict(status='SOURCE_MAP_ONLY_ROOT_INSTALLER_UNUSED',
  source218_INDEX_SHA='6578d66cd1aa1e68da9c054f3efc09bfe38dc20194e7ae6524165b390911f365',
  source218_bindings_SHA='6dca140a744b0e274572563bd4467070425496a5e6a1a47a1a293567bd02e37a',
  files=[files[k] for k in sorted(files)],source_model=bindings['source_model_metadata'],binary_model_reads_by_generator=0))
 normal=(P210/'collect210_original_two_role_formals_cost_normal900_UNUSED_once.py').read_bytes().decode('utf8')
 start=normal.index("  result=d.code(client,d.PY72,COLLECT_NODE,dict(spec=specs['e0_72'])")
 end=normal.index("  result=d.code(client,d.PY72,COLLECT_NODE,dict(spec=specs['w35_72'])",start)
 normal=normal[:start]+normal[end:]
 normal=normal.replace('ROOT210_','ROOT219_').replace('control210v2','control219').replace('current_closed210_models','current_closed219_models')
 normal=normal.replace('ORIGINAL_OWNER_TWO_RAW_FEES_CLOSED_ACTUAL','ORIGINAL_SOLO_OWNER_ONE_RAW_FEE_CLOSED_ACTUAL')
 normal=replace(normal,'ROOT219_ORIGINAL_UNIFIED_OWNER_LAUNCH_ACTUAL.json','ROOT219_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json')
 normal=replace(normal,'ROOT219_UNIFIED_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json','ROOT219_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
 normal=normal.replace('collect210_original_two_role_formals','collect219_original_W35_formal').replace('|launch210_|','|launch219_|launch210_|')
 oldq="qualified=bool(t['row']['returncode']==0"
 normal=replace(normal,oldq,"material_errors=[line for textrow in texts for line in textrow['UTF8'].splitlines() if 'PxPhysics::createMaterial' in line and '64K' in line]\nqualified=bool(not material_errors and t['row']['returncode']==0")
 normal=replace(normal,"qualified_formal=qualified,formal=formal,final=final,errors=errors,","qualified_formal=qualified,formal=formal,final=final,errors=errors,actual_material_limit_error_count=len(material_errors),original_material_error_lines=material_errors,")
 normal=normal.replace('One terminal collection of the original two-slot197 cohort; no extra GO.','One original normal900 collection of219 soleW35; no extra GO.')
 write(N/'collect219_original_W35_formal_cost_normal900_UNUSED_once.py',normal.encode())
 put(N/'reports/NEW219_SOURCE_SCOPE_AND_PENDING_ACTUAL.json',dict(epoch=time.time(),
  status='NEW_LOCAL_SOURCE_ONLY_NO_ROOT_EXECUTION_OR_GO', installer_FIRST_complete=True, normal900_complete=True,new_formalCPU_reader_complete=True,
  first_gate='actual210 normal closing + matching NEW CPU;missing report refuses before CIM/network/asset/PT',
  no_early210_normal_collection=True, root_only_remote_execution=True, old_model_CPU_PT_reads=0,
  all_saved_reports_pending_root_unified_Git=True, source_generation_asset_PT_NPZ_USD_raw_SDK_GPU_SSH_Git_reads_or_calls=0,
  preserved_reader_note='One broad219 source filename inventory clipped tool output;only source listing,no binary/fixture/robot execution.'))
 print(json.dumps(dict(source_only_generated=True,install_rows=len(files),control_files=len(control_rows),root_remote_calls=0)))


if __name__=='__main__':main()
