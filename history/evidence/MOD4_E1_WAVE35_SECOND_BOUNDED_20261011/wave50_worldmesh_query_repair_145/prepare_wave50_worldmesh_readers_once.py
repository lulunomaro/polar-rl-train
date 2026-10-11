"""Prepare independent read-only collectors for the new scope; never execute old ones."""
from second_io import *
import ast

old=(D/'collect_new_wave50_actual.py').read_text()
new=old.replace("sys.path.insert(0,str(W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011'))\nfrom slope8_worker_actual import worker_actual",'from wave50_worker_actual import worker_actual')
new=new.replace('WAVE50_FROZEN_PUBLISHED','WAVE50_WORLDMESH_FROZEN_PUBLISHED').replace('WAVE50_ACTUAL_COLLECTED','WAVE50_WORLDMESH_ACTUAL_COLLECTED').replace('WAVE50_COLLECTION_ERROR','WAVE50_WORLDMESH_COLLECTION_ERROR')
anchor="    assert p.stat().st_size==rawinfo['bytes'] and H(p.read_bytes())==rawinfo['sha256'];row['raw_SHA_exact']=True;cases[jid]=row"
assert new.count(anchor)==1
new=new.replace(anchor,"""    assert p.stat().st_size==rawinfo['bytes'] and H(p.read_bytes())==rawinfo['sha256'];row['raw_SHA_exact']=True
    queryinfo=row['probe']['route_scope']['query_worldmesh_evidence'];name=Path(queryinfo['path']).name;qp=folder/name
    if not qp.exists():
     part=qp.with_suffix(qp.suffix+'.partial');wf.get(WIN+'/jobs/'+jid+'/'+name,str(part));assert part.stat().st_size==queryinfo['bytes'] and H(part.read_bytes())==queryinfo['sha256'];part.rename(qp)
    assert qp.stat().st_size==queryinfo['bytes'] and H(qp.read_bytes())==queryinfo['sha256']
    try:qback=nf.open(io.E+'/eval_results/'+jid+'/'+name).read();assert qback==qp.read_bytes();row['query_two_host_byteSHA_exact']=True
    except FileNotFoundError:pending.append(dict(job_id=jid,phase='complete_query_NPZ_bridge_pending'));continue
    row['query_evidence_local']=str(qp);cases[jid]=row
    files.append(dict(path=str(qp.resolve()),source=queryinfo['path'],bytes=queryinfo['bytes'],sha256=queryinfo['sha256'],large_index_only=True,original_retained=True))""")
compile(new,'collect_wave50_worldmesh_actual.py','exec');p=D/'collect_wave50_worldmesh_actual.py';assert not p.exists();p.write_bytes(new.encode())
old=(D/'review_new_wave50_actual.py').read_text();new=old.replace('WAVE50_COMPONENT_FROZEN_PREPARED','WAVE50_WORLDMESH_QUERY_PREPARED').replace('WAVE50_ACTUAL_COLLECTED','WAVE50_WORLDMESH_ACTUAL_COLLECTED').replace('WAVE50_ACTUAL_REVIEW','WAVE50_WORLDMESH_ACTUAL_REVIEW').replace('WAVE50_REVIEW_ERROR','WAVE50_WORLDMESH_REVIEW_ERROR')
start="  profile=prepared['profile'];knots=";end="  a=audit(p,R/'cases'/jid);"
i=new.index(start);j=new.index(end,i)
new=new[:i]+"""  sys.path.insert(0,str(D/'wave50_worldmesh_scope'))
  from g4_worldmesh_query_contract import expected_ground
  qp=Path(row['query_evidence_local']);qi=s['query_worldmesh_evidence'];assert H(qp.read_bytes())==qi['sha256'] and qp.stat().st_size==qi['bytes'] and row['query_two_host_byteSHA_exact']
  with np.load(qp,allow_pickle=False) as q:
   assert np.array_equal(q['actual_world_ray_origins'],orig) and np.array_equal(q['actual_canonical_ray_x'],x) and np.array_equal(q['actual_sampled_ground'],np.asarray(s['actual_sampled_ground']))
   tri=q['world_triangles'];assert tri.ndim==4 and tri.shape[0]==80 and tri.shape[2:]==(3,3)
   vertices=tri.reshape(-1,3);faces=np.arange(len(vertices)).reshape(-1,3)
   expected,receipts,_=expected_ground(vertices,faces,np.asarray(s['tile_centers']),orig)
   assert np.array_equal(expected,q['expected_actual_ground']) and np.array_equal(expected,np.asarray(s['expected_actual_sampled_ground'])) and receipts==s['world_mesh_receipts']
   error=float(np.max(abs(expected-q['actual_sampled_ground'])));assert error<=1e-6 and s['actual_query_ground_tolerance_m']==1e-6 and error==s['actual_query_height_error_m']
   ideal_diff=float(np.max(abs(q['actual_sampled_ground']-q['ideal_profile_ground'])));assert ideal_diff==s['ideal_profile_difference_m']
"""+new[j:]
new=new.replace('actual_world_float32_query_identity_exact=True,','actual_world_float32_query_identity_exact=True,all_actual_world_triangles_procedural_byteexact=True,query_NPZ_two_host_byteSHA_exact=True,independent_CPU_ground_error_m=error,ideal_profile_difference_m=ideal_diff,')
compile(new,'review_wave50_worldmesh_actual.py','exec');p=D/'review_wave50_worldmesh_actual.py';assert not p.exists();p.write_bytes(new.encode())
save('WAVE50_WORLDMESH_READERS_PREPARED.json',dict(epoch=time.time(),collector=str(D/'collect_wave50_worldmesh_actual.py'),reviewer=str(p),prepared_only_not_actual_review=True,original_readers_source_retained=True,query_npz_and_actual_triangles_byteexact_required=True,ground_tolerance_m=1e-6,all_original_fullraw_hardware_and_contact_auditors_unchanged=True))
print(json.dumps(dict(readers_prepared=True,no_GPU_or_result_replay=True)))
