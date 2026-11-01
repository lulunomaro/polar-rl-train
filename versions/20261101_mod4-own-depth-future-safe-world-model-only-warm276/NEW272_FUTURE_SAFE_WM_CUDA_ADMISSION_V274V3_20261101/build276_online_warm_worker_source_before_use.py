"""Independent live WM warm source from actual272; no model/raw/SDK access."""
from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent.parent;N=T/'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276_20261101';N.mkdir(exist_ok=False);S=N/'source';S.mkdir()
B=T/'FUDAN_TERRAIN80_CURRENT_DEPTH_PACKET_V272_20261101/source'
original=(B/'evaluate272_front_depth_zero_PT_UNUSED_once.py').read_text('utf8')
prefix=original[:original.index(' arrays={};dynamic_memory=')]
prefix=prefix.replace('"""OwnMOD4 forward Z-depth sensor admission,12controls; no policy/checkpoint."""','"""Live ownMOD4 WM-only warm: frozen2135 teacher, one fresh WM Adam, original finite owner."""')
prefix=prefix.replace('import argparse,hashlib,io,json,os,runpy,sys,time,traceback','import argparse,hashlib,io,json,os,runpy,shutil,sys,time,traceback')
prefix=prefix.replace("sys.path.insert(0,str(Path(__file__).resolve().parent))","sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parent/'code'),str(Path(__file__).resolve().parent/'kernel')]")
prefix=prefix.replace('from contract272 import validate_task','from wm_task275 import validate_task,validate_go')
prefix=prefix.replace("assert TASK['actual_parent_private_EX_and_authority_admitted']and os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']","go=json.loads((P/'GO_PRODUCTION.json').read_bytes());validate_go(go,go['run_id'],TASK,time.time());assert os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']\nTASK=dict(TASK,run_id=go['run_id'],generation='OWN_LIVE_WM_WARM276_FRESH_EPISODES',actual_resource_admission_SHA=hashlib.sha256((P/'control276/ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json').read_bytes()).hexdigest())")
prefix=prefix.replace("OUT=P/'actual_capture'","OUT=P/'production'")
prefix=prefix.replace(" with(OUT/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)"," q=OUT/(n+'.partial');q.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf8');os.replace(q,OUT/n)")
prefix=prefix.replace("deadline=time.time()+TASK['worker_seconds']","deadline=go['save_deadline']")
prefix=prefix.replace("RM_RESCUE_STOP_FILE=str(OUT/'UNREQUESTED_STOP.json')","RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json')")
prefix=prefix.replace(" del ck\n body_names="," # Complete original actor/Critic/STD/17Adam remains frozen in ck; no old DR restored into fresh physical episodes.\n body_names=")
prefix=prefix.replace(" before=dict(base_air_time=real.literal.base_air_time.clone(),last_contacts=real.literal.last_contacts.clone(),last_actions=frame['last_actions'].clone())\n",'')
for p in B.glob('*.py'):
 if p.name not in ('evaluate272_front_depth_zero_PT_UNUSED_once.py','target272_single_N1_parent_UNUSED.py','contract272.py'):(S/p.name).write_bytes(p.read_bytes())
(N/'worker276_prefix_from_actual272.txt').write_text(prefix,encoding='utf8')
with(N/'SOURCE276_BUILD_PROVENANCE.json').open('x',encoding='utf8')as f:
 json.dump(dict(epoch=time.time(),source=str(B/'evaluate272_front_depth_zero_PT_UNUSED_once.py'),source_SHA=hashlib.sha256(original.encode()).hexdigest(),only_LOCAL_source_preparation=True,model_raw_SDK_GPU_remote_GO=0,original_camera_plant_state_and_terrain_functions_reused=True,old272_entry_not_replayed=True),f,indent=2)
print(json.dumps(dict(passed=True,path=str(N),prefix_lines=len(prefix.splitlines()))))
