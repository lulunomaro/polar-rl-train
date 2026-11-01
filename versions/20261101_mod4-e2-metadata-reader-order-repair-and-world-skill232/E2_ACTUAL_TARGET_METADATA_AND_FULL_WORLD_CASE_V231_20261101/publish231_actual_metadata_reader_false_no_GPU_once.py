from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;R=N/'reports'
actual=json.loads((R/'ROOT231_ACTUAL_E2_METADATA_AND_ORIGINAL_MEAN_CASE_RETURNED.json').read_bytes());assert not actual['passed_execution']and actual['bounded_case']is None
waits=[json.loads(x['UTF8'])for x in actual['full_UTF8']if x['path'].endswith('/E2_FROM226_ORIGINAL_METADATA_CHILD_WAIT_ACTUAL.json')];assert len(waits)==1
w=waits[0];assert w['actual_waited']and w['all_own_children_waited']and w['returncode']==1 and w['model_reads']==w['GPU_or_App_calls']==0
report=dict(epoch=time.time(),kind='ACTUAL231_METADATA_READER_SAME_LINE_AST_FALSE_BEFORE_GPU',passed_execution=False,actual_original_metadata_wait=w,
 cause='Frozen226 probe requires actor.lineno<vec.step.lineno, but original213 has one actor at(117,32) and one step at(117,124) on same line;hook(132,2) precedes main(134,6). Source ordering check was too coarse.',
 actual_authority227D_fresh_matched=True,source_asset_install_postcopy_passed=True,physical_GPU_parent_entered=False,model_bytes_decodes=0,NN_or_GPU_or_physics_or_optimizer_or_account=0,
 known_E2_policy_skill='NOT_TESTED;notaphysicalpolicyfailure',W35_current_training='Original227D untouched;no startupGPUrecheck/extrahealthwatcher',all_owned_metadata_children_waited_OUT=True,SSH_finally_closed=True,
 original231_and226_purpose='CONSUMED neverrerun',next='SeparateV3 lexicalposition reader fix/new232namespace/purpose. Originalworker91f7,TaskABI,reward/physics/guards unchanged;all oldfalse retained.')
p=R/'CURRENT_ACTUAL231_METADATA_READER_FALSE_BEFORE_MODEL_AND_NEXT232_WORK_ORDER.json';assert not p.exists();p.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print({'saved':str(p),'physical_failure':False,'model_reads':0})
