"""Actual126 limits and new338 guarded dispatch metadata, preserving all prior receipts."""
from pathlib import Path
import hashlib,json,os,sys,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';G=W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G3_REVIEWED_20261010';B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def main():
 save('METADATA_SYNC_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-DISPATCH-METADATA-01',once=True))
 review=sorted((G/'reports').glob('G3_126_REVIEW_*.json'))[-1];assert json.loads(review.read_bytes())['review_complete']
 assert json.loads((R/'G3_TARGET_CPU_ADMITTED.json').read_bytes())['passed']
 actual=sorted(R.glob('G3_ACTUAL_*.json'))[-1];a=json.loads(actual.read_bytes());assert not a['reports'].get('E1_ATTENTION.json')
 files={'E1_G3_126_COMPLETE_ACTUAL_REVIEW.json':review,'E1_G3_126_PREFIX_DIAGNOSIS.json':G/'reports/G3_126_PREFIX_DIAGNOSIS.json','SELECTED_E1_G3_SHORT_OBSERVATION_SOURCE.json':R/'SELECTED_E1_G3_SOURCE.json','E1_G3_FULL_CONTRACT_TARGET_CPU_ADMITTED.json':R/'G3_TARGET_CPU_ADMITTED.json','E1_G3_FULL_CONTRACT_DISPATCH_ACTUAL.json':R/'G3_DISPATCH_ACTUAL.json','E1_G3_FULL_CONTRACT_CURRENT_ACTUAL.json':actual,'E1_G3_FULL_CONTRACT_SHORT_OBSERVATION_REPORT.md':D/'REPORT.md','NEXT_G3_SHORT_OBSERVATION_REVIEW_WORK_ORDER.md':D/'NEXT_G3_SHORT_OBSERVATION_REVIEW_WORK_ORDER.md'}
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   for n,p in files.items():
    b=p.read_bytes()
    with f.open(E+'/reports/'+n,'wbx') as o:o.write(b)
    assert f.open(E+'/reports/'+n).read()==b
  code=r'''from pathlib import Path
import json,hashlib,time,os
R=Path(REPORTS_VALUE);D=Path(ROOT_VALUE);B=Path(BUDGET_VALUE);j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json'):assert b'MOD4-RM-TERRAIN-CURRICULUM-REVISION-003' in protected[n] and b'MOD4-RM-OUTER-CURB-AND-ROUGH-GEOMETRY-CLARIFICATION-002' in protected[n]
assert j(B)['authorized_training_seconds']==828000
state=j(D/'reports/E1_STATE.json');assert (D/'reports/E1_DISPATCH_STARTED.json').exists();freeze=j(D/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==338 and all(H((D/n).read_bytes())==h for n,h in freeze.items())
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);scope=v['next_E1_G3_frozen_scope'];scope.update(actual_result_pending=False,actual_independent_CPU_review_pending=False,actual_review=str(R/'E1_G3_126_COMPLETE_ACTUAL_REVIEW.json'),partial_route_diagnosis=str(R/'E1_G3_126_PREFIX_DIAGNOSIS.json'),full35mm_graduation=False,new_isolated338_executor=str(D))
v['actual_phase']=state['phase'];v['E1_G3_short_observation_execution_event']=dict(epoch=time.time(),root=str(D),source_count=338,selected_complete32058_source=str(R/'SELECTED_E1_G3_SHORT_OBSERVATION_SOURCE.json'),actual126_complete_review=str(R/'E1_G3_126_COMPLETE_ACTUAL_REVIEW.json'),partial_after_support_forward17of27_reverse25of27=True,no35mm_graduation=True,current_actual=str(R/'E1_G3_FULL_CONTRACT_CURRENT_ACTUAL.json'),targetCPU=str(R/'E1_G3_FULL_CONTRACT_TARGET_CPU_ADMITTED.json'),report=str(R/'E1_G3_FULL_CONTRACT_SHORT_OBSERVATION_REPORT.md'),next_work_order=str(R/'NEXT_G3_SHORT_OBSERVATION_REVIEW_WORK_ORDER.md'),first_observation_seconds=300,actual_first_newscope_SDK_native_PPO_scope_pending=True,no_auto_more_PPO_without_actual127_complete_review=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.G3dispatch-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';hb=hp.read_bytes();marker='E1 G3 actual126 partial route and338 guarded short observation20261010:';assert marker.encode() not in hb
text=chr(10)*2+marker+' 126 complete/errorfree,2bridgeJSON bytes/182768316byte rawNPZ SHA3c5f40bbdcbb6dad0e8380c20bbd26e24de02c449565032719565527c89b3418 and independent ground/contact/fulldata accepted. ordinary0/closure.650935282mm; fullwave bothwheel exit forward24of27/reverse26of27; including200mm aftersupport whole route17of27/25of27, all incomplete prefix preserved, not35mm graduation. Oldskills complete32058 source selected,32103world49of64 not learning source. Newroot MOD4_S3_E1_G3_REVIEWED_20261010 old330 byteexact plus8/source338; targetTorch2.10 CPU14/CPU96+oldnaturalboundary verified, unique supervise_e1_G3_reviewed_short_observation.py dispatched, ownproc/phase firstnew35mm SDK/native then two discard completePPO and one300s formal, save25/15s localguardian. No clock/samescope test replay, newG2_toG3 geometry restored old groups then actualCUDAroundtrip/new episode1, notsamegeometry/PhysXresume. Automatic127terrain+oldflat/spin/world at ownfullsave then savedreviewready, no automaticmorePPO. Trueactual/proc/run receipt first, missingfuturefilespending. Read newworkorder/currentCPU/actualreview; neverrestartoldonce/main/resume orclearaccount. ActualbudgetnormalPPOaccounts remain sole828000/sixextensions/new0; metadata writes no budget. Original125package/LFCRLF rejections kept. All newstage/final/127/sync reports require Git, weights/raw indexed only; master/RM003002001/S8/gate/hardware/paused93-94/MuJoCo ended unchanged.'+chr(10)
assert hp.read_bytes()==hb;tmp=hp.with_name(hp.name+'.G3dispatch-'+str(time.time_ns()));tmp.write_bytes(hb+text.encode());os.replace(tmp,hp)
assert all((R/n).read_bytes()==b for n,b in protected.items()) and j(B)['authorized_training_seconds']==828000
print(json.dumps(dict(epoch=time.time(),actual_phase=state['phase'],source338_SHA_verified=True,master_approval_tracks_RM_bytes_preserved=True,metadata_only_no_training_launch_or_budget_write=True,canonical_authorized_total828000_unchanged=True,canonical_normal_active_accounting_not_mutated=True,current_before_SHA=H(before),current_after_SHA=H(raw),new_budget_seconds=0)))
'''.replace('REPORTS_VALUE',repr(E+'/reports')).replace('ROOT_VALUE',repr(ROOT)).replace('BUDGET_VALUE',repr(B))
  compile(code,'<G3-dispatch-metadata>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(out+err).decode(errors='replace');proof=json.loads(out);proof['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];save('METADATA_SYNCED.json',proof)
  with c.open_sftp() as f:
   b=(R/'METADATA_SYNCED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_FULL_CONTRACT_METADATA_SYNCED.json','wbx') as o:o.write(b)
   assert f.open(E+'/reports/E1_G3_FULL_CONTRACT_METADATA_SYNCED.json').read()==b
  print(json.dumps(dict(metadata_synced=True,actual_phase=proof['actual_phase'],source338_verified=True,new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('METADATA_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),trial_id='E1-G3-DISPATCH-METADATA-01',do_not_repeat_once=True));raise
