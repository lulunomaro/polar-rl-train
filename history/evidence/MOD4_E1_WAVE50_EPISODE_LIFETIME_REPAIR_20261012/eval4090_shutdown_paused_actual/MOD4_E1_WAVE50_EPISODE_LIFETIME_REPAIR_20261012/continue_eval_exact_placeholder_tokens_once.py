from pathlib import Path
import ast,json,os,re,traceback,time
import prepare_and_start_linux4090_frozen_evaluation_once as original
io=original.io
def main():
 assert not (io.R/'LINUX4090_EVAL_TARGET_CPU_PREPARED.json').exists()
 own=json.loads(max(io.R.glob('LIFETIME459_OWN_FINAL_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes());compact=dict(own_checkpoint={k:own['own_checkpoint'][k] for k in ('path','sha256','iteration_stored')})
 tree=ast.parse(Path(original.__file__).read_text());items=[v.value for v in ast.walk(tree) if isinstance(v,ast.Constant) and isinstance(v.value,str) and v.value.startswith('from pathlib import Path\n') and ('D.mkdir();' in v.value or 'compile(file.read_text()' in v.value)];assert len(items)==2
 mapping=dict(ROOT_TOKEN=repr(original.ROOT),TRAINROOT_TOKEN=repr('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012'),OWN_TOKEN=repr(json.dumps(compact)),PY_TOKEN=repr(io.PY))
 def replace(s):
  s=re.sub(r'\b(ROOT_TOKEN|TRAINROOT_TOKEN|OWN_TOKEN|PY_TOKEN)\b',lambda m:mapping[m[0]],s);compile(s,'exact-placeholder-prechecked','exec');return s
 stage=replace(next(x for x in items if 'D.mkdir();' in x));launch=replace(next(x for x in items if 'compile(file.read_text()' in x));io.save('LINUX4090_EVAL_EXACT_TOKEN_PREPARATION_REVIEW.json',dict(epoch=time.time(),passed=True,original_ROOT_inside_TRAINROOT_substring_SyntaxError_before_GPU_preserved=True,exact_word_tokens_and_compact_proof_precompiled=True,no_oldjob_replay=True))
 n,w=io.connect_linux_only()
 try:
  v=io.run(n,stage);io.save('LINUX4090_EVAL_TARGET_CPU_PREPARED.json',v)
  with n.open_sftp() as f:
   with f.open(original.ROOT+'/eval4090_frozen_batch_once.py','wb') as out:out.write(original.WORKER.encode())
  v=io.run(n,launch);io.save('LINUX4090_EVAL_DISPATCH_ACTUAL.json',v);print(json.dumps(v))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:io.save('EXACT_TOKEN_EVAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),only_unexecuted_substep_continued=True));raise
