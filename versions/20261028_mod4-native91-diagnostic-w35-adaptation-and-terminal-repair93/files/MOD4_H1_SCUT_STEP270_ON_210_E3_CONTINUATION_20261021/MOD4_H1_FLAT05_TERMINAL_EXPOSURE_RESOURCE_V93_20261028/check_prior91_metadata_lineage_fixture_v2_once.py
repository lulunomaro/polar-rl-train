"""Metadata fixture only, no checkpoint or SDK admission claim."""
from pathlib import Path
import os,sys,json,time,traceback
N=Path(__file__).resolve().parent;B=N/'payload';R=N/'reports'
os.environ['CUDA_VISIBLE_DEVICES']=''
sys.path[:0]=[str(B/'source'),str(B/'source/sm_deps'),str(B)]
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
put('NATIVE93_ORIGINAL_METADATA_FIXTURE_CONSTRUCTION_ERROR_ACTUAL.json',dict(error='KeyError: native_iteration',cause='V1 fixture passed formal producer descriptor (updates) to saved native publication verifier (native_iteration). Actual saved publication/source validator unchanged.',before_any_model_GPU_or_SDK=True,old_inline_tool_failure_retained=True))
try:
 import native91_prior_migration_validation_v1 as prior
 import native91_terminal93_pins_v1 as pins
 import native88C_to_flat_migration_v1 as current
 pub=dict(pins.SOURCE_PINS['final']);assert 'native_iteration' not in pub and pub['updates']==9256
 pub['native_iteration']=pub['updates']
 full=dict(UniSuperMimic_changed_plant_migration=pub['native88_migration_window'],UniSuperMimic_test_contract=pins.SOURCE_PINS['native_contract'],spring_pressure_recipe=dict(nominal_stiffness_N_m=2000,actual_stiffness_bounds_N_m=[1800,2200]))
 prior.verify_saved_migration(full,pub)
 assert current.SOURCES['h1']['updates']==9256 and current.SOURCES['h1']['world_updates']==92560 and current.SOURCES['h1']['policy_updates']==9000
 put('NATIVE93_PRIOR91_METADATA_LINEAGE_SOURCE_FIXTURE_V2_ACTUAL.json',dict(passed=True,explicit_metadata_fixture_not_fresh_SDK_or_model_validation=True,descriptor_to_publication_fixture_mapping='native_iteration=qualified descriptor updates',source91_saved_metadata_admitted=True,new93_progress=current.SOURCES['h1'],no_model_load_forward_hash_physics_GPU_or_remote=True))
 print(json.dumps(dict(passed=True,metadata_fixture_only=True)))
except BaseException:
 put('NATIVE93_METADATA_FIXTURE_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc()));raise
