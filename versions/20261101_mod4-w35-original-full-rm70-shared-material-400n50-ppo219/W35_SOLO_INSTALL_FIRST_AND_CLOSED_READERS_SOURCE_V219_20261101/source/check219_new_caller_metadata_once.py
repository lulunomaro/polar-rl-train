"""NEW219 source/closing-schema purpose only; no218 fixture or physical test."""
from pathlib import Path
import ast,copy,hashlib,json,time
from bridge219 import load_closed_e0,E0_CLOSE_SOURCE_SHA
import remote219_payloads as payload
N=Path(__file__).resolve().parent.parent;R=N/'reports';T=N.parent
ID='NEW219_W35_SOLO_INSTALLER_CLOSING_SCHEMA_AND_ORIGINAL_CONTROL_SOURCE_CPU_V1'


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def function(text,name):
 tree=ast.parse(text)
 return next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
def same(a,b,name):assert ast.dump(function(a,name),include_attributes=False)==ast.dump(function(b,name),include_attributes=False),name


def main():
 frozen=json.loads((R/'CPU219_PURPOSE_FROZEN.json').read_bytes())
 assert frozen['purpose_id']==ID and frozen['groups']==3 and frozen['expected_rejections']==9
 assert not (R/'CPU219_ONCE_CONSUMED.json').exists()
 put(R/'CPU219_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose_id=ID,status='STARTED_ONCE_NO_REENTRY',model_or_remote_calls=0))
 for row in frozen['source_files']:
  b=Path(row['path']).read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['SHA']
  if row['path'].endswith('.py'):ast.parse(b.decode('utf8'),filename=row['path'])
 payloads={k:v for k,v in vars(payload).items() if isinstance(v,str) and k.isupper()}
 for name,value in payloads.items():ast.parse(value,filename='UNEXECUTED_TARGET_'+name)
 launch=(N/'launch219_install_original_solo_W35_FIRST_UNUSED_once.py').read_text(encoding='utf8')
 body=launch[launch.index('def main():'):]
 assert body.index('e0=load_closed_e0')<body.index('cim=exact_cim()')<body.index("wrapper=module(")<body.index('client=d.connect72')<body.index('sf.put(')
 assert "client.close();client=None  #Authority control closed" in body
 install=json.loads((R/'INSTALL219_SOURCE_ROWS_FROZEN.json').read_bytes())
 assert len(install['files'])==491 and all(not r['relative'].endswith('.pt') for r in install['files'])
 assert install['source_model']['SHA']=='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
 groups=[dict(group='all_new_source_and_unexecuted_target_payload_AST_first_closure_gate',passed=True,
              target_payloads=len(payloads),source_files=len(frozen['source_files']),asset_PT_reads=0)]
 p210=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031'
 old=(p210/'control/mixed210_finite_owner_authority72.py').read_text(encoding='utf8')
 new=(N/'control219/solo219_finite_owner_authority72.py').read_text(encoding='utf8')
 same(old,new,'account');same(old,new,'Handler')
 oldc=(p210/'control/three_slot_common_v1.py').read_text(encoding='utf8');newc=(N/'control219/three_slot_common_v1.py').read_text(encoding='utf8')
 for name in ['charge_values','authenticated_row','terminal']:same(oldc,newc,name)
 e0close=(p210/'package/run210_mixed_E0_JUMP_worker.py').read_bytes()
 assert hashlib.sha256(e0close).hexdigest()==E0_CLOSE_SOURCE_SHA
 assert "try:real.close()" in e0close.decode('utf8') and "if ns is not None:ns['app'].close()" in e0close.decode('utf8')
 assert "set(specs)=={'w35_72'}" in new and "set(specs)=={'e0_72'}" not in new
 groups.append(dict(group='original_owner_HMAC_account_rawcharge_and_terminal_source_preserved',passed=True,
                    original_control_not_imported_or_executed=True,ledger_reads=0))
 fixture=R/'SYNTHETIC_219_CLOSING_SCHEMA_FIXTURE';fixture.mkdir(exist_ok=False)
 sha='d'*64
 final=dict(SHA=sha,saved_iteration=32067,Adam_min=642860,Adam_max=642860)
 c=dict(synthetic_fixture_only=True,epoch=100,passed_collection=True,
  owner_closed=dict(canonical_None=True,shared_locks_free=True,cohort_final=dict(original_cost_settled=True),owner_exit=dict(original_cost_settled=True)),
  roles=dict(e0_72=dict(qualified_formal=True,private_EX_free=True,errors=[],
   original_node_terminal=dict(row=dict(returncode=0)),original_node_exit=dict(all_own_children_waited=True,private_EX_released=True),
   final=dict(passed=True,actual_new_PPO_updates=1,final=final))),
  formals=dict(e0_72=dict(SHA=sha,transfers=1,two_host_SHA_equal=True,source='/synthetic/E0/production/model_final_complete.pt',path='/synthetic/NEW_E0_model.pt')))
 u=dict(synthetic_fixture_only=True,epoch=101,passed=True,old_model_reads=0,
  roles=dict(e0_72=dict(passed=True,SHA=sha,new_PPO_updates=1,saved_iteration=32067,Adam17_step=642860,
   actor35_critic38_STD6=True,complete_task_and_DR_state_present=True,save_at_or_after_requested_deadline=True)))
 def files(name,a,b):
  x=fixture/(name+'_CLOSING_SYNTHETIC.json');y=fixture/(name+'_CPU_SYNTHETIC.json');put(x,a);put(y,b);return x,y
 x,y=files('positive',c,u);assert load_closed_e0(x,y,synthetic_fixture=True)['formal']['SHA']==sha
 refused=[]
 def refuse(name,call):
  try:call()
  except (ValueError,AssertionError,KeyError,FileNotFoundError):refused.append(name);return
  raise AssertionError('Expected refusal: '+name)
 refuse('missing_closure_before_network',lambda:load_closed_e0(fixture/'missing.json',y))
 cases=[]
 a=copy.deepcopy(c);a['owner_closed']['canonical_None']=False;cases.append(('owner_active',a,u))
 b=copy.deepcopy(u);b['roles']['e0_72']['SHA']='a'*64;cases.append(('CPU_other_artifact',c,b))
 b=copy.deepcopy(u);b['roles']['e0_72']['saved_iteration']=32066;cases.append(('old_CPU_iteration',c,b))
 a=copy.deepcopy(c);a['roles']['e0_72']['original_node_terminal']['row']['returncode']=1;cases.append(('wait_nonzero',a,u))
 a=copy.deepcopy(c);a['roles']['e0_72']['errors']=['ENV_CLOSE_ORIGINAL_ERROR.json'];cases.append(('close_error_not_Appclosed',a,u))
 a=copy.deepcopy(c);a['formals']['e0_72']['path']+='.partial';cases.append(('partial_not_formal',a,u))
 b=copy.deepcopy(u);b['passed']=False;cases.append(('new_CPU_false',c,b))
 for name,a,b in cases:
  xx,yy=files(name,a,b);refuse(name,lambda xx=xx,yy=yy:load_closed_e0(xx,yy,synthetic_fixture=True))
 refuse('synthetic_cannot_qualify_production',lambda:load_closed_e0(x,y))
 assert len(refused)==9
 groups.append(dict(group='new210_actual_closing_schema_bridge_positive_and_before_GO_refusals',passed=True,
                    synthetic_schema_only=True,rejected_cases=refused))
 put(R/'CPU219_NEW_CALLER_METADATA_ACTUAL.json',dict(epoch=time.time(),purpose_id=ID,passed=True,groups=groups,
  group_count=3,rejected_cases=9,synthetic_fixture_only=True,actual210_closure_or_training_ready=False,
  old218_fixture_replays=0,model_raw_NPZ_USD_SDK_GPU_SSH_Git_reads_or_calls=0))
 print(json.dumps(dict(passed=True,groups=3,rejections=9,old218_fixture_replays=0,forbidden_calls=0)))


if __name__=='__main__':main()
