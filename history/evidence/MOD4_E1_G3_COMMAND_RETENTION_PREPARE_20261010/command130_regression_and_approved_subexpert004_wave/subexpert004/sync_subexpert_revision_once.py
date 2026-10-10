"""Deliver the explicitly approved sidecar revision; never replace historical approval."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def main():
 assert not (R/'REVISION_SYNC_STARTED.json').exists()
 a=json.loads((R/'REVISION_APPROVED.json').read_bytes());assert a['approved'] and a['human_authorization']['quote']=='按照我说的修改计划吧，修改完后进行'
 save('REVISION_SYNC_STARTED.json',dict(epoch=time.time(),revision=a['approved_revision_id'],new_training_or_budget=False))
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  names=['MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','REVISION_APPROVED.json']
  with c.open_sftp() as f:
   for n in names:
    b=(R/n).read_bytes();remote='MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json' if n=='REVISION_APPROVED.json' else n
    with f.open(E+'/'+remote,'wbx') as q:q.write(b)
    assert f.open(E+'/'+remote).read()==b
  code=r'''from pathlib import Path
import hashlib,json,os,time
R=Path(REPORTS);B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};budget=B.read_bytes();assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
a=json.loads((R/'MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json').read_bytes());assert a['approved']
assert H((R/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md').read_bytes())==a['approved_revision_md_sha256'];assert H((R/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json').read_bytes())==a['approved_revision_json_sha256']
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);assert 'terrain_subexpert_revision004' not in v
v['terrain_subexpert_revision004']=dict(revision=str(R/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json'),approval=str(R/'MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json'),approved=True,human_quote=a['human_authorization']['quote'],active_next_expert='E1_WAVE',current35mm_first300s_same_scope=True,V3_pure_not_adopted=True,independent_experts=['E0','E1_WAVE','E1_CURB','E1_SLOPE','E1_STAIR'],gate_untrained=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.Subexpert004-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='Human-approved terrain subexpert revision004:';assert marker.encode() not in old
msg='\n\n'+marker+' Read MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json and MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json. Human explicitly requested revise then execute. E0 remains frozen; wave/curb/slope/real-stair have independent full weights and state. First new independent E1_WAVE root from complete129 source3643c97, SAME35mm/SAMEcurrentconditionedcommands/families, only300s loadlearnsaveexit and exactscope reuse, noV3pure or repeated preflight. Full131 terrain and inherited skills after save; inherited flatskills diagnostic, whole-system retention belongs to frozen experts plus later actualhardtop1 routing. No automatic900s/50mm or gate readiness claim. Original130false/regression/365refusal/raw/cost and draft preserved. Other experts require actual own newgeometry contracts, protect original budget/master/hardware/DR/S7/S8. All reports and final receipts Git required.\n'
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.Subexpert004-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),revision004_synced=True,protected_master_approval_tracks_RM_canonical_bytes_unchanged=True,current_before_SHA=H(before),current_after_SHA=H(raw),new_budget_seconds=0)))
'''.replace('REPORTS',repr(E))
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(out+err).decode(errors='replace')
  receipt=json.loads(out);receipt['delivered_files']=[dict(name=n,bytes=(R/n).stat().st_size,sha256=H((R/n).read_bytes())) for n in names];save('REVISION_METADATA_SYNCED.json',receipt);print(json.dumps(receipt))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('REVISION_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_completed_mutations=True));raise
