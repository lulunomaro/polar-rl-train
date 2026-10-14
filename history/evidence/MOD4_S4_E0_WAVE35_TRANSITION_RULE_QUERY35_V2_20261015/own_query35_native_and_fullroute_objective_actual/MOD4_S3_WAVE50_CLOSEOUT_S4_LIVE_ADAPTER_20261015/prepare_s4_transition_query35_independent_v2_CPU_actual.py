"""New scope reference fixes only independent procedural geometry source."""
from pathlib import Path
import sys,json,time,hashlib,shutil,zipfile,importlib.util,traceback
import numpy as np
A=Path(__file__).resolve().parent;W=A.parent;OLD=W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_20261015';N=W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 receipt=json.loads(sorted((OLD/'reports').glob('s4_rule_original35_transition_native120_v1_CURRENT_ACTUAL_*.json'))[-1].read_bytes())
 assert receipt['outputs']['ORIGINAL_ERROR.json'] and receipt['states']['PARENT_EXIT_RECEIPT.json']['exit_code']==1 and receipt['shared_OS_lock_free'] and all(not p['actual_alive'] for p in receipt['actual_PID_identities'])
 error=receipt['outputs']['ORIGINAL_ERROR.json']['error'];assert 'Actual world triangles differ from procedural float32 cell identity' in error
 assert receipt['outputs']['COMPLETE_ACTUAL.json'] is None
 assert not N.exists();Q=N/'payload';R=N/'reports';shutil.copytree(OLD/'payload_v2',Q);R.mkdir()
 helper=Q/'g4_worldmesh_query_contract.py';old=helper.read_text();assert old.count('from g4_cad_wave_geometry import make_mesh')==1
 new=old.replace('from g4_cad_wave_geometry import make_mesh','from g3_cad_wave_geometry import make_mesh');helper.write_text(new,encoding='utf8')
 assert new.replace('from g3_cad_wave_geometry import make_mesh','from g4_cad_wave_geometry import make_mesh')==old
 pair=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes())
 for row in pair['sources']:row['local_path']=row['local_path'].replace(OLD.name,N.name)
 pair['own_reference_now_original35']=True;(Q/'S4_PAIR_SOURCE_MANIFEST.json').write_text(json.dumps(pair,indent=2),encoding='utf8')
 p=Q/'paired_full80_parameter_bound_v2.py';s=p.read_text();assert s.count(OLD.name)==1;p.write_text(s.replace(OLD.name,N.name),encoding='utf8')
 sys.path[:0]=[str(Q/'runtime/isaac/mod4'),str(Q)]
 spec=importlib.util.spec_from_file_location('independent_query35_CPU_reference',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 oldspec=importlib.util.spec_from_file_location('retained_wrong_query50_reference',OLD/'payload_v2/g4_worldmesh_query_contract.py');wrong=importlib.util.module_from_spec(oldspec);oldspec.loader.exec_module(wrong)
 from g3_cad_wave_geometry import make_mesh,profile
 mesh,_=make_mesh((9.,9.));vertices=np.asarray(mesh.vertices).copy();vertices[:,:2]-=4.5;faces=np.asarray(mesh.faces)
 centers=np.stack(((np.arange(80)//2+.5)*9-180,(np.arange(80)%2+28+.5)*9-180),-1)
 vv=np.concatenate([(vertices+np.r_[c,0]).astype(np.float32) for c in centers]);ff=np.concatenate([faces+i*len(vertices) for i in range(80)])
 starts=np.repeat(np.concatenate((centers,np.ones((80,1))*2),-1)[:,None],35,axis=1)
 half=profile()['span_m']/2;starts[:,1:34,0]+=np.linspace(-half,half,33);starts[:,0,0]-=half+.4;starts[:,34,0]+=half+.4
 starts=starts.astype(np.float32)
 try:wrong.expected_ground(vv,ff,centers,starts)
 except AssertionError as ex:assert 'triangles differ' in str(ex)
 else:raise AssertionError('Old50 reference did not reject actual35 fixture')
 expected,rows,triangles=mod.expected_ground(vv,ff,centers,starts)
 assert expected.shape==(80,35) and triangles.shape[0]==80 and all(r['byteexact'] for r in rows)
 assert np.max(abs(expected[:,[0,34]]))==0 and 0.005<expected.max()<=.035001
 bad=vv.copy();bad[10,2]+=.001
 try:mod.expected_ground(bad,ff,centers,starts)
 except AssertionError:pass
 else:raise AssertionError('Modified actual vertex accepted')
 try:mod.expected_ground(vv,ff,centers+.001,starts)
 except AssertionError:pass
 else:raise AssertionError('Incorrect center accepted')
 m=json.loads((Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes());m.update(epoch=time.time(),source_pair=pair['sources'],original_failed_scope_preserved=str(OLD),S4_query_reference_declared_change='original procedural independent reference now35 instead of50; same triangle byte equality and1e-6 query tolerances')
 m['S4_transition_scope']['only_source_pair']=pair['sources']
 for row in m['file_rows']:row.update(bytes=(Q/row['relative']).stat().st_size,sha256=H(Q/row['relative']))
 (Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 for p in Q.rglob('*.py'):compile(p.read_text(encoding='utf8'),str(p),'exec')
 z=N/'S4_ORIGINAL35_QUERY_CORRECTED_SOURCE_V2.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
  for row in m['file_rows']:out.write(Q/row['relative'],row['relative'])
  out.write(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json','REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')
  for row in pair['sources']:out.write(Q/'source'/Path(row['local_path']).name,'source/'+Path(row['local_path']).name)
 proof=dict(epoch=time.time(),passed_CPU_reference_binding=True,original_native_failure_kept=True,original_boundary=receipt['states']['PARENT_EXIT_RECEIPT.json'],actual_all_parent_child_absent=True,shared_OSlock_free=True,old_expected50_rejects_actual35_fixture=True,new80cell35_reference_source_bound_triangles_exact=True,synthetic_query2800_rays=True,modified_vertex_and_incorrect_center_rejected=True,helper_AST_only_G3_source_import_changed=True,thresholds1e6_contactCOM_hardware_physical_loop_no_change=True,original_W35_geometry_source_bytes_unchanged=True,public_CPU_procedural_reference_not_GPU_native_pass=True,no_new_steps_RNG_PPO_or_ledger=True)
 (R/'QUERY35_REFERENCE_OLD_REJECTION_NEW_SOURCE_BINDING_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
 prep=json.loads((OLD/'reports/S4_ORIGINAL35_TRANSITION_RULE_SOURCE_CPU_PREPARED_ACTUAL_V2.json').read_bytes());prep.update(epoch=time.time(),new_root='D:/MOD4_async_eval/'+N.name,active_payload=str(Q),package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),manifest=dict(path=str(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),sha256=H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')),worker=dict(path=str(Q/'paired_full80_parameter_bound_v2.py'),sha256=H(Q/'paired_full80_parameter_bound_v2.py')),runtime=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=H(Q/'full80_runtime_native_v1.py')),source_pair=pair['sources'],independent_query_reference_CPU_proof_SHA=H(R/'QUERY35_REFERENCE_OLD_REJECTION_NEW_SOURCE_BINDING_CPU_ACTUAL.json'),old_scope_failed_not_relabelled=True)
 p=R/'S4_ORIGINAL35_TRANSITION_RULE_SOURCE_CPU_PREPARED_ACTUAL_V2.json';p.write_text(json.dumps(prep,indent=2),encoding='utf8');print(json.dumps(dict(prepared=str(p),CPU_reference_passed=True,package=prep['package'],no_GPU=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (A/'reports'/('QUERY35_CPU_REFERENCE_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU=True),indent=2),encoding='utf8');raise
