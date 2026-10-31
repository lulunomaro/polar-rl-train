"""New immutable caller/control manifests after original219 pre-GO role refusal."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
closed=read(R/'ROOT219_PRE_GO_ROLE_REFUSAL_ORIGINAL_EXIT_ACTUAL.json')
assert closed['passed']and closed['empty_GO']and closed['canonical_None']and closed['private_EX_free']
assert closed['original_owner_out']and closed['original_node_out']
control=read(R/'CONTROL219_FROZEN_MANIFEST.json')
old=next(r for r in control['files']if r['relative']=='forwarded_original_owner_control_v1.py')
new=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/control_v2/forwarded_original_owner_control_v1.py'
before=Path(old['local_path']).read_text('utf8');after=new.read_text('utf8')
needle="('h1','h1_210','e2','h1_seed28','e0_72')"
assert before.count(needle)==1 and before.replace(needle,"('h1','h1_210','e2','h1_seed28','e0_72','w35_72')")==after
replacement=dict(relative=old['relative'],local_path=str(new),bytes=new.stat().st_size,SHA=H(new))
control['files']=[replacement if r is old else r for r in control['files']]
control['source_repair']='Actual210v2 exact sender already supports authorized W35 role; HMAC/body/route/port code otherwise identical'
put('CONTROL219V3_FROZEN_MANIFEST.json',control)
install=read(R/'INSTALL219_SOURCE_ROWS_FROZEN.json')
copy=read(R/'ROOT219_SOURCE_ASSET_POSTCOPY_AND_SINGLE_W35_INPUT_COPY_ACTUAL.json')['input']
assert copy['passed']and copy['bytes']==17619013 and copy['SHA']==install['source_model']['SHA']
old_source=install['source_model']['original_target_path']
install['source_model']['original_target_path']=copy['new_copy']
install['staged_source_reuse']=dict(original_qualified_W35_path=old_source,
 selected_source_copy=copy,reason='First219 failed before GO/SDK/model decode. Reuse its producer-verified staged copy, never reread original frozen W35 for another CPU review.',
 new_staged_copy_streams=1,new_original_frozen_W35_byte_streams=0,new_GPU_decode_required=1)
put('INSTALL219V3_SOURCE_ROWS_FROZEN.json',install)
base=N/'launch219V2_install_original_solo_W35_FIRST_UNUSED_once.py'
assert H(base)=='55804fde9c40448a8b3af0f90aa08ffa3766be5009cbecff075d694b01980dfb'
s=base.read_text('utf8').replace("'launch219V2_|launch219_|","'launch219V3_|launch219V2_|launch219_|")
s=s.replace("R/'INSTALL219_SOURCE_ROWS_FROZEN.json'","R/'INSTALL219V3_SOURCE_ROWS_FROZEN.json'")
s=s.replace("R/'CONTROL219_FROZEN_MANIFEST.json'","R/'CONTROL219V3_FROZEN_MANIFEST.json'")
s=s.replace('ROOT219_','ROOT219V3_')
anchor="e0=load_closed_e0(args.closing,args.new_e0_cpu)"
s=s.replace(anchor,"prior=read(R/'ROOT219_PRE_GO_ROLE_REFUSAL_ORIGINAL_EXIT_ACTUAL.json');assert prior['passed']and prior['empty_GO']and prior['original_owner_out']and prior['original_node_out']\n "+anchor)
# This alias is metadata about the new stream, not another original-source read.
s=s.replace('necessary_old_W35_input_streamcopy=1','necessary_staged_W35_copy_streamcopy=1,original_frozen_W35_input_streamcopy=0')
ast.parse(s)
launch=N/'launch219V3_install_original_solo_W35_FIRST_UNUSED_once.py'
with launch.open('x',encoding='utf8',newline='')as f:f.write(s)
derivations=[]
for name in ('collect219_original_W35_formal_cost_normal900_UNUSED_once.py','review219_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py'):
 source=N/name;text=source.read_text('utf8').replace('ROOT219_','ROOT219V3_')
 text=text.replace('collect219_original_','collect219V3_original_').replace('review219_NEW_','review219V3_NEW_')
 dest=N/name.replace('219_','219V3_',1);ast.parse(text)
 with dest.open('x',encoding='utf8',newline='')as f:f.write(text)
 derivations.append(dict(source=str(source),source_SHA=H(source),new=str(dest),SHA=H(dest)))
put('ROOT219V3_FROZEN_BEFORE_USE_SOURCE_REPAIR.json',dict(epoch=time.time(),
 original219_pre_GO_failure_preserved=True,original_GO_count=0,original_model_GPU_reads=0,
 old_sender=old,new_sender=replacement,only_sender_change='Add authorized w35_72 to send allowlist; actual210v2 source reused',
 all_other_HMAC_account_and_task_source_unchanged=True,new_launch=dict(path=str(launch),bytes=launch.stat().st_size,SHA=H(launch)),
 install_manifest_SHA=H(R/'INSTALL219V3_SOURCE_ROWS_FROZEN.json'),control_manifest_SHA=H(R/'CONTROL219V3_FROZEN_MANIFEST.json'),
 new_original_frozen_W35_stream_reads=0,new_staged_copy_streams=1,new_selected_copy_GPU_read_decode=1,
 original219_and_V2_entries_consumed_not_replayed=True,normal_CPU_derivations=derivations,
 source_worker_reward_physics_or_budget_changed=False,model_raw_SDK_GPU_network_calls=0))
print(json.dumps(dict(source_repair=True,launch=str(launch),SHA=H(launch),sender_SHA=H(new),no_runtime_execution=True)))
