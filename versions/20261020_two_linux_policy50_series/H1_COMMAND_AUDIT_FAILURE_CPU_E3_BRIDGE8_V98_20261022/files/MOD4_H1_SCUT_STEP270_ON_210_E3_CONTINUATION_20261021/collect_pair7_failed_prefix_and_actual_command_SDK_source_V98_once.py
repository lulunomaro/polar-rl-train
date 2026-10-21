from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;N=T/'H1_STEP270_E3_PAIR_V7_20261022';R=T/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
read=lambda p:json.loads(Path(p).read_bytes())
CODE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,time
B=Path(v['h1']);owner=Path(v['owner'])
assert json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'] and json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
for root in (B,owner):
 for p in psutil.process_iter(['pid','cmdline']):
  try:assert p.pid==os.getpid() or not any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or [])
  except psutil.Error:pass
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');before=C.read_bytes();c=json.loads(before)
assert c['active_segment'] is None and c['remaining_training_seconds']==v['remaining']
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['lock'])):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
prefix=json.loads((B/'job0/production/failed_prefix_complete.json').read_bytes());assert prefix['failed_partial_prefix'] and prefix['updates']==100
p=Path(prefix['path']);assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size==prefix['bytes']
sdk=Path('/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab');texts=[]
for p in (sdk/'envs/mdp/commands/velocity_command.py',sdk/'managers/command_manager.py'):
 raw=p.read_bytes();texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8')))
assert C.read_bytes()==before
print(json.dumps(dict(epoch=time.time(),all_own_training_processes_actual_out=True,prefix=prefix,actual_installed_SDK_source_texts=texts,no_GPU_or_budget_write=True,failed_prefix_not_production_qualified=True)))
'''
def main():
    q=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');proof=read(N/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert proof['H1_production_failed_no_FINAL']
    put('V98_H1_FAILED_PREFIX_DIAGNOSTIC_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),only_new_failed_prefix_and_actual_SDK_text=True,no_GPU_or_source_qualification=True))
    c=d.t.connect()
    try:
        v=d.code(c,d.t.PY,CODE,dict(h1=q['roots']['h1'],owner=q['owner_root'],lock=q['specs']['h1']['private_lock'],remaining=proof['remaining_actual_snapshot']),timeout=45)
        f=v['prefix'];folder=N/'failed_H1_diagnostic_models';folder.mkdir();p=folder/Path(f['path']).name;part=p.with_suffix('.pt.partial')
        sf=c.open_sftp()
        try:sf.get(f['path'],str(part))
        finally:sf.close()
        assert part.stat().st_size==f['bytes'] and hashlib.sha256(part.read_bytes()).hexdigest()==f['SHA'];part.replace(p)
        v['prefix'].update(local_path=str(p),twohost_complete_SHA=True)
        put('V98_H1_FAILED_PREFIX_AND_ACTUAL_COMMAND_SDK_SOURCE_RETURNED_ACTUAL.json',v)
        print(json.dumps(dict(returned=True,failed_prefix_SHA=f['SHA'],only_diagnostic_not_source=True)))
    finally:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:put('V98_H1_FAILED_PREFIX_DIAGNOSTIC_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_or_qualification=True));raise
