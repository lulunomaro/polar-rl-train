"""Append verified monitor and Git receipts; preserve training and historical plan bytes."""
from slope_io import *
import traceback

def main():
    names={'E1_SLOPE8_137_COMPLETE_NEXT10_STAGE_GIT_RECORDED.json':R/'COMPLETE137_SLOPE10_CPU_STAGE_GIT_RECORDED.json',
           'E1_SLOPE8_137_COMPLETE_NEXT10_MONITOR_ACTUAL_VERIFIED.json':R/'COMPLETE137_FINAL_MONITOR_ACTUAL_VERIFIED.json',
           'MOD4_MONITOR_CURRENT_137_COMPLETE_SLOPE10_CPU_PROMPT.md':D/'MONITOR_CURRENT_137_COMPLETE_SLOPE10_CPU_PROMPT.md'}
    assert json.loads(names['E1_SLOPE8_137_COMPLETE_NEXT10_STAGE_GIT_RECORDED.json'].read_bytes())['remote_main_tag_peeled_verified']
    assert json.loads(names['E1_SLOPE8_137_COMPLETE_NEXT10_MONITOR_ACTUAL_VERIFIED.json'].read_bytes())['automation_prompt_exact']
    save('COMPLETE137_FINAL_MONITOR_GIT_SYNC_STARTED.json',dict(epoch=time.time(),metadata_only=True))
    n,w=connect_both()
    try:
        with n.open_sftp() as f:
            prior=f.listdir(E+'/reports');assert all(x not in prior for x in names)
            for name,path in names.items():put(f,E+'/reports/'+name,path.read_bytes())
        row=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(__CENTRAL__)/'reports';B=Path(__BUDGET__);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];s=rev['slope8_137_actualray_scope'];assert rev['approved'] and not s['actual_complete_review_pending'] and s['scoped8deg_frozen_behavior_accepted']
mon=json.loads((R/'E1_SLOPE8_137_COMPLETE_NEXT10_MONITOR_ACTUAL_VERIFIED.json').read_bytes());g=json.loads((R/'E1_SLOPE8_137_COMPLETE_NEXT10_STAGE_GIT_RECORDED.json').read_bytes())
assert mon['automation_prompt_exact'] and mon['status']=='ACTIVE' and mon['rrule']=='FREQ=HOURLY;INTERVAL=2' and g['remote_main_tag_peeled_verified'] and not g['push_pending']
assert json.loads(budget)['active_segment'] is None and json.loads(budget)['authorized_training_seconds']==828000
s.update(complete_stage_Git_receipt=str(R/'E1_SLOPE8_137_COMPLETE_NEXT10_STAGE_GIT_RECORDED.json'))
rev.update(actual_monitor_receipt=str(R/'E1_SLOPE8_137_COMPLETE_NEXT10_MONITOR_ACTUAL_VERIFIED.json'),actual_monitor_prompt=str(R/'MOD4_MONITOR_CURRENT_137_COMPLETE_SLOPE10_CPU_PROMPT.md'))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.COMPLETE137-MONITOR-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();append='\n\nComplete137/new10CPU stage Git remote main/tag/peeled verified: '+g['commit']+'/'+g['tagobject']+'. Existing mod4-10 ACTIVE every2h prompt verified exactly against latest137 complete/next10 CPU-only handoff. New monitoring/Git receipts reference above; later ordinary supplement must capture these receipts and final monitor. No training, GUI, budget, or oldonce replay.\n'
assert h.read_bytes()==hb;tmp=h.with_name(h.name+'.COMPLETE137-MONITOR-'+str(time.time_ns()));tmp.write_bytes(hb+append.encode());os.replace(tmp,h)
assert B.read_bytes()==budget and all((R/n).read_bytes()==raw for n,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,monitor_and_stage_Git_receipts_synced=True,master_approval_tracks_RM_canonical_bytes_preserved=True,no_GPU_PPO_or_budget_write=True,canonical_SHA=hashlib.sha256(budget).hexdigest())))
'''.replace('__CENTRAL__',repr(E)).replace('__BUDGET__',repr(B)))
        p=save('COMPLETE137_FINAL_MONITOR_GIT_METADATA_SYNCED.json',row)
        with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE8_137_COMPLETE_NEXT10_MONITOR_GIT_METADATA_SYNCED.json',p.read_bytes())
        print(json.dumps(row))
    finally:cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('COMPLETE137_FINAL_MONITOR_GIT_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_sync_replay=True));raise
