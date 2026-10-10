"""New complete129 decision and metadata annotation only; no training or ledger writes."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p
def main():
 assert not (R/'COMMAND129_COMPLETE_FINALIZE_STARTED.json').exists()
 review=sorted(R.glob('CANDIDATE_129_REVIEW_[0-9]*.json'))[-1];selected=sorted(R.glob('CANDIDATE_129_SELECTED_SOURCE_REVIEW_[0-9]*.json'))[-1]
 v=json.loads(review.read_bytes());a=json.loads(selected.read_bytes());assert v['review_complete'] and a['review_complete'] and not v['pending']
 own=v['own'];ck=own['checkpoint'];assert ck['sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e' and ck['finite_tensors']==102
 t=v['terrain'];assert t['base_review']['ordinary']==0 and t['groups']['forward']['complete_envs']==24 and t['groups']['reverse']['complete_envs']==27
 assert a['summary']['retention']['world']['candidate_source364']['passed']==63
 missing=[x for x in t['full_route_rows'] if x['group']=='forward' and not x['complete_episodes']];assert [x['env'] for x in missing]==[6,21,33]
 save('COMMAND129_COMPLETE_FINALIZE_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-COMMAND-129-COMPLETE-DECISION-01',metadata_only=True))
 decision=save('COMMAND129_COMPLETE_RETENTION_DECISION.json',dict(epoch=time.time(),trial_id='E1-G3-COMMAND-129-COMPLETE-DECISION-01',actual_complete_review=str(review),selected_source_comparison=str(selected),selected_next_source=ck,source_fullsave_PID_PASSED_unique_and_CPU_verified=True,summary=a['summary'],terrain_ordinary=0,terrain_closure_mm=t['base_review']['closure_mm'],uncompleted_forward_prefixes=missing,negative4pi_original_residual_env_count=1,world_original_residual_env_count=1,positive4pi_original_passed=8,continuation_admitted=True,continuation_scope='same35mm geometry and same verified conditional plane signed straight/world05 command scope; one900s load-learn-save-exit then complete matched review',no_next50mm_admission=True,no_permanent_anti_forgetting_or_all_E1_RM70mm_graduation=True,no_causal_ablation_proof=True,old126_127_128_and_original_false_flags_preserved=True,no_more_same_scope_preflight_SDK_native_or_clock_replay=True,new_budget_seconds=0))
 work=save('NEXT_COMMAND_RETENTION_MATCHED_CONTINUATION_WORK_ORDER.json',dict(epoch=time.time(),trial_id='E1-G3-COMMAND-MATCHED-900S-WORK-ORDER-01',root='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010',source=ck,selected_129_review_complete=True,seconds=900,save_interval=25,guardian_local_interval_seconds=15,no_new_geometry_or_command_axis=True,reuse_all_actual_same_scope_CPU_SDK_native_complete_PPO_clock_D0_D7_evidence_exact=True,startup_requires_same_G3_terrain_restored_exact=True,startup_requires_same_retained_command_state_restored_exact=True,saved_source_episode_plus_one=True,no_PhysX_exactresume_claim=True,postsave_frozen_cases_label='130-e1-g3-command-retention-matched',only_one_matched_continuation_then_review=True,new_budget_seconds=0))
 note=R/'COMMAND129_COMPLETE_REPORT.md';assert not note.exists();note.write_text('129四项actualcomplete/errorfree，两host JSON逐字SHA和完整NPZ SHA、全部root30q/参数/recipes/assignments/6000callbacks/ground-contact-integral-COMlink/hardware原容差实际审查。选定源32058与新source364：world62/64→63/64，maxcross.053276684→.051815866m/s，负4π5/8→7/8，正8/8；直行±1.5误差.026857004/.043898690m/s。35mm前完整23/27→24/27，倒保持27/27，ordinary0、closure.661372382mm；env6/21/33有效完整15s前缀未达到两轮200mm后支撑，站立26不要求行进，不把stand complete_envs0称失败。原false和残差保持，未证明长期或因果抗遗忘，非35mm全部通过/E1/RM70mm毕业。下一仅从本ownfullsave继续同geometry和同命令范围900s，省去已通过同scope SDK/native/preflight/clock重复；启动必须实际旧新全组及same command/terrain恢复+一次episode，完整保存后新130四case再审，不自动第三块。\n',encoding='utf8')
 costs=[28.112966537475586,219.33840322494507,222.32168865203857,293.5042884349823,325.1909341812134]
 save('COMMAND_COST_FLOAT_AGGREGATE_RECONCILIATION.json',dict(epoch=time.time(),segments_seconds=costs,segment_duration_sum_seconds=sum(costs),canonical_idle_delta_seconds=320858.98546409607-319770.51718330383,aggregate_difference_seconds=sum(costs)-(320858.98546409607-319770.51718330383),difference_is_sub_microsecond_floating_accumulation=True,no_ledger_write_or_reaccount=True))
 files={'E1_G3_COMMAND_RETENTION_129_COMPLETE_ACTUAL_REVIEW.json':review,'E1_G3_COMMAND_RETENTION_129_SELECTED_SOURCE_MATCHED_REVIEW.json':selected,'E1_G3_COMMAND_RETENTION_129_COMPLETE_RETENTION_DECISION.json':decision,'E1_G3_COMMAND_RETENTION_129_COMPLETE_REPORT.md':note,'NEXT_E1_G3_COMMAND_RETENTION_MATCHED_CONTINUATION_WORK_ORDER.json':work}
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   for n,p in files.items():
    raw=p.read_bytes()
    with f.open(E+'/reports/'+n,'wbx') as out:out.write(raw)
    assert f.open(E+'/reports/'+n).read()==raw
  code=r'''from pathlib import Path
import hashlib,json,time,os
R=Path(REPORTS);B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
budget=B.read_bytes();ledger=json.loads(budget);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);event=v['E1_G3_command_retention_364_execution_event'];assert 'behavior129_complete' not in event
event['behavior129_complete']=dict(epoch=time.time(),actual_review=str(R/'E1_G3_COMMAND_RETENTION_129_COMPLETE_ACTUAL_REVIEW.json'),selected_comparison=str(R/'E1_G3_COMMAND_RETENTION_129_SELECTED_SOURCE_MATCHED_REVIEW.json'),decision=str(R/'E1_G3_COMMAND_RETENTION_129_COMPLETE_RETENTION_DECISION.json'),next_work_order=str(R/'NEXT_E1_G3_COMMAND_RETENTION_MATCHED_CONTINUATION_WORK_ORDER.json'),next_only_same_scope900s=True,no_permanent_anti_forgetting_proof=True,no_50mm_admission=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.Command129-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='E1 source364 actual129 complete matched decision20261010:';assert marker.encode() not in old
msg=chr(10)*2+marker+' Read new129complete fullraw contact/hardware/initial30q and selected32058review. world62to63of64/negative4pi5to7of8/positive8of8; forward23to24of27 and reverse27of27,ordinary0. Three forward incompleteprefixes6/21/33 and originalfalse/residuals retained. One900s SAME35mm and SAMEconditionedcommand continuation from actualown3c97SHA admitted only after ownfullsave/actualexit/two real locks/uniqueactiveempty. Reuse complete same-scope contracts, noSDK/native/PPOpreflight/clock replay, fullsame command+G3terrain restore actualstartup thenepisode+1.130fourcases afterownfullsave, noautomaticthirdblock or50mm/permanentanti-forgetting/E1/RMgraduation. Allreports including later130/sync/monitor Git supplement required.'+chr(10)
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.Command129-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),complete129_decision_synced=True,canonical_master_approval_tracks_RM_bytes_preserved=True,current_before_SHA=H(before),current_after_SHA=H(raw),new_budget_seconds=0)))
'''.replace('REPORTS',repr(E+'/reports'))
  compile(code,'<complete129metadata>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);v['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];p=save('COMMAND129_COMPLETE_METADATA_SYNCED.json',v)
  with c.open_sftp() as f:
   raw=p.read_bytes()
   with f.open(E+'/reports/E1_G3_COMMAND_RETENTION_129_COMPLETE_METADATA_SYNCED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_COMMAND_RETENTION_129_COMPLETE_METADATA_SYNCED.json').read()==raw
  print(json.dumps(dict(complete129_synced=True,next_only_same_scope900s=True,new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  save('COMMAND129_COMPLETE_FINALIZE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_completed_metadata_transactions=True));raise
