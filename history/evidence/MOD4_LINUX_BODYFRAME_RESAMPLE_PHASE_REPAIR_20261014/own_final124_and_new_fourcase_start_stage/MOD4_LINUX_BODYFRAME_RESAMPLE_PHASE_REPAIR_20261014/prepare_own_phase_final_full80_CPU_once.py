"""Prepare a fresh frozen evaluation only after the own complete CPU closeout."""
from pathlib import Path
import ast, hashlib, json, shutil, time, zipfile, traceback
D=Path(__file__).resolve().parent;W=D.parent
OLD=W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'
NEW=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_FULL80_20261015'
SHA='cfcefb1c46b33d6028bf6663921fac12a58a5abfdba782e1480a18ac84de541b'
PREVIOUS='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139'
CASE='native3060_bodyframe_phase_final_full80_frozen1500_v1'
TASK='MOD4_BodyframePhaseFinalFull80_20261015_Frozen1500_v1'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
 assert not p.exists(),str(p)
 compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
def main():
 proof=D/'reports/PHASE_REPAIR_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json'
 final=json.loads(proof.read_bytes());assert final['passed'] and final['actual_parent_guardian_child_out'] and final['two_locks_free']
 assert final['own_checkpoint']['sha256']==SHA and final['updates']==124 and final['controls']==2976
 source=Path(final['own_checkpoint']['path']);assert h(source)==SHA and source.stat().st_size==19894311
 assert not NEW.exists();Q=NEW/'payload';R=NEW/'reports';Q.mkdir(parents=True);R.mkdir()
 m=json.loads((OLD/'payload/REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes())
 for row in m['file_rows']:
  p=OLD/'payload'/row['relative'];assert p.stat().st_size==row['bytes'] and h(p)==row['sha256']
  target=Q/row['relative'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 worker=Q/'paired_full80_parameter_bound_v2.py';before=worker.read_text(encoding='utf8')
 after=before.replace(PREVIOUS,SHA).replace(OLD.name,NEW.name)
 assert ast.dump(ast.parse(after.replace(SHA,PREVIOUS).replace(NEW.name,OLD.name)),include_attributes=False)==ast.dump(ast.parse(before),include_attributes=False)
 worker.write_text(after,encoding='utf8')
 shutil.copy2(source,Q/'source/model_32635_left_repair.pt')
 changed=[]
 for row in m['file_rows']:
  p=Q/row['relative'];newh=h(p)
  if newh!=row['sha256']:changed.append(row['relative'])
  row.update(bytes=p.stat().st_size,sha256=newh)
 assert set(changed)=={'paired_full80_parameter_bound_v2.py','source/model_32635_left_repair.pt'}
 m.update(epoch=time.time(),source_SHA=SHA,actual_own_model32830=False,actual_own_model32998=True,actual_own_final_CPU_closeout_SHA=h(proof),original_physics_source_reused_except_source_namespace_literals=['paired_full80_parameter_bound_v2.py'])
 (Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 z=NEW/'FULL80_FROZEN1500_SOURCE_V1.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
  for row in m['file_rows']:out.write(Q/row['relative'],row['relative'])
  out.write(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json','REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')
 prep=dict(epoch=time.time(),CPU_prepared=True,source_SHA=SHA,source_own_final=str(source),whole_core195_107_99_and_owned_BODY_state_independently_verified=True,own_model32998=True,
  worker=dict(path=str(worker),sha256=h(worker)),runtime=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=h(Q/'full80_runtime_native_v1.py')),
  manifest=dict(path=str(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),sha256=h(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')),
  package=dict(path=str(z),bytes=z.stat().st_size,sha256=h(z)),changed_literals_only=['paired_full80_parameter_bound_v2.py'],original_full80_backend_native_and_physical_scope_SHA_reused=True,
  own_fulltrace_review=dict(path=str(proof),sha256=h(proof)),new_GPU_scope_pending=True,full1500_GPU_NOT_launched=True,qualified50=False)
 (R/'FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json').write_text(json.dumps(prep,indent=2),encoding='utf8')
 names=['collect_left_full80_bounded_transport_actual.py','review_full80_full1500_CPU_actual.py','review_full80_original_route_prefix_CPU_actual.py']
 for name in names:
  s=(OLD/name).read_text(encoding='utf8').replace(OLD.name,NEW.name).replace(PREVIOUS,SHA).replace('native3060_bodyframe_first_final_full80_frozen1500_v1',CASE)
  write(NEW/name,s)
 s=(OLD/'review_bodyframe_first_full80_direct_e3_prefix_actual.py').read_text(encoding='utf8')
 s=s.replace("MOD4_3060_LEFT_SECOND_FULL80_20261014",OLD.name).replace('e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c',PREVIOUS)
 # Replace the candidate SHA only in its explicit comparison, preserving baseline.
 s=s.replace("b['source_SHA']=='"+PREVIOUS+"'","b['source_SHA']=='"+SHA+"'")
 s=s.replace('BODYFRAME_DIRECT_E3_ORIGINAL_FULL80_PREFIX_ACTUAL_REVIEW.json','PHASE_FINAL_DIRECT_F516_ORIGINAL_FULL80_PREFIX_ACTUAL_REVIEW.json')
 write(NEW/'review_phase_final_full80_direct_f516_prefix_actual.py',s)
 s=(OLD/'deploy_bodyframe_first_final_full80_current_terminal_reviewed_v3_once.py').read_text(encoding='utf8')
 s=s.replace(OLD.name,NEW.name).replace(PREVIOUS,SHA).replace('native3060_bodyframe_first_final_full80_frozen1500_v1',CASE).replace('MOD4_BodyframeFirstFinalFull80_20261014_Frozen1500_v1',TASK)
 s=s.replace("import transport_249_bodyframe_current_terminal_role_v3 as t","sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'"+OLD.name+"'))\nimport transport_249_bodyframe_current_terminal_role_v3 as t")
 s=s.replace("root=Path(ROOT);p=root/'payload';assert not p.exists();p.mkdir()","root=Path(ROOT);p=root/'payload';assert not p.exists();p.mkdir()\nimport sys\nsys.path.insert(0,str(p))")
 anchor="unpack=unpack.replace('ROOT',repr(ROOT)).replace('MANIFESTSHA',repr(CPU['manifest']['sha256'])).replace('SOURCESHA',repr(SHA))"
 assert s.count(anchor)==1
 s=s.replace(anchor,"unpack=unpack.replace('root=Path(ROOT);','root=Path('+repr(ROOT)+');').replace('MANIFESTSHA',repr(CPU['manifest']['sha256'])).replace('SOURCESHA',repr(SHA))")
 write(NEW/'deploy_own_phase_final_full80_unique_once.py',s)
 print(json.dumps(dict(prepared=str(R/'FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json'),source_SHA=SHA,package=prep['package'],only_new_source_namespace_no_physics_change=True,no_SSH_or_GPU=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('PHASE_FINAL_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_SSH_GPU=True),indent=2),encoding='utf8');raise
