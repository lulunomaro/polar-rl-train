"""One isolated same-G2 entry; reuse actual identical CPU/native/PPO/SDK evidence."""
from pathlib import Path
import os,sys,json,hashlib,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
OLD='/home/egde/rl_candidates/MOD4_S3_E1_G2_REVIEWED_20261010'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def call(c,code,python='/usr/bin/python3',timeout=90):
    _,o,e=c.exec_command(python+' -c '+shlex.quote(code),timeout=timeout);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');return json.loads(b)
def put(sf,path,b):
    with sf.open(path,'wbx') as out:out.write(b)
    assert sf.open(path).read()==b
def main():
    assert not (R/'STAGE_STARTED.json').exists();(R/'STAGE_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-CONTINUATION-STAGE-01',new=NEW,new_budget_seconds=0)),encoding='utf8')
    secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
    try:
        code="""from pathlib import Path
import json,time,hashlib,shutil,os
old=Path(OLD);new=Path(NEW);assert not new.exists()
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');before=B.read_bytes();ledger=json.loads(before);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
state=json.loads((old/'reports/E1_STATE.json').read_bytes());passed=json.loads((old/'reports/e1_G2_reviewed_observation_PASSED.json').read_bytes());guardian=json.loads((old/'reports/E1_GUARDIAN_STARTED.json').read_bytes())
assert state['phase']=='E1_G2_reviewed_saved_review_ready' and state['child'] is None and not (old/'reports/E1_ATTENTION.json').exists()
for row in (state['owner'],guardian,dict(pid=passed['own_PID_bound_receipt']['pid'],start_ticks=72362884)):
 p=Path('/proc')/str(row['pid'])
 if p.exists():
  s=(p/'stat').read_text().split(') ',1)[1].split();assert s[0]=='Z' or int(s[19])!=row['start_ticks']
assert len([x for x in ledger['completed_segments'] if x['pid']==passed['own_PID_bound_receipt']['pid']])==1
f=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes());assert len(f['sha256'])==329
new.mkdir();(new/'reports').mkdir()
for n,h in f['sha256'].items():
 p=old/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;nw=new/n;nw.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,nw)
assert B.read_bytes()==before
print(json.dumps(dict(epoch=time.time(),original329_byteexact=True,actual_prior_own_fullsave_exited_and_unique_segment_settled=True,canonical_bytes_exact=True)))
""".replace('OLD',repr(OLD)).replace('NEW',repr(NEW))
        copied=call(c,code);(R/'OLD329_COPIED.json').write_text(json.dumps(copied,indent=2),encoding='utf8')
        with c.open_sftp() as f:
            old=json.loads(f.open(OLD+'/reports/SOURCE_FREEZE.json').read());p=D/'payload/supervise_e1_G2_matched_continuation.py';raw=p.read_bytes();put(f,NEW+'/'+p.name,raw)
            freeze=dict(old,candidate_root=NEW,sha256=dict(old['sha256'],**{p.name:H(raw)}),original329_byteexact=True,new_same_geometry_controller_count=1)
            assert len(freeze['sha256'])==330;put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());(R/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2),encoding='utf8')
            for name in ('MATCHED_123_REVIEW.json','SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json'):put(f,NEW+'/reports/'+name,(R/name).read_bytes())
            reused=[]
            for name in ('G2_TARGET_CPU_PASSED.json','E1_COMPLETE_PPO_PREFLIGHT_PASSED.json','G2_BEHAVIOR_PACKAGE_READY.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json'):
                b=f.open(OLD+'/reports/'+name).read();put(f,NEW+'/reports/'+name,b);reused.append(dict(name=name,path=OLD+'/reports/'+name,bytes=len(b),sha256=H(b),same_scope_evidence_reused_no_replay=True))
            (R/'SAME_SCOPE_EVIDENCE_REUSED.json').write_text(json.dumps(dict(epoch=time.time(),files=reused,no_new_CPU_test_SDK_native_PPO_preflight_clock_or_package=True),indent=2),encoding='utf8')
        cpu=call(c,"""from pathlib import Path
import sys,json,time,hashlib
D=Path(NEW);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'))
import torch;torch.set_num_threads(1);import supervise_e1_G2_matched_continuation as m
m.verify();m.wait_existing();src=m.source();full=m.fullsave(src);ck=torch.load(src,map_location='cpu',weights_only=False)
assert full['finite_tensors']==96 and ck['E1_terrain_state']['profile']=='mod4_G2_CAD_derived_20mm_v1' and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),new_controller_source330_verified=True,complete_four_case_review_verified=True,actual_full_source=full,source_bytes=src.stat().st_size,same_G2_state=True,old_safe_boundary_verified=True,no_CUDA_initialized=True,no_repeated_preflight=True)))
""".replace('NEW',repr(NEW)),PY,180)
        (R/'CPU_SOURCE_BOUNDARY_ADMITTED.json').write_text(json.dumps(cpu,indent=2),encoding='utf8')
        dispatched=call(c,"""from pathlib import Path
import sys,subprocess,time,json,os
D=Path(NEW);assert not (D/'dispatch.log').exists() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
with (D/'dispatch.log').open('x') as out:p=subprocess.Popen([PY,str(D/'supervise_e1_G2_matched_continuation.py')],cwd='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002',stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(2);assert p.poll() is None,(D/'dispatch.log').read_text()
q=Path('/proc')/str(p.pid);st=(q/'stat').read_text().split(') ',1)[1].split();argv=(q/'cmdline').read_bytes().decode().split('\\0');assert str(D/'supervise_e1_G2_matched_continuation.py') in argv
print(json.dumps(dict(epoch=time.time(),owner=dict(pid=p.pid,start_ticks=int(st[19]),cwd=os.readlink(q/'cwd'),argv=argv,state=st[0]),new_root=str(D),source_count=330,observation_seconds=900,no_repeat_native_PPO_preflight_clock=True,new_budget_seconds=0)))
""".replace('NEW',repr(NEW)).replace('PY',repr(PY)))
        (R/'DISPATCH_ACTUAL.json').write_text(json.dumps(dispatched,indent=2),encoding='utf8');print(json.dumps(dispatched))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
    try:main()
    except Exception:
        (R/'STAGE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-CONTINUATION-STAGE-01',error=traceback.format_exc(),original_failure_source_and_costs_preserved=True,no_blind_repeat=True),indent=2),encoding='utf8');raise
