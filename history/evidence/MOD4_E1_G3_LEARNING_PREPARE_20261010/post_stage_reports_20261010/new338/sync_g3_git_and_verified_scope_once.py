"""Publish new stage Git proof and genuine native/preflight progress, no relaunch."""
from pathlib import Path
import hashlib,json,os,sys,subprocess,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json';TAG='trial-20261010-e1-reviewed-35mm-full-contract-scope-and-short-observation-deployed'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def main():
 save('GIT_SCOPE_SYNC_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-GIT-SCOPE-SYNC-02',once=True))
 commit=git('rev-parse',TAG+'^{}');obj=git('rev-parse',TAG);remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines());assert remote['refs/heads/main']==git('rev-parse','HEAD') and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==commit
 idx=P/'history/evidence/MOD4_E1_G3_LEARNING_PREPARE_20261010/REPORT_CAPTURE_INDEX.json';v=json.loads(idx.read_bytes());tracked=set(git('ls-tree','-r','--name-only',commit).splitlines());assert all(x['Git_path'] in tracked and H((P/x['Git_path']).read_bytes())==x['archived_sha256'] for x in v['reports_and_implementation'])
 proof=dict(epoch=time.time(),tag=TAG,commit=commit,tagobject=obj,remote_main=remote['refs/heads/main'],remote_main_tag_peeled_verified=True,push_pending=False,reports_captured=len(v['reports_and_implementation']),large_indices=len(v['large_originals_index_only']),prior_references=len(v['prior_identical_reports_reused']),archive_tracked_and_SHA_verified=True,post_stage_reports_and_current_reader_pending_fix_require_supplement=True,no_new_training_or_budget_authority=True);save('GIT_RECORDED.json',proof)
 latest=sorted(R.glob('G3_ACTUAL_*.json'))[-1];a=json.loads(latest.read_bytes());assert not a['reports'].get('E1_ATTENTION.json');rows={}
 for n,count,steps,total in (('G3_ACTUAL_SDK.json',10,300,1200),('G3_NATIVE20K.json',20000,120,576)):
  x=a['native'][n]['summary'];assert x['PPO_update_count']==0 and x['num_envs']==count and x['timed_control_steps']==steps and x['physical_callback_count']==steps*4 and x['health']['actual_physics_callbacks']==total and x['E1_actual_ground_error_m']==x['E1_height_reward_formula_error']==0 and not x['nonfinite'] and x['actual_task_failed_environments']==0
  rows[n]=dict(original_report=a['native'][n]['original_report'],num_envs=count,control_steps=steps,warmup=x['warmup_control_steps'],timed_callbacks=x['physical_callback_count'],total_callbacks=x['health']['actual_physics_callbacks'],ground_and_height_formula_error0=True,closure_mm=x['max_closure_error_m']*1000,ordinary_terminated_envs=0,nonfinite=False,no_PPO=True,actual_35mm_identity=x['E1_terrain_identity'])
 small=a['reports']['g3_discard128_PASSED.json'];assert small['actual_updates']==2 and small['actual_environment_steps']==6144 and len(small['unique_completed_segment'])==1 and small['discarded_preflight']
 active=a['canonical']['active_segment'];tail=max(0,a['epoch']-active['accounted_through_epoch']) if active else 0
 summary=dict(epoch=time.time(),actual_snapshot=dict(path=str(latest.resolve()),bytes=latest.stat().st_size,sha256=H(latest.read_bytes())),native=rows,discard128=dict(checkpoint=small['checkpoint'],updates=2,environment_steps=6144,callbacks=small['health']['actual_physics_callbacks'],unique_completed_segment=small['unique_completed_segment'],weights_discarded=True),current_phase=a['reports']['E1_STATE.json']['phase'],actual_processes=a['actual'],canonical_authorized=a['canonical']['authorized'],canonical_snapshot_remaining=a['canonical']['remaining'],unaccounted_tail_at_snapshot=tail,remaining_after_snapshot_tail=a['canonical']['remaining']-tail,big20k_and_formal_own_receipts_take_precedence=True,formal_fullsave_and127_behavior_pending=True,new_budget_seconds=0,not_35mm_graduation_or_permanent_anti_forgetting=True);save('NATIVE_AND_PREFLIGHT_ACTUAL_VERIFIED.json',summary)
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  files={'E1_G3_FULL_CONTRACT_GIT_RECORDED.json':R/'GIT_RECORDED.json','E1_G3_SCOPE_NATIVE_AND_PREFLIGHT_CURRENT_ACTUAL.json':latest,'E1_G3_SCOPE_NATIVE_AND_PREFLIGHT_ACTUAL_VERIFIED.json':R/'NATIVE_AND_PREFLIGHT_ACTUAL_VERIFIED.json'}
  with c.open_sftp() as f:
   for n,p in files.items():
    b=p.read_bytes()
    with f.open(E+'/reports/'+n,'wbx') as o:o.write(b)
    assert f.open(E+'/reports/'+n).read()==b
  code=r'''from pathlib import Path
import json,hashlib,time,os
R=Path(REPORTS_VALUE);B=Path(BUDGET_VALUE);j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b' and j(B)['authorized_training_seconds']==828000
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);event=v['E1_G3_short_observation_execution_event'];event.update(stage_Git_recorded=str(R/'E1_G3_FULL_CONTRACT_GIT_RECORDED.json'),native_and_preflight_verified=str(R/'E1_G3_SCOPE_NATIVE_AND_PREFLIGHT_ACTUAL_VERIFIED.json'),current_scope_actual=str(R/'E1_G3_SCOPE_NATIVE_AND_PREFLIGHT_CURRENT_ACTUAL.json'),actual_first_newscope_SDK_native_completed=True,discard128_complete_weights_discarded=True,big20k_and_formal_own_receipts_take_precedence=True,no_auto_more_PPO_without_actual127_complete_review=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.G3GitScope-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';hb=hp.read_bytes();marker='E1 G3 Git scope and new native actual verified20261010:';assert marker.encode() not in hb
text=chr(10)*2+marker+' New annotated trial-20261010-e1-reviewed-35mm-full-contract-scope-and-short-observation-deployed commit66b327e5651152b4fb42b7e47c0aca40d8ffe47e/tagobject76669fb91d68789406f4b13cc2e289d98686d6a8 remote main/tag/peeled/55report archiveSHA/2largeindices/60priorreferences verified. Actualnew35mm10env300control1200callbacks/20k24warm+120timed480callbacks576total, noPPO/task0/nonfinitefalse/ground0/heightformula0/solver32-4, closure.600281695/1.705825329mm. This is scope contract, not full35mm route or learning graduation. Discard1282updates6144envsteps unique28.120006s weightsdiscarded. Latest ownbig20k/preflight/formal/fullsave receipts take precedence; no replay oldstage/main/resume/nativeSDK/PPO. Formalsource32058/newG2toG3 fullresume/newphysicalepisode; no morePPO after single300s without actual127 matched review. Original125/LFCRLF refusals retained. Newcurrent/sync/reader pending fix and laterfinal127 reports require supplement Git; credentials excluded and large originals indexed. Actualcanonicalnormalactiveaccounts total828000/new0, no metadata budget write; master/RM/S8/gate/hardware/pause93-94/MuJoCo ended unchanged.'+chr(10)
assert hp.read_bytes()==hb;tmp=hp.with_name(hp.name+'.G3GitScope-'+str(time.time_ns()));tmp.write_bytes(hb+text.encode());os.replace(tmp,hp)
assert all((R/n).read_bytes()==b for n,b in protected.items()) and j(B)['authorized_training_seconds']==828000
print(json.dumps(dict(epoch=time.time(),Git_native_scope_metadata_synced=True,master_approval_tracks_RM_bytes_preserved=True,metadata_only_no_PPO_or_budget_write=True,canonical_normal_accounting_left_to_original_parent=True,current_before_SHA=H(before),current_after_SHA=H(raw),new_budget_seconds=0)))
'''.replace('REPORTS_VALUE',repr(E+'/reports')).replace('BUDGET_VALUE',repr(B))
  compile(code,'<G3GitScope>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(out+err).decode(errors='replace');done=json.loads(out);done['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];save('GIT_SCOPE_METADATA_SYNCED.json',done)
  with c.open_sftp() as f:
   b=(R/'GIT_SCOPE_METADATA_SYNCED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_FULL_CONTRACT_GIT_SCOPE_METADATA_SYNCED.json','wbx') as o:o.write(b)
   assert f.open(E+'/reports/E1_G3_FULL_CONTRACT_GIT_SCOPE_METADATA_SYNCED.json').read()==b
  print(json.dumps(dict(stage_Git_metadata_synced=True,new_native_scope_verified=True,formal_and127_pending=True,new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('GIT_SCOPE_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_repeat=True));raise
