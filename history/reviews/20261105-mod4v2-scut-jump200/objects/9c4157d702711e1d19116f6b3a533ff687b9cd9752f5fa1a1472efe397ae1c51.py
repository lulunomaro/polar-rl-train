"""New random fixture reaches the existing32-iteration BPTT warmup boundary."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
import torch
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
R=N/'sampling_optimized_cli14';R.mkdir(exist_ok=False)
source=json.loads((N/'sampling_scripted_production_resume12/RESULT.json').read_bytes())['checkpoint']
with Path(source['path']).open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==source['SHA']
value=torch.load(source['path'],map_location='cpu',weights_only=False)
before=value['context_reward_extension']['counts']['pi_bptt_optimizer_steps']
value['iteration']=32 # Synthetic fixture scheduling only, all learned tensors/Adam retained.
checkpoint=R/'random_fixture_iteration32.pt'
torch.save(value,checkpoint)
with checkpoint.open('rb')as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
env=dict(os.environ,PYTHONPATH=str(G/'project/isaac'))
argv=[sys.executable,'-B','-X','utf8','-m','mod4v2_scut.supermimic_train',
    '--package','F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package',
    '--components',str(N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4'),
    '--reset-bank',str(N/'runtime_refs/runtime/isaac/mod4/reset_bank.json'),
    '--job-root',str(R/'production'),'--resume',str(checkpoint),'--resume-SHA',sha,
    '--binding',str(G/'project/isaac/mod4v2_scut/SUPERMIMIC_BINDINGS.json'),
    '--num-envs','4','--small-test','--max-updates','1','--save-deadline',str(time.time()+180),
    '--sampling-optimization']
with(R/'WORKER.log').open('xb')as stream:rc=subprocess.run(argv,env=env,stdout=stream,stderr=subprocess.STDOUT).returncode
read=lambda name:json.loads((R/'production'/name).read_bytes())
progress=read('LATEST_PROGRESS.json');final=read('FINAL.json');close=read('APP_CLOSE_INTENT.json')
assert rc==0 and progress['new_verified_BPTT_steps']==1
assert final['verified_BPTT_steps']==before+1 and final['checkpoint']['iteration']==33
assert close['env_closed']and not close['error']
out=dict(epoch=time.time(),passed=True,production_PT_reads=0,SSH=0,
    source_random_fixture=source,synthetic_iteration_only=32,
    source_fixture=dict(path=str(checkpoint),bytes=checkpoint.stat().st_size,SHA=sha),
    prior_cli13='Warmup-phase atiteration1->2,0newBPTT; raw retained, not sufficient for CLI policyupdate evidence',
    actual_new_H32=1,progress=progress,final=final,close=close)
(R/'RESULT.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(out))
