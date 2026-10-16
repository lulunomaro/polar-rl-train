"""Collect missing complete models and read geometry/pose source after actual scope exit."""
from pathlib import Path
import json,time,hashlib,getpass,paramiko,importlib.util,shlex,traceback
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/h1_flat_fullphysics_calibration_v1_launcher_environment_v2';PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
s=importlib.util.spec_from_file_location('pure_transport_helpers',D/'deploy_H1_fullphysics_calibration_unused_scope_once.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert not (R/'H1_CLOSED_CALIBRATION_MODEL_USD_POSE_SOURCE_ACTUAL_COLLECTION.json').exists();c0=json.loads((R/'H1_FULLPHYSICS_CALIBRATION_V2_ACTUAL_BOUND_COLLECTION.json').read_bytes());assert not c0['actual_processes'] and c0['parent_exit'] and not c0['errors']
 pw=getpass.getpass('Host72 closed H1 model and source read-only password (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());sf=None
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  v=m.code(c,r'''
from pathlib import Path
import sys,json,time,hashlib,ast,psutil
from pxr import Usd,UsdPhysics
B=Path(sys.argv[1]);assert json.loads((B/'PARENT_FINAL.json').read_bytes())['passed'];assert json.loads((B/'PARENT_EXIT_ACTUAL.json').read_bytes())['own_child_actual_out']
for name in ('PARENT_IDENTITY.json','WORKER_STARTED_ACTUAL.json'):
 v=json.loads((B/name).read_bytes())
 if psutil.pid_exists(v['pid']):
  p=psutil.Process(v['pid']);assert abs(p.create_time()-v['creation'])>.01 or p.cmdline()!=v['argv']
def row(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())
usd=B/'job1/assets/robot.usd';stage=Usd.Stage.Open(str(usd));shapes=[]
for p in stage.Traverse():
 if p.HasAPI(UsdPhysics.CollisionAPI):
  enabled=UsdPhysics.CollisionAPI(p).GetCollisionEnabledAttr().Get();approx=UsdPhysics.MeshCollisionAPI(p).GetApproximationAttr().Get() if p.HasAPI(UsdPhysics.MeshCollisionAPI) else None;shapes.append(dict(path=str(p.GetPath()),type=p.GetTypeName(),collision_enabled=enabled,approximation=approx))
sdk=Path('/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/assets/articulation/articulation_data.py');text=sdk.read_text();tree=ast.parse(text);methods={n.name:ast.get_source_segment(text,n) for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in ('body_pos_w','body_quat_w','body_link_pos_w','body_link_quat_w','body_link_state_w')}
print(json.dumps(dict(epoch=time.time(),actual_parent_child_out=True,models=[row(B/'output/source_model_fresh80_before.pt'),row(B/'output/source_model_fresh80_after.pt')],source_USD=row(usd),source_USD_enabled_collision_shapes=shapes,actual_loaded_tree_source_pose_aliases=methods,sdk_source=row(sdk),USD_source_not_live_cooked_shape_readback=True,no_AppLauncher_physics_GPU_optimizer_or_canonical_mutation=True)))
''',ROOT)
  outdir=D/'H1_closed_calibration_models';outdir.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(90);rows=[]
  for r in v['models']:
   out=outdir/Path(r['path']).name;part=out.with_suffix('.pt.partial');sf.get(r['path'],str(part));assert part.stat().st_size==r['bytes'] and hashlib.sha256(part.read_bytes()).hexdigest()==r['SHA'];part.replace(out);rows.append(dict(path=str(out.resolve()),bytes=out.stat().st_size,SHA=r['SHA'],remote=r['path'],twohost_bytes_SHA_exact=True))
  v['local_models']=rows;put('H1_CLOSED_CALIBRATION_MODEL_USD_POSE_SOURCE_ACTUAL_COLLECTION.json',v);print(json.dumps(dict(models=rows,authored_shapes=len(v['source_USD_enabled_collision_shapes']),enabled_shapes=sum(x['collision_enabled'] is True for x in v['source_USD_enabled_collision_shapes']),pose_alias_names=list(v['actual_loaded_tree_source_pose_aliases']),no_new_GPU=True)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_CLOSED_MODEL_GEOMETRY_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_replay=True));raise
