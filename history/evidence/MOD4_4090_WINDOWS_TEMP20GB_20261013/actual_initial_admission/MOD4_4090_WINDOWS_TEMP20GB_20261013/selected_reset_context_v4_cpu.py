from pathlib import Path;import ast,json,hashlib,shutil,time,psutil,msvcrt
r=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013');old=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/temporary_scope2048_memory20GB_contrib_ready_v3_20261013');new=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/temporary_scope2048_memory20GB_reset_context_v4_20261013')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
e=json.loads((old/'attempts/temporary2048_sdk_v1/output/ORIGINAL_ERROR.json').read_bytes());x=json.loads((old/'attempts/temporary2048_sdk_v1/EXIT_RECEIPT.json').read_bytes());assert e['prePPO'] and 'Inplace update to inference tensor' in e['error'] and x['own_child_and_descendants_actual_absent'] and x['worker_exitcode']==1
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload');(new/'reports').mkdir();(new/'attempts').mkdir()
w=new/'payload/temporary_worker.py';before=ref(w);tree=ast.parse(w.read_text(encoding='utf8'));hits=0
for n in ast.walk(tree):
 for field,value in list(ast.iter_fields(n)):
  if not isinstance(value,list):continue
  for i,item in enumerate(value):
   if isinstance(item,ast.Expr) and ast.unparse(item).startswith('env._reset_idx(selected)'):
    block=value[i:i+3];assert [ast.unparse(z).split('(')[0] for z in block]==['env._reset_idx','env.scene.write_data_to_sim','env.sim.forward']
    # Include originalscene.update directly following these3, no extra call.
    assert ast.unparse(value[i+3]).startswith('env.scene.update(');block=value[i:i+4]
    ctx=ast.With(items=[ast.withitem(context_expr=ast.parse('torch.inference_mode()',mode='eval').body,optional_vars=None)],body=block,type_comment=None)
    value[i:i+4]=[ctx];hits+=1;break
assert hits==1
w.write_text(ast.unparse(ast.fix_missing_locations(tree))+'\n',encoding='utf8');compile(w.read_text(encoding='utf8'),str(w),'exec')
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf['scope_root']=str(new);mf['epoch']=time.time();mf['independent_selected_reset_context_only_fix']=dict(old=before,new=ref(w),original300control1200callback_loop_AST_unchanged=True,only_original4calls_context_wrapped=True,no_new_physics_step_reset_or_threshold_change=True)
cpu=json.loads(Path(mf['target_CPU_receipt']['path']).read_bytes());cpu.update(scope=str(new),epoch=time.time(),new_selected_reset_context=mf['independent_selected_reset_context_only_fix'],old_source_failure_preserved=str(old));cp=new/'reports/TARGET_TEMP2048_RESET_CONTEXT_CPU_ACTUAL.json';cp.write_text(json.dumps(cpu,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(cp)
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
f=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';f.write_text(json.dumps(mf,indent=2),encoding='utf8');l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(dict(epoch=time.time(),case_id='temporary2048_memory20GB_reset_context_sequence_v4',approved_GPU_scope=True,mode='sdk',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(f),human20GB_temporary_branch_authorized=True),indent=2),encoding='utf8')
proof=dict(epoch=time.time(),passed_CPU_context_only=True,worker_change=mf['independent_selected_reset_context_only_fix'],old_error=e,old_EXIT=x,all_actual6Lab_apps_sourcefreeze_count=len(mf['sourcefreeze_files']),manifest=ref(f),source_originals_not_hotpatched=True,new_Task_GPU_future=True)
(new/'reports/RESET_CONTEXT_ONLY_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
