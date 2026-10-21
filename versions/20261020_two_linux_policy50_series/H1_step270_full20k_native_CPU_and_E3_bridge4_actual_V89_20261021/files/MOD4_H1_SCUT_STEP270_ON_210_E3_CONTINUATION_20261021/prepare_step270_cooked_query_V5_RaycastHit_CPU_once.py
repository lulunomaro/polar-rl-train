from pathlib import Path
from types import SimpleNamespace
import ast, hashlib, json, time, traceback

B=Path(__file__).resolve().parent;R=B/'reports';H=lambda x:hashlib.sha256(x).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

previous=json.loads((R/'STEP270_COOKED_QUERY_V4_SOURCE_AST_PREPARED_ACTUAL.json').read_bytes())
returned=json.loads((R/'STEP270_COOKED_QUERY_V4_FINITE_RETURNED_ACTUAL.json').read_bytes())
assert not returned['pending'] and returned['parent_exit']['all_own_children_waited'] and returned['parent_exit']['own_eval_lease_released']
log=(B/'cooked_query_V4_actual/WORKER_FULL.log').read_text(encoding='utf8')
assert "RaycastHit' object has no attribute 'items'" in log
old=(B/'step270_cooked_PhysX_query_audit_worker_v4_JSON_diagnostic.py').read_text(encoding='utf8')
start=old.index('  def cast(origin,direction,distance):\n');end=old.index('  for i,point in enumerate(',start)
replacement='''  def cast(origin,direction,distance):
   hits=[];raw_hits=[];callback_errors=[]
   def callback(hit):
    try:
     row=dict(collision=str(hit.collision),rigidBody=str(hit.rigid_body),position=[float(x) for x in hit.position],normal=[float(x) for x in hit.normal],distance=float(hit.distance),faceIndex=int(hit.face_index),material=str(hit.material),actual_callback_type=str(type(hit)))
     raw_hits.append(row)
     if row['collision'].startswith('/World/ground/'):hits.append(row)
     return True
    except BaseException:
     callback_errors.append(traceback.format_exc());return False
   returned=query.raycast_all(tuple(float(x) for x in origin),tuple(float(x) for x in direction),float(distance),callback)
   if callback_errors:
    put('ORIGINAL_CALLBACK_READER_ERROR.json',dict(epoch=time.time(),errors=callback_errors,raw_hits=raw_hits));raise RuntimeError('Actual RaycastHit callback failed; no swallowed exception or admission')
   if not hits:
    put('ORIGINAL_MISSING_QUERY_RAW_DIAGNOSTIC.json',dict(epoch=time.time(),origin=[float(x) for x in origin],direction=[float(x) for x in direction],distance=float(distance),raycast_all_return=str(returned),all_unfiltered_hits=raw_hits));raise RuntimeError('Cooked terrain filter missing; no fallback or admission')
   return min(hits,key=lambda x:x['distance'])
'''
new=(old[:start]+replacement+old[end:]).replace('H1_step270_cooked_PhysX_queries_v4_diagnostic','H1_step270_cooked_PhysX_queries_v5_struct')
ast.parse(new)
assert ast.dump(ast.parse(new.replace(replacement,old[start:end]).replace('H1_step270_cooked_PhysX_queries_v5_struct','H1_step270_cooked_PhysX_queries_v4_diagnostic')))==ast.dump(ast.parse(old))
cast_source='\n'.join(line[2:] for line in replacement.splitlines())
records=[]
class Query:
    def __init__(self,hits):self.hits=hits
    def raycast_all(self,o,d,n,cb):
        for h in self.hits:
            if not cb(h):break
        return bool(self.hits)
def hit(path,d):return SimpleNamespace(collision=path,rigid_body=path,position=(0,0,0),normal=(0,0,1),distance=d,face_index=4,material='/World/ground/physicsMaterial')
scope=dict(time=time,traceback=traceback,put=lambda n,v:records.append((n,v)),query=Query([hit('/World/envs/env_0/Robot',.1),hit('/World/ground/part0000',1.5),hit('/World/ground/part0001',1.2)]))
exec(compile(cast_source,'actual_new_cast_CPU','exec'),scope)
chosen=scope['cast']((0,0,1.5),(0,0,-1),4)
assert chosen['collision']=='/World/ground/part0001' and chosen['faceIndex']==4
scope['query']=Query([{'collision':'/World/ground/part0000'}])
try:scope['cast']((0,0,1.5),(0,0,-1),4);raise AssertionError('Malformed callback was admitted')
except RuntimeError as e:assert 'callback failed' in str(e)
assert records[-1][0]=='ORIGINAL_CALLBACK_READER_ERROR.json'
scope['query']=Query([hit('/World/envs/env_0/Robot',.1)])
try:scope['cast']((0,0,1.5),(0,0,-1),4);raise AssertionError('Non-ground collider was admitted')
except RuntimeError as e:assert 'filter missing' in str(e)
worker=B/'step270_cooked_PhysX_query_audit_worker_v5_RaycastHit.py'
with worker.open('x',encoding='utf8',newline='\n') as f:f.write(new)
payload=B/'H1_step270_cooked_query_V5_struct_delta';payload.mkdir();(payload/'worker.py').write_bytes(worker.read_bytes())
cfg=json.loads((Path(previous['payload'])/'FROZEN_CONFIG.json').read_bytes());cfg['kind']='H1_step270_cooked_PhysX_queries_v5_struct';put(payload/'FROZEN_CONFIG.json',cfg)
manifest=json.loads((Path(previous['payload'])/'SOURCE_MANIFEST.json').read_bytes())
for row in manifest['files']:
    if row['relative'] in ('worker.py','FROZEN_CONFIG.json'):
        data=(payload/row['relative']).read_bytes();row.update(bytes=len(data),SHA=H(data))
put(payload/'SOURCE_MANIFEST.json',manifest)
workflows=[]
for source,target in [('deploy_step270_cooked_query_V4_unused_root_once.py','deploy_step270_cooked_query_V5_unused_root_once.py'),('collect_step270_cooked_query_V4_bounded_once.py','collect_step270_cooked_query_V5_bounded_once.py')]:
    text=(B/source).read_text(encoding='utf8').replace('COOKED_QUERY_V4','COOKED_QUERY_V5').replace('cookedquery_2110v4','cookedquery_2110v5').replace('cooked_query_V4_actual','cooked_query_V5_actual');ast.parse(text);p=B/target
    with p.open('x',encoding='utf8',newline='\n') as f:f.write(text)
    workflows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes()),unused=True))
put(R/'STEP270_COOKED_QUERY_V5_SOURCE_AST_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed_source_AST_only=True,source_SHA=previous['source_SHA'],payload=str(payload),zip=previous['zip'],worker=dict(path=str(worker),bytes=worker.stat().st_size,SHA=H(worker.read_bytes())),workflows=workflows,actual_V4_callback_type_error_evidence=True,normalized_rest_AST_exact=True,CPU_cases=['actual callback function uses structured attributes and filters original ground prefix','nearest matching ground hit selected; nearer robot excluded','malformed callback recorded and rejected','non-ground only rejected'],all_CPU_cases_passed=True,query_threshold_1um_unchanged=True,no_physics_or_actor_or_optimizer_change=True,not_installed_or_executed=True,primary_sources=['https://docs.omniverse.nvidia.com/kit/docs/omni_physics/108.1/extensions/runtime/source/omni.physx/docs/dev_guide/scene_queries.html','https://docs.omniverse.nvidia.com/kit/docs/omni_physics/108.1/extensions/runtime/source/omni.physx/docs/api/python.html'],primary_source_paraphrase='Raycast-all callbacks receive a RaycastHit structure with collision, rigid_body and face_index properties; raycast-closest returns a dictionary.'))
print(json.dumps(dict(source_AST_prepared=True,callback_CPU_cases=4,not_GPU_or_remote_executed=True)))
