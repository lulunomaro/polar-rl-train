"""Close out only this actual own saved Wave segment; no training or budget transaction."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports';ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p
def main():
 assert not (R/'WAVE_FINAL_CLOSEOUT_STARTED.json').exists()
 actualpath=sorted(R.glob('WAVE_ACTUAL_*.json'))[-1];actual=json.loads(actualpath.read_bytes());cpupath=sorted(R.glob('WAVE_OWN_CPU_[0-9]*.json'))[-1];cpu=json.loads(cpupath.read_bytes());own=cpu['saved'][0];final=own['final_PASS_and_unique_segment'];assert final and not final['discarded_preflight']
 assert actual['state']['phase']=='E1_WAVE_G3_isolated_saved_review_ready' and actual['canonical']['active_segment'] is None and not actual['reports'].get('E1_ATTENTION.json')
 h=final['health'];assert h['control_steps']==144 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==576 and h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed'] and h['stop_reason'] is None
 assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and final['actual_environment_steps']==2880000 and final['actual_updates']==6 and len(final['unique_completed_segment'])==1
 save('WAVE_FINAL_CLOSEOUT_STARTED.json',dict(epoch=time.time(),trial_id='E1-WAVE-G3-OWN-FINAL-CLOSEOUT-01',own_final_CPU102_source366_verified=True,no_recharge=True))
 segment=final['unique_completed_segment'][0];review=save('WAVE_FORMAL_FINAL_ACTUAL_REVIEW.json',dict(epoch=time.time(),expert='E1_WAVE',checkpoint=own['checkpoint'],actual_snapshot_count=own['actual_snapshot_count'],own366freeze_verified=own['own366freeze_verified'],own_PID=own['own_PID_bound_receipt']['pid'],updates=6,controls=144,environment_steps=2880000,callbacks=576,health=h,unique_segment=segment,actual_accounted_seconds=segment['ended_epoch']-segment['started_epoch'],original_parent_settled_once=True,full_same_geometry_same_command_CPUCUDA_restore=own['startup_same_G3_same_command_verified'],independent_output_ownership_final=actual['reports']['E1_WAVE_OWNERSHIP_FINAL_VERIFIED.json'],published131=actual['reports']['E1_131-e1-wave-g3-isolated_ASYNC_PUBLISHED.json'],behavior131_complete=False,not_all_course_finished=True,no_permanent_anti_forgetting_claim=True,new_budget_seconds=0))
 note='独立E1_WAVE已实际首300s观察、完整保存并退出。ownmodel32068 SHA'+own['checkpoint']['sha256']+' / CPU102 / source366 / '+str(own['actual_snapshot_count'])+'实际srcsnapshot及own366完整freeze已核；6updates144controls2.88Menvsteps576callbacks exact，ordinary/integrity/unknown0/nonfinitefalse/STOPnone，closure'+str(h['max_closure_error_m']*1000)+'mm。actual'+str(segment['ended_epoch']-segment['started_epoch'])+'s原父唯一结清，未扩展/重charge。全部sameG3/samecommand actorcriticstdoptimizer/D0D7/globalnamed/commandprivateCPUCUDA恢复与diskroundtrip/savedsourceepisode+1实际通过，非PhysXresume。独立输出目录与warmstartSHA保持，其他专家不是optimizer/save目标。131四case已自动发布、尚需actualcomplete独立审查；不把完整保存称35mm全通过/永久抗遗忘/MoE路由完成。004细分计划已批准执行，下一CPU准备独立CURB/SLOPE/STair范围、待131真实行为决定后按各自新合同推进；V3旧平地pure未采用证据保持。原130退化/false/raw/成本/两有效prefix/读者错误与本阶段所有回执Git捕获。\n'
 note_path=R/'WAVE_FORMAL_FINAL_REPORT.md';assert not note_path.exists();note_path.write_bytes(note.encode())
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  files={'E1_WAVE_G3_ISOLATED_FORMAL_FINAL_ACTUAL_REVIEW.json':review,'E1_WAVE_G3_OWN_FINAL_CPU_VERIFIED.json':cpupath,'E1_WAVE_G3_FORMAL_FINAL_CURRENT_ACTUAL.json':actualpath,'E1_WAVE_G3_FORMAL_FINAL_REPORT.md':note_path,'E1_WAVE_G3_131_CURRENT_COLLECTION.json':sorted(R.glob('CANDIDATE_131_COLLECTED_*.json'))[-1]}
  with c.open_sftp() as f:
   for n,p in files.items():
    b=p.read_bytes()
    with f.open(E+'/'+n,'wbx') as q:q.write(b)
    assert f.open(E+'/'+n).read()==b
  code=r'''from pathlib import Path
import hashlib,json,fcntl,time,os
R=Path(REPORTS);D=Path(ROOT);B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};budget=B.read_bytes();l=json.loads(budget);assert l['active_segment'] is None and l['authorized_training_seconds']==828000
p=json.loads((D/'reports/e1_wave_G3_isolated_observation_PASSED.json').read_bytes());s=json.loads((D/'reports/E1_STATE.json').read_bytes());assert s['phase']=='E1_WAVE_G3_isolated_saved_review_ready' and s['child'] is None
for loc in (s['owner'],json.loads((D/'reports/E1_GUARDIAN_STARTED.json').read_bytes()),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=80211793)):
 q=Path('/proc')/str(loc['pid'])
 if q.exists():
  a=(q/'stat').read_text().split(') ',1)[1].split();assert a[0]=='Z' or int(a[19])!=loc['start_ticks']
for lock in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lock.open('r') as q:fcntl.flock(q,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(q,fcntl.LOCK_UN)
assert len([x for x in l['completed_segments'] if x['pid']==p['own_PID_bound_receipt']['pid']])==1
cp=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=cp.read_bytes();v=json.loads(before);a=v['terrain_subexpert_revision004'];assert a['approved'] and 'wave_first_actual_fullsave' not in a
a['wave_first_actual_fullsave']=dict(epoch=time.time(),root=str(D),actual_review=str(R/'E1_WAVE_G3_ISOLATED_FORMAL_FINAL_ACTUAL_REVIEW.json'),own_CPU=str(R/'E1_WAVE_G3_OWN_FINAL_CPU_VERIFIED.json'),candidate_checkpoint_SHA=p['checkpoint']['sha256'],actual_updates=p['actual_updates'],unique_completed_segment=p['unique_completed_segment'],all_actual_parent_guardian_child_exited=True,two_OS_locks_free=True,phase='E1_WAVE_G3_isolated_saved_review_ready',needs_actual131_behavior=True,gate_untrained=True,more_PPO_automatic=False)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert cp.read_bytes()==before;tmp=cp.with_name(cp.name+'.WaveFinal-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,cp)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='Independent E1_WAVE actual final source366:';assert marker.encode() not in old;msg='\n\n'+marker+' own32068 SHA2b4f5a575d3a4d97013b331e215c503ab86e528a63a92d719a3366a684b52284 CPU102/72actualsnapshot+366ownfreeze/PID2348218/PASSED unique originalparent settled. 6updates144control2.88Msteps576callback ordinaryintegrityunknown0 nonfinitefalse STOPnone closure.947713444mm. FullsameG3samecommand actualCPUCUDA restoration/savedsourceepisode1 and ownoutput verified. Parent guardian child exited/twoOSlocksfree/activeempty legal review boundary. Read final actualreport/CPU and131 actualcollection; all4published pendingbehavior. Do not revive oldentry/automatic900s/50mm/V3pure. Separate terrain task evidence from oldflat diagnostic; E0frozen, nextCurbslopeStair each independent new scope under approved004, no gate readiness or allRMgraduation claim. Allnewfinalbehaviorreadererrorsmonitorsync reports Git required.\n';assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.WaveFinal-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),wave_final_closeout_synced=True,all_actual_parent_guardian_child_exited=True,two_real_OS_locks_free=True,canonical_master_approval_tracks_RM_bytes_preserved=True,remaining_idle_seconds=l['authorized_training_seconds']-l['charged_training_seconds'],new_budget_seconds=0)))
'''.replace('Path(REPORTS)','Path('+repr(E)+')').replace('Path(ROOT)','Path('+repr(ROOT)+')')
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(out+err).decode(errors='replace');v=json.loads(out);v['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];save('WAVE_FINAL_CLOSEOUT_METADATA_SYNCED.json',v);print(json.dumps(v))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('WAVE_FINAL_CLOSEOUT_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_completed_metadata_or_budget_transactions=True));raise
