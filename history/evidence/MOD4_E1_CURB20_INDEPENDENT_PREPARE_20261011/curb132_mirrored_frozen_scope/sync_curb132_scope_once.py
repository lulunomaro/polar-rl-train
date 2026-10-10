"""New CURB132 deployment annotation only; protected runtime and ledger unchanged."""
from curb_io import *
import traceback
def main():
    save('CURB132_SCOPE_SYNC_STARTED.json',dict(epoch=time.time(),trial_id='E1-CURB20-132-SCOPE-METADATA-01',once=True,metadata_only=True))
    publication=json.loads((R/'CURB132_PUBLISHED.json').read_bytes());assert publication['canonical_bytes_preserved']
    files={'E1_CURB20_132_FROZEN_PREPARED.json':R/'CURB_FROZEN_PREPARED.json',
        'E1_CURB20_132_FROZEN_PUBLISHED.json':R/'CURB132_PUBLISHED.json',
        'NEXT_E1_CURB20_FROZEN_AND_INDEPENDENT_LEARNING_WORK_ORDER.md':R/'NEXT_CURB20_FROZEN_AND_INDEPENDENT_LEARNING_WORK_ORDER.md'}
    n,w=connect_both()
    try:
        authority=boundary(n)
        with n.open_sftp() as f:
            for name,p in files.items():
                b=p.read_bytes()
                with f.open(E+'/reports/'+name,'wbx') as out:out.write(b)
                assert f.open(E+'/reports/'+name).read()==b
        receipt=linux_json(n,r'''from pathlib import Path
import hashlib,json,os,time
R=Path(CENTRAL)/'reports';B=Path(BUDGET);H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};budget=B.read_bytes()
assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
l=json.loads(budget);assert l['active_segment'] is None and l['authorized_training_seconds']==828000
pub=json.loads((R/'E1_CURB20_132_FROZEN_PUBLISHED.json').read_bytes());job=pub['jobs'][0]
cp=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=cp.read_bytes();v=json.loads(before);a=v['terrain_subexpert_revision004'];assert a['approved'] and 'curb132_frozen_scope' not in a
assert a['wave131_behavior_complete']['qualified_wave_expert'] is False
a['curb132_frozen_scope']=dict(epoch=time.time(),expert='E1_CURB',job_id=job['job_id'],package_SHA=job['artifacts']['runtime']['sha256'],checkpoint_SHA=job['artifacts']['checkpoint']['sha256'],actual_published=True,frozen_only=True,actual_complete_pending=True,independent_CURB_PPO_not_launched=True,next_work_order=str(R/'NEXT_E1_CURB20_FROZEN_AND_INDEPENDENT_LEARNING_WORK_ORDER.md'),current_priority='Read actual132 fullraw then admit genuinely new isolatedCURB contracts',new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert cp.read_bytes()==before;tmp=cp.with_name(cp.name+'.CURB132-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,cp)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='Approved004 independentCURB132 actual frozen scope published:';assert marker.encode() not in old
msg='\n\n'+marker+' New20mmverticalriser/150mmstripcontinuousupperplatform/40original40mirrored realtiles;80env1500controls15s20260928white3/source3643c97/283manifestSHAexact. Onlynewgeometry+frozenroute; actualtwo-wheel starts/fullcurbstrip/200mmrear support/contact/fullraw requirecompleteerrorfree132 review. Healthy3060worker unchanged; no4090PPO/ledgerwrite. Wave131 forward22 reverse25of27/7validincompleteprefixes retained,2b4 notqualified or selectedwarmstart. Read E1_CURB20_132_FROZEN_PREPARED/PUBLISHED and new NEXT_E1_CURB20_FROZEN_AND_INDEPENDENT_LEARNING_WORK_ORDER. Afteractualreasonablecomplete progressnewisolatedCURB fullrestore with explicitoldassignment/privateRNG validation thennewgeometryrebind/CUDAepisode1/newSDK/native/fullPPOonce/300sformal, noblindhold or oldcomplete replay. PreserveE0/Wave/master/reward/LR/DR/hardware/clock/canonical828000/sixextensions. AllnewreportsGit.\n'
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.CURB132-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),curb132_scope_synced=True,current_scope_frozen_only=True,independent_CURB_PPO_not_launched=True,protected_master_approval_tracks_RM_canonical_bytes_preserved=True,new_budget_seconds=0)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)))
        receipt['actual_authority']=authority
        receipt['files']=[dict(name=name,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for name,p in files.items()]
        p=save('CURB132_SCOPE_METADATA_SYNCED.json',receipt)
        with n.open_sftp() as f:
            with f.open(E+'/reports/E1_CURB20_132_SCOPE_METADATA_SYNCED.json','wbx') as out:out.write(p.read_bytes())
            assert f.open(E+'/reports/E1_CURB20_132_SCOPE_METADATA_SYNCED.json').read()==p.read_bytes()
        print(json.dumps(dict(synced=True,curb132_frozen_only=True,master_canonical_bytes_preserved=True)))
    finally:cleanup(n,w)
if __name__=='__main__':
    try:main()
    except Exception:
        save('CURB132_SCOPE_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_partial_retained=True,no_replay_executed_mutations=True));raise
