"""Retain v27 pre-GPU rejection; prepare a fresh root and distinct clock-native output namespace."""
from pathlib import Path
import ast,hashlib,json,shutil,time
B=Path(__file__).resolve().parent;R=B/'reports';OLD=B/'controller50';C=B/'controller50V3';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 actual=json.loads((R/'POLICY50_FIRST_METADATA_FINITE_RETURNED_ACTUAL.json').read_bytes())['actual'];assert actual['series_error'] and actual['GO'] is None and not actual['actual_own_processes'] and actual['series_exit']['status']=='original_error_no_automatic_retry'
 manifest=json.loads((B/'remote_snapshot_policy50/windows/hour0001/recovery/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());historical=next(x for x in manifest['files'] if x['relative']=='job0/native/NATIVE336_COMPLETE.json');assert 'common.spawn' in actual['series_error']['error']
 assert not C.exists();shutil.copytree(OLD,C)
 worker=C/'overlay/recovery_worker.py';s=worker.read_text('utf8');assert 'OUT=J/a.phase' in s;s=s.replace('OUT=J/a.phase',"OUT=J/('clock_native50' if native else a.phase)");worker.write_text(s,encoding='utf8')
 common=C/'three_slot_common_v1.py';s=common.read_text('utf8');s=s.replace("return J/('production' if phase=='production' else 'native')","return J/('production' if phase=='production' else 'clock_native50')");common.write_text(s,encoding='utf8')
 parent=C/'auto_E3_serial_supervisor_v1.py';s=parent.read_text('utf8').replace('MOD4_E3_AUTO50_PENDING_SERIES_20261020.json','MOD4_E3_AUTO50_V3_PENDING_SERIES_20261020.json').replace('job0/native/','job0/clock_native50/').replace("node/'job0/native'","node/'job0/clock_native50'");parent.write_text(s,encoding='utf8')
 native=C/'policy50_native_CPU_v1.py';s=native.read_text('utf8').replace("native=B/'job0/native'","native=B/'job0/clock_native50'")
 before="report=dict(epoch=time.time()"
 extra="healths=list((native/'logs').rglob('CLOCK_TRAINING_HEALTH.json'));assert len(healths)==1;health=read(healths[0]);assert health['integrity_task_reset_events']==health['unknown_task_reset_events']==0 and health['nonfinite_observed'] is False and health['max_mimic_error_rad']<=.01 and health['termination_reason_coverage_exact'] and health['actual_physics_callbacks']==health['expected_physics_callbacks']==192 and not health['stop_reason']\nreport=dict(epoch=time.time()"
 assert before in s;s=s.replace(before,extra);native.write_text(s,encoding='utf8')
 config=json.loads((C/'POLICY50_OVERLAY_CONFIG.json').read_bytes())
 for row in config['changes']:row.update(candidate_SHA=H(C/'overlay'/row['relative']),candidate_bytes=(C/'overlay'/row['relative']).stat().st_size)
 (C/'POLICY50_OVERLAY_CONFIG.json').write_text(json.dumps(config,indent=2),encoding='utf8')
 text=(B/'deploy_policy50_after_saved_series_boundary_once.py').read_text('utf8').replace("C=B/'controller50'","C=B/'controller50V3'").replace('E3auto50_2010v27/controller','E3auto50_2010v28/controller').replace('MOD4_E3_AUTO50_PENDING_SERIES_20261020.json','MOD4_E3_AUTO50_V3_PENDING_SERIES_20261020.json')
 text=text.replace('POLICY50_SERIAL_V2_SOURCE_PREPARED_CPU_ACTUAL.json','POLICY50_V3_SOURCE_PREPARED_CPU_ACTUAL.json')
 for name in ['DEPLOY_STARTED_ACTUAL','ORIGINAL_SERIES_CLOSED_RESOURCE_HANDOFF_ACTUAL','REMOTE_CONTROLLER_OVERLAY_EXACT_SHA_ACTUAL','SERIAL_PARENT_DEPLOYED_ACTUAL','DEPLOY_FINITE_RETURNED_ACTUAL','DEPLOY_ORIGINAL_ERROR_']:
  text=text.replace('POLICY50_'+name,'POLICY50_V3_'+name)
 marker="assert (old/'STOP_SERIES_AFTER_CURRENT.json').is_file()"
 pre="failed=owned/'tasks/E3auto50_2010v27/controller';fex=read(failed/'SERIES_EXIT_ACTUAL.json');assert fex['status']=='original_error_no_automatic_retry' and read(failed/'SERIES_CURRENT.json')['active'] is None and not (failed.parent/'windows/hour0001/recovery/job0/GO_PRODUCTION.json').exists();assert not any(p.pid!=os.getpid() and any(a.startswith(str(failed.parent)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))\nwith (owned/'state/MOD4_E3_AUTO50_PENDING_SERIES_20261020.json').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\n"+marker
 assert marker in text;text=text.replace(marker,pre);(B/'deploy_policy50_namespace_fixed_V3_once.py').write_text(text,encoding='utf8')
 reader=(B/'collect_policy50_first_actual_learning_finite_once.py').read_text('utf8').replace('POLICY50_','POLICY50_V3_').replace("B/'remote_snapshot_policy50'","B/'remote_snapshot_policy50_V3'").replace("node/'job0/native'","node/'job0/clock_native50'")
 (B/'collect_policy50_V3_first_actual_learning_finite_once.py').write_text(reader,encoding='utf8')
 reviewer=(B/'review_policy50_first_actual_learning_CPU_once.py').read_text('utf8').replace('POLICY50_','POLICY50_V3_').replace("/job0/native/logs/","/job0/clock_native50/logs/")
 # Only report names receive V3; actual producer clock/SOURCE/SDK filenames are unchanged.
 reviewer=reviewer.replace("production/POLICY50_V3_ACTUAL_CLOCK", "production/POLICY50_ACTUAL_CLOCK")
 (B/'review_policy50_V3_first_actual_learning_CPU_once.py').write_text(reviewer,encoding='utf8')
 assert all(ast.parse(p.read_text('utf8')) for p in C.rglob('*.py'));e={'J':Path('fixture/job0')};s=common.read_text('utf8');fn=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='outdir');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual namespace guard>','exec'),e);assert e['outdir']('native')==Path('fixture/job0/clock_native50') and e['outdir']('production')==Path('fixture/job0/production')
 # Historical receipt is retained by the factory; no delete or overwrite is used.
 report=dict(epoch=time.time(),passed_source_CPU=True,controller_files={p.name:H(p) for p in C.iterdir() if p.is_file()},original_preGO_rejection_preserved=True,historical_native_receipt=historical,new_clock_native_namespace='clock_native50',old_failed_v27_no_GO_no_PPO_no_GPU_child=True,new_unused_remote_root='/home/lc01/Zonglin Li/zonglin2/tasks/E3auto50_2010v28/controller',native_clock_and_original_health_qualified_before_GO=True,no_runtime_physics_reward_or_optimizer_change_from_reviewed_policy50_V2=True,not_GPU_admitted_yet=True)
 put('POLICY50_V3_SOURCE_PREPARED_CPU_ACTUAL.json',report);print(json.dumps(dict(prepared=True,preGO_namespace_bug_fixed=True,old_roots_retained=True,new_root='E3auto50_2010v28')))
if __name__=='__main__':main()
