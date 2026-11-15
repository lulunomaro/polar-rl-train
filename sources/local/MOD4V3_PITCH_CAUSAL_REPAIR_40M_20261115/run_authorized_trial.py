"""Collect the explicitly authorized no-update probe, then start exactly one2400s run."""
from pathlib import Path
import time,json,sys,subprocess,shlex,traceback
T=Path(__file__).resolve().parent;E=T/'evidence';sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
out=E/'diagnostic_causal';out.mkdir(exist_ok=False);remote=REMOTE+'/probe_causal_pitch_lookahead';seen={};start=time.time()
try:
 while True:
  c=connect()
  try:
   sf=c.open_sftp()
   try:entries=sf.listdir_attr(remote)
   except FileNotFoundError:entries=[]
   for item in entries:
    if not item.filename.endswith('.json') or seen.get(item.filename)==(item.st_mtime,item.st_size):continue
    sf.get(remote+'/'+item.filename,str(out/item.filename));seen[item.filename]=(item.st_mtime,item.st_size)
   sf.get(REMOTE+'/probe_causal_pitch_lookahead.log',str(out/'owner.log'))
  finally:c.close()
  if (out/'ERROR.json').exists():raise RuntimeError((out/'ERROR.json').read_text())
  if (out/'SAFE_CLOSED.json').exists():break
  if time.time()-start>900:raise TimeoutError('Probe has not closed; no training auto-relaunch')
  time.sleep(10)
 result=json.loads((out/'ROUGH_PROBE.json').read_text());assert result['no_optimizer_updates'] and result['num_envs']==2048
 pitch=result['pitch'];assert pitch['prediction_coefficient']==60. and pitch['prediction_horizon_s']==.2 and pitch['target_envs']==615
 assert pitch['reward_component_sums']['predicted_pitch']<0.
 assert result['peaks']['command_overwrite_m_s']==0.
 (E/'NATIVE_LOOKAHEAD_GATE.json').write_text(json.dumps(dict(passed=True,no_optimizer=True,actual_added_prediction_cost=pitch['reward_component_sums']['predicted_pitch'],done_totals=result['done_totals'],command_overwrite_m_s=0.,model_unchanged=True),indent=2)+'\n',encoding='utf8')
 print('NATIVE_LOOKAHEAD_GATE_PASS',json.dumps(pitch),flush=True)
 r=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/'start_training.py')],cwd=T.parents[2]);r.check_returncode()
except BaseException:
 (E/'PROBE_OR_START_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),automatic_relaunch=False),indent=2)+'\n',encoding='utf8');raise
