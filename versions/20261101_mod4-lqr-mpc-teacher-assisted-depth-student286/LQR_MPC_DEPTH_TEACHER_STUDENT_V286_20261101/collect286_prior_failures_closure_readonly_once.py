"""Read original283/285 fee segments while preserving live286 canonical owner."""
from pathlib import Path
import json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
from launch286_original_teacher_student_once import module,put,read
REMOTE=r'''from pathlib import Path
import fcntl,hashlib,json,psutil,time
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
active=c['active_segment'];assert active and active['owner_parent_pid']==v['current_owner']['pid']
assert v['current_GO']['original_owner_pid']==v['current_owner']['pid']
out=[]
for prior in v['prior']:
 owner=prior['owner'];O=Path(owner['root']);J=Path(prior['task']['job_root']);control=J/('control'+prior['number'])
 final=json.loads((O/'COHORT_FINAL.json').read_bytes());exit=json.loads((O/'OWNER_EXIT_ACTUAL.json').read_bytes())
 terminal=json.loads((control/'NODE_TERMINAL_ACTUAL.json').read_bytes());nodeexit=json.loads((control/'NODE_EXIT_ACTUAL.json').read_bytes())
 assert final['original_cost_settled'] and exit['original_cost_settled'] and nodeexit['all_own_children_waited'] and nodeexit['private_EX_released']
 assert terminal['row']['terminal_all_own_children_waited'] and terminal['row']['original_error'] and not terminal['row']['final']
 identity=json.loads((control/'NODE_IDENTITY.json').read_bytes())
 for x in (owner,identity):
  try:p=psutil.Process(x['pid']);assert p.create_time()!=x['creation'] or p.status()==psutil.STATUS_ZOMBIE
  except psutil.NoSuchProcess:pass
 segments=[s for s in c['completed_segments']if s.get('owner_parent_pid')==owner['pid']]
 assert len(segments)==1;s=segments[0];g=final['go']['jump_72'];fee=s['experts']['jump_72']
 assert fee['started_epoch']==g['learning_started_epoch'] and fee['duration_bound_passed']
 assert abs(s['charged_expert_seconds']-fee['charged_seconds'])<1e-5
 texts=[]
 for root in (O,control,J/'production'):
  for p in sorted(root.glob('*')):
   if p.is_file()and p.suffix in('.json','.log'):
    b=p.read_bytes();texts.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
 out.append(dict(trial_id=prior['task']['run_id'],original_closed_segment=s,raw_fee_charged_once=fee['charged_seconds'],
  final=final,owner_exit=exit,node_terminal=terminal,node_exit=nodeexit,model_reads=0,full_UTF8=texts))
print(json.dumps(dict(epoch=time.time(),passed=True,current286_owner_matched=True,active_segment_preserved=True,
 prior=out,no_account_write=True,no_healthy_GPU_or_model_scan=True)))'''

def main():
    assert not(R/'ROOT286_PRIOR283_285_CLOSURE_AND_ORIGINAL_FEES.json').exists()
    active=read(R/'ROOT286_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json')
    prior=[]
    for number in ('283','285'):
        old=T/('LQR_MPC_DEPTH_TEACHER_STUDENT_V'+number+'_20261101')
        prior.append(dict(number=number,task=read(old/('TASK'+number+'_FROZEN.json')),
          owner=read(old/'reports'/('ROOT'+number+'_ORIGINAL_OWNER_LAUNCH_ACTUAL.json'))['owner']))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    transport=previous=client=secret=None
    try:
        transport,previous=module('close286_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install()
        secret=module('close286_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover()
        client=d.connect72(secret);secret=None
        result=d.code(client,d.PY72,REMOTE,dict(current_owner=active['original_owner'],current_GO=active['current']['go']['jump_72'],prior=prior),timeout=60)
        put('ROOT286_PRIOR283_285_CLOSURE_AND_ORIGINAL_FEES.json',result)
        print(json.dumps(dict(passed=result['passed'],current286_preserved=True,prior=[dict(trial=x['trial_id'],fee=x['raw_fee_charged_once'])for x in result['prior']])))
    finally:
        secret=None
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put('ROOT286_PRIOR_CLOSURE_SSH_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':main()
