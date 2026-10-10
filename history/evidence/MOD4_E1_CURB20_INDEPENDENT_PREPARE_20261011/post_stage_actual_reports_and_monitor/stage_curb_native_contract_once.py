"""Stage a new isolated CURB contract root, never a PPO learner or old entry."""
from curb_io import *
import shlex,traceback
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_INDEPENDENT_20261011'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def main():
    review_path=sorted(R.glob('CURB132_REVIEW_[0-9]*.json'))[-1]
    review=json.loads(review_path.read_bytes());assert review['review_complete'] and not review['pending']
    save('CURB_NATIVE_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='E1-CURB20-INDEPENDENT-NATIVE-DEPLOY-01',once=True,CPU_staging_no_PPO=True))
    additions={'isaac/mod4/'+name:D/'implementation'/name for name in ('curb20_geometry.py','curb20_profile.json','curb20_current_state.py','curb20_retention_runtime.py')}
    additions.update({name:D/'implementation'/name for name in ('native_e1_curbscope_probe.py','supervise_curb_native_scope_once.py')})
    n,w=connect_both()
    try:
        authority=boundary(n)
        copy=linux_json(n,r'''from pathlib import Path
import json,hashlib,shutil
old=Path(OLD_ROOT);new=Path(NEW_ROOT);B=Path(BUDGET);budget=B.read_bytes();assert not new.exists()
f=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes());assert len(f['sha256'])==366
new.mkdir();(new/'reports').mkdir()
for name,h in f['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
assert B.read_bytes()==budget
print(json.dumps(dict(epoch=__import__('time').time(),old366_source_bytes_preserved=True,new_root=str(new),native_only_no_PPO=True,old_freeze=f)))
'''.replace('OLD_ROOT',repr(OLD)).replace('NEW_ROOT',repr(NEW)).replace('BUDGET',repr(B)))
        freeze=dict(copy['old_freeze']);hashes=dict(freeze['sha256'])
        with n.open_sftp() as f:
            for name,p in additions.items():
                raw=p.read_bytes();assert name not in hashes
                with f.open(NEW+'/'+name,'wbx') as out:out.write(raw)
                assert f.open(NEW+'/'+name).read()==raw;hashes[name]=H(raw)
            freeze.update(candidate_root=NEW,sha256=hashes,independent_expert='E1_CURB',genuinely_new_geometry_contract=True,
                original366_all_bytes_preserved=True,no_PPO_learning_controller_deployed=True)
            source=json.loads((W/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010/reports/COMMAND129_COMPLETE_RETENTION_DECISION.json').read_bytes())['selected_next_source']
            assert source['sha256']==SHA
            evidence={'SOURCE_FREEZE.json':json.dumps(freeze,indent=2).encode(),
                'SOURCE_SELECTED.json':json.dumps(source,indent=2).encode(),
                'CURB132_COMPLETE_ACTUAL_REVIEW.json':review_path.read_bytes(),
                'CURB_NATIVE_SCOPE_PREPARED.json':(R/'CURB_NATIVE_SCOPE_PREPARED.json').read_bytes(),
                'NEXT_CURB20_WORK_ORDER.md':(R/'NEXT_CURB20_FROZEN_AND_INDEPENDENT_LEARNING_WORK_ORDER.md').read_bytes()}
            for name,raw in evidence.items():
                with f.open(NEW+'/reports/'+name,'wbx') as out:out.write(raw)
                assert f.open(NEW+'/reports/'+name).read()==raw
            with f.open(E+'/reports/E1_CURB20_132_COMPLETE_ACTUAL_REVIEW.json','wbx') as out:out.write(review_path.read_bytes())
            assert f.open(E+'/reports/E1_CURB20_132_COMPLETE_ACTUAL_REVIEW.json').read()==review_path.read_bytes()
        save('CURB_NATIVE_SOURCE_FREEZE.json',freeze)
        code=r'''from pathlib import Path
import sys,torch,json,hashlib,time
D=Path(NEW_ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb_native_scope_once as own
own.verify();source=json.loads((D/'reports/SOURCE_SELECTED.json').read_bytes());p=Path(source['path']);assert own.H(p)==own.SHA
info=own.inherited.fullsave(p);ck=torch.load(p,map_location='cpu',weights_only=False)
assert info['finite_tensors']==102 and not torch.cuda.is_initialized()
from curb20_geometry import make_mesh
from curb20_current_state import PROFILE
for mirror in (False,True):
 mesh,origin=make_mesh((9.,9.),mirror);assert len(mesh.faces)==8
assert ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1'
assert ck['E1_retained_flat_command_state']['assignment_sha256'] and ck['E1_retained_flat_command_state']['rng_device_type']=='cuda'
print(json.dumps(dict(epoch=time.time(),passed=True,target_CPU_only=True,no_CUDA_initialized=True,source_fullsave=info,source_SHA=own.SHA,source_bytes=p.stat().st_size,source_count=len(json.loads((D/'reports/SOURCE_FREEZE.json').read_bytes())['sha256']),new_Curb_geometry_CPU_validated=True,new_profile=PROFILE,no_optimizer_or_other_expert_save_target=True,new_Curb_complete_resume_and_assignment_migration_pending=True,SDK_native_pending=True,no_PPO_executor=True)))
'''.replace('NEW_ROOT',repr(NEW))
        compile(code,'<curb-target-cpu>','exec')
        _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read()
        assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');cpu=json.loads(raw)
        p=save('CURB_NATIVE_TARGET_CPU_VERIFIED.json',cpu)
        with n.open_sftp() as f:
            with f.open(NEW+'/reports/CURB_NATIVE_TARGET_CPU_VERIFIED.json','wbx') as out:out.write(p.read_bytes())
            assert f.open(NEW+'/reports/CURB_NATIVE_TARGET_CPU_VERIFIED.json').read()==p.read_bytes()
        save('CURB_NATIVE_STAGED.json',dict(epoch=time.time(),trial_id='E1-CURB20-INDEPENDENT-NATIVE-DEPLOY-01',root=NEW,source_count=len(hashes),additions={name:H(p.read_bytes()) for name,p in additions.items()},
            source_CPU=cpu,old_actual_authority=authority,no_PPO_or_learning_launch_yet=True,canonical_not_mutated=True))
        print(json.dumps(dict(root=NEW,source_count=len(hashes),source_CPU102=True,new_Curb_geometry=True,no_PPO=True)))
    finally:cleanup(n,w)
if __name__=='__main__':
    try:main()
    except Exception:
        save('CURB_NATIVE_STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_partial_retained=True,no_replay_stage_or_GPU_or_budget_transaction=True));raise
