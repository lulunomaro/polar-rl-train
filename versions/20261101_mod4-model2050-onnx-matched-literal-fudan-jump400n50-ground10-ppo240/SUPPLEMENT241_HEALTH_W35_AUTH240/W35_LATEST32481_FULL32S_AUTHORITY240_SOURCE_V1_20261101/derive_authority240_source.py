"""Independent LOCAL metadata-only adapter;preserve original full32s bytes."""
from pathlib import Path
import ast,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
B=T/'W35_LATEST32481_FULL32S_SAMEUID_EVAL_SOURCE_V1_20261101'
A=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101'
def read(p):return json.loads(Path(p).read_bytes())
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
 assert read(R/'DERIVE_AUTH240_PURPOSE_FROZEN.json')['executions']==1
 assert ref(B/'INDEX_W35_LATEST32481_FULL32S_FROZEN.json')['SHA']=='40ede6a8e9acbf824954df95c3255b60b09e6b8dd6d8fd6f5511125abe787b2c'
 launchpath=A/'reports/ROOT240_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json';statepath=A/'reports/ROOT240_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json';bindingpath=A/'reports/KNOWN_ACTIVE240_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json'
 launch=read(launchpath);state=read(statepath);binding=read(bindingpath)
 assert binding['kind']=='KNOWN_ACTIVE240_EXACT_ORIGINAL_MODEL2050_SOLO_AUTHORITY_BINDING'
 assert launch['run_id']==binding['run_id']=='MODEL2050_LITERAL40050_JUMP240_1793502489321389900' and state['current_owner_matched'] and state['canonical_None'] is False
 assert binding['owner']==launch['owner'] and binding['go']==state['current']['go'] and set(binding['go'])=={'jump_72'}
 assert binding['owner']['pid']==1018842 and binding['owner']['creation']==1793502495.27
 assert binding['go']['jump_72']['source_CPU_SHA']=='50069ee3616fa3a5a7a20f7aa258d8c5f6bba6809150268080c43aa46729836c'
 put(R/'DERIVE_AUTH240_ONCE_CONSUMED.json',dict(epoch=time.time(),source_metadata_only=True))
 unchanged=['evaluate_latest32481_full32s_ROOT_ONLY_once.py','target_latest32_parent_ROOT_ONLY.py','guard_latest32.py','rm70_intervals227.py','positional_rows227.py','decode227_positional.py']
 for name in unchanged:
  with (N/name).open('xb') as f:f.write((B/name).read_bytes())
 s=(B/'contract_latest32.py').read_text(encoding='utf8')
 s=once(s,"KNOWN235_RUN='E2_B3AE_WORLD_MIMIC01_PPO235V4_20261101_0937'",'KNOWN_ACTIVE_RUN='+repr(binding['run_id'])+'\nKNOWN_BINDING_KIND='+repr(binding['kind'])+'\nKNOWN_ROLE=\'jump_72\'\nEXPECTED_OWNER='+repr(binding['owner'])+'\nEXPECTED_GO='+repr(binding['go']))
 start=s.index('def validate_authority(')
 s=s[:start]+'''def validate_authority(c,binding,owner_identity=None,owner_current=None,process_fact=None,closed=None):
 assert c['authority_generation']==GENERATION and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 assert binding['kind']==KNOWN_BINDING_KIND and binding['run_id']==KNOWN_ACTIVE_RUN
 owner=binding['owner']
 for k in ('pid','creation','exe','argv','cwd','root'):assert owner[k]==EXPECTED_OWNER[k],k
 assert owner_identity['pid']==owner['pid'] and owner_identity['creation']==owner['creation']
 # b.ident.root is process cwd;SPAWN.owner.root is its task directory.
 # Use explicit fresh process cwd for comparison,never compare those root labels.
 assert binding['go']==EXPECTED_GO and owner_current['go']==EXPECTED_GO and set(binding['go'])=={KNOWN_ROLE}
 if c['active_segment'] is not None:
  a=c['active_segment'];assert a['owner_parent_pid']==owner['pid'] and process_fact['running']
  for k in ('pid','creation','exe','argv','cwd'):assert process_fact[k]==owner[k],k
  # Original240 charge_values initializes this exact field from full GO.
  assert set(a['experts'])=={KNOWN_ROLE} and a['experts'][KNOWN_ROLE]['started_epoch']==EXPECTED_GO[KNOWN_ROLE]['learning_started_epoch']
  return dict(mode='FRESH_EXACT240_ACTIVE',active_GPU_UUID=binding['go'][KNOWN_ROLE]['GPU_UUID'],run_id=binding['run_id'],owner=owner)
 assert closed and closed['cohort_final']['go']==EXPECTED_GO and closed['cohort_final']['original_cost_settled'] and closed['owner_exit']['original_cost_settled'] and closed['owner_exit']['own_original_two_fcntl_released_if_held']
 assert not process_fact['running'] and set(closed['cohort_final']['rows'])=={KNOWN_ROLE} and all(x['terminal_all_own_children_waited'] for x in closed['cohort_final']['rows'].values())
 return dict(mode='FRESH_CNONE_AFTER_MATCHING240_CLOSED',active_GPU_UUID=None,run_id=binding['run_id'],owner=owner)
'''
 write(N/'contract_latest32.py',s)
 s=(B/'make_latest32_Task_SOURCE_ONLY.py').read_text(encoding='utf8').replace('KNOWN235_RUN','KNOWN_ACTIVE_RUN')
 s=once(s,"binding['kind']=='KNOWN_ACTIVE235_EXACT_ORIGINAL_E2_SOLO_AUTHORITY_BINDING'", "binding['kind']==KNOWN_BINDING_KIND")
 write(N/'make_latest32_Task_SOURCE_ONLY.py',s)
 s=(B/'run_ROOT_latest32481_full32s_once.py').read_text(encoding='utf8').replace('KNOWN235_RUN','KNOWN_ACTIVE_RUN')
 s=once(s,"INDEX='INDEX_W35_LATEST32481_FULL32S_FROZEN.json'", "INDEX='INDEX_W35_LATEST32481_AUTH240_FROZEN.json'")
 s=once(s,"R/'CPU_LATEST32_NEW_INTERFACE_ACTUAL.json'", "R/'CPU_AUTH240_NEW_JSON_INTERFACE_ACTUAL.json'")
 s=once(s,'ROOT_LATEST32_FRESH72_EXACT235_OR_CLOSED_CNONE_THEN_CLOSE72.json','ROOT_LATEST32_FRESH72_EXACT240_OR_CLOSED_CNONE_THEN_CLOSE72.json')
 write(N/'run_ROOT_latest32481_full32s_once.py',s)
 put(R/'AUTH240_EXACT_SAVED_METADATA_AND_SOURCE_BINDINGS.json',dict(epoch=time.time(),base_INDEX=ref(B/'INDEX_W35_LATEST32481_FULL32S_FROZEN.json'),
  actual_launch=ref(launchpath),actual_FIRST_state=ref(statepath),actual_binding=ref(bindingpath),
  actual_original_accounting_source=ref(A/'control240/three_slot_common_v1.py'),
  actual_owner_pid=binding['owner']['pid'],actual_owner_creation=binding['owner']['creation'],actual_run=binding['run_id'],actual_role='jump_72',
  fullGO_source_CPU_SHA_scope='Whole Ready VALUE SHA50069...,not model fullCPU5ec90...',
  actual_b_ident_root_scope='psutil cwd;SPAWN owner.root=task directory',
  unchanged_byte_files=[ref(N/x) for x in unchanged],changed_only=['contract authority constants/validator','Taskbuilder binding kind/run join','caller current authority fact label/newCPU/selfINDEX'],
  current_authority_not_claimed_from_snapshot=True,actual_remote_or_model_or_SDK_or_Git=0,old_fixture_replays=0))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'DERIVE_AUTH240_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
