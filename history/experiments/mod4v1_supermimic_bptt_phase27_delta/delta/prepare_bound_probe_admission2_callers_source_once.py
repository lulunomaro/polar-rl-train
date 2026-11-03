"""New source purposes after actual original 1800s zero-GO timeout.
Source stage may be prepared ahead; parent Popen additionally requires an actual
post-closure release witness. No source/parent/budget protocol is weakened.
"""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent;out=R/'reports/BOUND_ONLY_ADMISSION2_PARENT_CALLER_SOURCE_V1.json';assert not out.exists()
prior_gate="""
def prior_zero_admission():
 p=json.loads((R/'BOUND_ONLY_E3_W35_V1_LATEST_CLOSED_RESULT_PATH.json').read_bytes());raw=Path(p['path']).read_bytes();v=json.loads(raw);t=v['top'];end=t['PARENT_EXIT_SCOPE.json'];assert v['closed']and v['actual_external_parent_wait_bound']and not v['early_controller_dead_without_wait_proof'];assert t['ACTUAL_GROUP_ADMISSION.json']is None and t['CHILDREN.json']is None and t['GROUP_EVAL_START.json']is None and t['FINAL.json']is None;assert end['all_own_children_waited']and end['child_waits']==[]and end['original_single_GPU_private_EX_released']and end['original_global_finite_EX_released']and end['canonical_writes']==0;assert 'Originalresourcewait1800sexpired'in str(t['PARENT_ORIGINAL_ERROR.json']);assert all(x['status']=='NOT_ADMITTED'and x['FINAL']is None and x['WORKER_SCENE_READY']is None for x in v['rows']);w=t['BOUND_PROBE_PARENT_WAITED_ACTUAL_V1.json'];assert w['actual_parent_p_wait_returned']and w['returncode']==1 and not w['controller_errors'];return v,end,hashlib.sha256(raw).hexdigest()
prior,prior_end,prior_closed_SHA=prior_zero_admission()
"""
release_gate="""release=json.loads((R/'reports/BOUND_PROBE_V1_RESOURCES_RELEASED_AFTER_ZERO_GO_TIMEOUT_V1.json').read_bytes());assert release['observer_only']and release['resource_release_observed']and release['actual']['original_frozen_resources_observed_clear']and release['actual']['original_relevant_leases_clear']and release['actual']['epoch']>=prior_end['epoch']and release['old_root']==prior['root']and release['old_closed_metadata_SHA']==prior_closed_SHA
"""
items=[('upload_preflight_bound_only_e3_w35_v1_once.py','upload_preflight_bound_only_e3_w35_admission2_once.py'),('stage_bound_only_e3_w35_after_preflight_once.py','stage_bound_only_e3_w35_admission2_after_preflight_once.py'),('dispatch_bound_only_e3_w35_original_parent_once.py','dispatch_bound_only_e3_w35_admission2_original_parent_once.py'),('collect_bound_only_e3_w35_metadata_once.py','collect_bound_only_e3_w35_admission2_metadata_once.py'),('grade_bound_only_closed_w35_original_rows_once.py','grade_bound_only_admission2_closed_w35_original_rows_once.py')]
rows=[]
for old,new in items:
 dest=R/new;assert not dest.exists();text=(R/old).read_text(encoding='utf-8').replace('BOUND_ONLY_E3_W35_V1','BOUND_ONLY_E3_W35_V1_ADMISSION2').replace('MOD4V1_BOUND_ONLY_E3_W35_PROBE_V1_','MOD4V1_BOUND_ONLY_E3_W35_PROBE_V1_ADMISSION2_')
 if old.startswith(('upload_','dispatch_')):
  # Insert local evidence gates before the first marker/out guard or connector.
  anchor="R=Path(__file__).resolve().parent;";assert text.count(anchor)==1;text=text.replace(anchor,anchor+'\n'+prior_gate+(release_gate if old.startswith('dispatch_')else'')+'\n',1)
 if old.startswith('grade_'):text=text.replace("purpose='bound_only_zero_update_v1'","purpose='bound_only_zero_update_admission2_v1'").replace('W35_ORIGINAL_SPLIT_GRADE_BOUND_ONLY_ZERO_UPDATE_V1.json','W35_ORIGINAL_SPLIT_GRADE_BOUND_ONLY_ZERO_UPDATE_ADMISSION2_V1.json')
 ast.parse(text);dest.write_text(text,encoding='utf-8',newline='\n');raw=dest.read_bytes();rows.append(dict(path=str(dest),source_template=old,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
v=dict(kind='NEW_BOUND_ONLY_ADMISSION2_CALLERS_AFTER_ACTUAL_ZERO_GO_CLOSURE',files=rows,static_original_17_source_PINs_and_CLI_unchanged=True,original_parent_controller_resources_deadlines_preserved=True,SDK_model_raw_C_lock_signal_parent_operations=0,parent_Popen_requires_positive_release_after_prior_closure=True)
out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
