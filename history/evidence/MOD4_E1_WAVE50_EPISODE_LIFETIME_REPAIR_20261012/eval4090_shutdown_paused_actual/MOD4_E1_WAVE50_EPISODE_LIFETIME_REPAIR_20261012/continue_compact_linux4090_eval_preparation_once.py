from pathlib import Path
import ast,json,os,time,hashlib,traceback
import prepare_and_start_linux4090_frozen_evaluation_once as original
io=original.io
def main():
 n,w=io.connect_linux_only()
 try:
  boundary=io.run(n,"from pathlib import Path;import json;d=Path("+repr(original.ROOT)+");print(json.dumps(dict(root_exists=d.exists(),files=[str(p.relative_to(d)) for p in d.rglob('*') if p.is_file()] if d.exists() else [],no_GPU_Popen_by_original_before_this_CPU_substep=True)))")
  io.save('LINUX4090_OVERSIZED_SSH_PREPARATION_OUTCOME_ACTUAL.json',boundary);assert not boundary['root_exists'], 'Inspect original partialstage; no blindreplay'
  own=json.loads(max(io.R.glob('LIFETIME459_OWN_FINAL_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes());compact=dict(own_checkpoint={k:own['own_checkpoint'][k] for k in ('path','sha256','iteration_stored')})
  tree=ast.parse(Path(original.__file__).read_text());items=[v.value for v in ast.walk(tree) if isinstance(v,ast.Constant) and isinstance(v.value,str) and v.value.startswith('from pathlib import Path\n') and ('D.mkdir();' in v.value or 'compile(file.read_text()' in v.value)];assert len(items)==2
  stage=next(x for x in items if 'D.mkdir();' in x).replace('ROOT_TOKEN',repr(original.ROOT)).replace('TRAINROOT_TOKEN',repr('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012')).replace('OWN_TOKEN',repr(json.dumps(compact)))
  v=io.run(n,stage);io.save('LINUX4090_EVAL_TARGET_CPU_PREPARED.json',v)
  with n.open_sftp() as f:
   with f.open(original.ROOT+'/eval4090_frozen_batch_once.py','wb') as out:out.write(original.WORKER.encode())
  launch=next(x for x in items if 'compile(file.read_text()' in x).replace('ROOT_TOKEN',repr(original.ROOT)).replace('PY_TOKEN',repr(io.PY));v=io.run(n,launch);io.save('LINUX4090_EVAL_DISPATCH_ACTUAL.json',v);print(json.dumps(v))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:io.save('COMPACT_LINUX4090_EVAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),only_unexecuted_steps_no_GPU_replay=True));raise
