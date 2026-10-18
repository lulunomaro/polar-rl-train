from pathlib import Path,PurePosixPath
import json,time,hashlib,ast,shutil
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 history=B/'failed_first_target_portable_path_reader_source';history.mkdir();p=B/'closed_production_continuation_CPU_v2.py';shutil.copy2(p,history/p.name)
 t=p.read_text('utf8');old="Path(x['path']).name:x['SHA']";new="x['path'].replace(chr(92),'/').rsplit('/',1)[-1]:x['SHA']";assert t.count(old)==1;t=t.replace(old,new);ast.parse(t);p.write_text(t,'utf8');shutil.copy2(p,B/'controllers'/p.name)
 v=json.loads((R/'THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes())
 for key,folder in v['payloads'].items():
  dest=Path(folder);mf=dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';shutil.copy2(mf,history/(key+'_THREE_SLOT_COMPLETE_MANIFEST_BEFORE.json'));shutil.copy2(p,dest/p.name);m=json.loads(mf.read_bytes());row=next(r for r in m['files'] if r['relative']==p.name);row.update(bytes=p.stat().st_size,SHA=H(p));mf.write_text(json.dumps(m,indent=2),'utf8');v['specs'][key]['manifest_SHA']=H(mf)
 assert PurePosixPath(r'C:\Users\lulu\reward.py').name!= 'reward.py'
 report=json.loads((R/'SCUT_FUDAN_CLEAN_AIR_REWARD_FINAL_CPU_V7_ACTUAL.json').read_bytes());mapped={x['path'].replace(chr(92),'/').rsplit('/',1)[-1]:x['SHA'] for x in report['overlay']}
 for key in ('h1_scut_fudan_jump_reward_v1.py','h1_takeoff_progress_environment_v2.py','train_H1_ground_prelaunch_fullstate_v2.py'):assert mapped[key]==H(B/'reward_runtime_overlay'/key)
 v.update(epoch=time.time(),only_unused_controller_portable_CPU_report_path_parser_fixed=True,prior_preparer_report=str(R/'THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json'),reward_source_physics_and_model_unchanged=True)
 with (R/'THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_PORTABLE_PATH_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 with (R/'PORTABLE_WINDOWS_REPORT_PATH_ON_LINUX_CPU_FIX_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,foreign_Windows_path_basename_under_Linux_explicitly_tested=True,exact_reward_overlay_SHA_matches=True,no_GPU_or_model_or_reward_change=True,failed_loader_source_retained=str(history)),f,indent=2)
 print('Portable Windows-report basename fix CPU passed; prepared new manifests, no remote action.')
if __name__=='__main__':main()
