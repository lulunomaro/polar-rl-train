"""Independent CPU PPO proof: wholecore+ownedBODY, actor/Adam andactualsource14restore."""
from pathlib import Path
import json,sys,time,hashlib,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=D/'payload_v1';B=W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014';sys.path.insert(0,str(P))
from bodyframe_original_CPU_guard import logical_fullsave,same
from birth_bodyframe_state_v1 import KEY,validate
from birth_bodyframe_full_checkpoint_v5 import bindings_from_checkpoint
from left_sameidentity_typed13_receipts import REQUIRED_BOOLEAN_SCHEMA,validate_set
def read(p):return json.loads(Path(p).read_bytes())
def main():
 collection=Path(sys.argv[1]);v=read(collection);rows=v['two_host_byteSHA_exact'];assert not v['actual_positive_saved_pending'] and all(x['two_host_byteSHA_exact'] for x in rows)
 for row in rows:assert Path(row['local_path']).stat().st_size==row['bytes'] and hashlib.sha256(Path(row['local_path']).read_bytes()).hexdigest()==row['sha256']
 weight=rows[0];ck=torch.load(weight['local_path'],map_location='cpu',weights_only=False);source=read(B/'reports/BODYFRAME_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json')['own_checkpoint'];old=torch.load(source['path'],map_location='cpu',weights_only=False)
 assert source['sha256']=='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139' and hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256']
 core={k:x for k,x in ck.items() if k not in (KEY,'E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE')};info=logical_fullsave(core);validate(ck[KEY],bindings_from_checkpoint(ck));assert torch.equal(ck[KEY]['bound_episode'],ck['E1_terrain_state']['episode'])
 assert same(old['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'],ck['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'])
 delta=[float(ck['optimizer_state_dict']['state'][i]['step'])-float(old['optimizer_state_dict']['state'][i]['step']) for i in range(17)];assert len(set(delta))==1 and delta[0]>0 and delta[0]%20==0
 updates=int(delta[0]/20);changed=[k for k,x in ck['actor_state_dict'].items() if not torch.equal(x,old['actor_state_dict'][k])];assert len(changed)==9
 controls=updates*24;assert ck[KEY]['completed_controls']-old[KEY]['completed_controls']==controls
 marker={Path(x['local_path']).name:Path(x['local_path']) for x in rows if Path(x['local_path']).name.endswith('STARTUP_VERIFIED.json')};assert len(marker)==14
 body=read(marker['BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json']);pid=body['pid'];typed=validate_set([marker[k] for k in REQUIRED_BOOLEAN_SCHEMA],pid,source['sha256'])
 assert body['passed'] and body['actual_GPU_fullrestore_passed'] and not body['CPU_fixture_only'] and body['source_sha256']==source['sha256'] and body['predecessor_bodyframe_state_present'] and not body['first_declared_new_entry_and_BODYdirection'] and body['source_episode_plus_one'] and body['no_initializer_repeat_or_new_RNG'] and body['own_bodyframe_predecessor_and_newbirth_disk_roundtrips']
 mark=ck['E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE'];assert mark['actual_GPU_fullrestore'] and mark['own_pid']==pid and mark['startup_receipt_SHA']==hashlib.sha256(marker['BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json'].read_bytes()).hexdigest()
 m=read(next(x['local_path'] for x in rows if Path(x['local_path']).name=='BODYFRAME_TARGET_ACTUAL_MANIFEST.json'));freeze=next(x for x in rows if Path(x['local_path']).name=='BODYFRAME_SOURCE_FREEZE.json');assert m['sourcefreeze_SHA']==freeze['sha256'] and m['same_declared_BODY_profile_continuation'] and not m['new_axis_initializer_requested']
 assert not torch.cuda.is_initialized();out=R/('SECOND_BODY_OWN_POSITIVE_WEIGHT_LOCAL_CPU_VERIFIED_'+str(time.time_ns())+'.json');value=dict(epoch=time.time(),passed=True,source=source,own_weight=weight,core=info,owned_BODY_CPU_verified=True,body_state_controls_delta_exact=True,updates=updates,controls=controls,envsteps=controls*20000,callbacks=controls*4,actor_changed=changed,all17_Adam_delta=delta[0],typed13=typed,body14_actual_same_profile_restore=True,source_episode_plus_one=True,initializer_not_repeated=True,sourcefreeze_manifest_bound=True,no_CUDA_or_PPO_in_observer=True,active_save_not_formal_final_or_50mm_improvement=True,qualified50=False,full_final_trace_cost_exit_and_new_fourcase_review_required=True);out.write_text(json.dumps(value,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),passed=True,weight_SHA=weight['sha256'],updates=updates,envsteps=controls*20000,actor_changed=9,Adam_delta=delta[0])))
if __name__=='__main__':main()
