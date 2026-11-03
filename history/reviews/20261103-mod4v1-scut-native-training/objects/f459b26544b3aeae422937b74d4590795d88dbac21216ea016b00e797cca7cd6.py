"""Apply the human's light GPU occupancy permission to the unused diagnostic."""
from pathlib import Path
import ast,hashlib,json,time

N=Path(__file__).resolve().parent;D=N/'env20000_1h/action_clip_eval1'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2)
assert not(D/'reports/LAUNCH_ONCE.json').exists()
old=read(D/'SOURCE_FROZEN_REV2.json');plan=read(D/'PLAN_REV2.json')
resource='''import psutil,shutil
 line=subprocess.check_output(['nvidia-smi','-i',plan['GPU_UUID'],'--query-gpu=uuid,name,memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
 fields=[x.strip()for x in line.split(',')]
 apps=subprocess.check_output(['nvidia-smi','-i',plan['GPU_UUID'],'--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True).strip()
 free,used,util=int(fields[2]),int(fields[3]),int(fields[4])
 admitted=(fields[0]==plan['GPU_UUID']and fields[1]=='NVIDIA GeForce RTX 4090'and free>15669 and (not apps or (used<=4096 and util<=30)))
 ram=psutil.virtual_memory().available;disk=shutil.disk_usage(r).free
 admitted=admitted and ram>64*1024**3 and disk>50*1024**3
 o.put(r/'GPU_ADMISSION.json',dict(epoch=time.time(),line=line,selected_gpu_compute_apps=apps,admitted=bool(admitted),light_occupancy_allowed=True,ram=ram,disk=disk,all_original_locks_held=True))
 if not admitted:raise BlockingIOError('Insufficient measured capacity for the authorized shared diagnostic')'''
source=(D/'owner_eval.py').read_text(encoding='utf8')
assert source.count("o.resource(plan['GPU_UUID'])")==1
source=source.replace("o.resource(plan['GPU_UUID'])",resource)
ast.parse(source)
owner=D/'owner_eval_shared.py'
with owner.open('x',encoding='utf8')as f:f.write(source)
plan.update(source_revision=3,human_gpu_permission='如果卡上有有占用但占用不大可以直接用',
    resource_policy=dict(selected_gpu_only=True,allow_light_occupancy=True,min_free_mib_exclusive=15669,
        occupied_max_used_mib=4096,occupied_max_utilization_percent=30,
        original_canonical_and_private_and_finite_locks_unchanged=True),
    previous_plan=dict(path=str(D/'PLAN_REV2.json'),SHA=H((D/'PLAN_REV2.json').read_bytes())))
put(D/'PLAN_REV3.json',plan)
rows=[row for row in old['files']if row['relative']not in ('owner_eval.py','PLAN.json')]
for path,relative in ((owner,'owner_eval.py'),(D/'PLAN_REV3.json','PLAN.json')):
    raw=path.read_bytes();rows.append(dict(path=str(path),relative=relative,bytes=len(raw),SHA=H(raw)))
put(D/'SOURCE_FROZEN_REV3.json',dict(files=rows,shared_package=old['shared_package'],
    prior_overlay=old['prior_overlay'],previous_index_SHA=H((D/'SOURCE_FROZEN_REV2.json').read_bytes()),
    actual_run=False,full_tree_copy=False,new_model_copy=False))
print(json.dumps(dict(revision=3,source_files=len(rows),native_pending=True,light_GPU_occupancy_allowed=True)))
