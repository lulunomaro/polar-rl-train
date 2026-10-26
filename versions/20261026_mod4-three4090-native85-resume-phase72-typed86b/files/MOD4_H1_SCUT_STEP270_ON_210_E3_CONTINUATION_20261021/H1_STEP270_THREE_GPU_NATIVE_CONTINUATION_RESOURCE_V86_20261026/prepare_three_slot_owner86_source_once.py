from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;P=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026';R=N/'reports';R.mkdir(exist_ok=True);D=N/'controllers'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not D.exists();D.mkdir()
 rows=[]
 for name in ('three_slot_common_v1.py','three_slot_finite_node_v1.py','single_writer72_authority_V85M_source.py','mixed84_protocol_v1.py','three_real_gpu_resource_v1.py'):
  shutil.copyfile(P/'controllers'/name,D/name)
 owner=(P/'controllers/three_slot_finite_owner_V85M_pair_authority72.py').read_bytes().decode('utf8')
 start="specs=cfg['experts'];assert set(specs)=={'e2','recovery'}"
 assert owner.count(start)==1
 owner=owner.replace(start,"specs=cfg['experts'];assert set(specs)=={'h1','e2','recovery'}")
 assert owner.count("cfg['deferred_experts']==['h1']")==1
 owner=owner.replace("cfg['deferred_experts']==['h1']","cfg['deferred_experts']==[];validate_schedule(cfg)")
 marker='from single_writer72_authority_V85M_source import authority_tracking_schema_admitted,authority_original_extension_count,authority_budget_GO_allowed'
 assert owner.count(marker)==1;owner=owner.replace(marker,marker+'\nfrom mixed86_protocol_v1 import validate_schedule')
 gate='and authority_budget_GO_allowed(c)'
 assert owner.count(gate)==1;owner=owner.replace(gate,gate+" and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'")
 (D/'three_slot_finite_owner_V86_authority72.py').write_bytes(owner.encode('utf8'))
 p=D/'three_slot_common_v1.py';old=p.read_bytes().decode('utf8');new=old.replace('def valid_ready(row,spec):\n','def valid_ready(row,spec):\n if spec.get(\'native_continuation\'):\n  from mixed86_protocol_v1 import native_valid_ready\n  return native_valid_ready(row,spec)\n',1);assert new!=old;p.write_bytes(new.encode('utf8'))
 def function(text,name):return next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name==name)
 assert ast.dump(function(old,'charge_values'),include_attributes=False)==ast.dump(function(new,'charge_values'),include_attributes=False)
 before=ast.parse(old);after=ast.parse(new)
 for a,b in zip(before.body,after.body):
  if isinstance(a,ast.FunctionDef) and a.name=='valid_ready':
   b.body=b.body[1:]
  assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
 p=D/'three_real_gpu_resource_v1.py';raw=p.read_bytes().decode('utf8');needle="(15669 if spec['key']=='h1' else 7000)";assert raw.count(needle)==1;p.write_bytes(raw.replace(needle,"(15669 if spec['key']=='h1' or spec.get('finite_method_test') else 7000)").encode('utf8'))
 shutil.copyfile(N/'mixed86_protocol_v1.py',D/'mixed86_protocol_v1.py')
 for p in D.glob('*.py'):
  ast.parse(p.read_text('utf8'))
  prior=P/'controllers'/p.name
  if p.name=='three_slot_finite_owner_V86_authority72.py':prior=P/'controllers/three_slot_finite_owner_V85M_pair_authority72.py'
  rows.append(dict(relative=p.name,old_SHA=H(prior) if prior.exists() else None,new_SHA=H(p),bytes=p.stat().st_size))
 result=dict(epoch=time.time(),status='SOURCE_ONLY_OWNER72_THREE_SLOT_NATIVE86',files=rows,original_charge_values_AST_exact=True,
   node_and_authority_adapter_byte_exact=True,owner_changes='strict three-slot schedule, typed-source validation and explicit finite-restored mode only',
   common_changes='new exact native-continuation admission branch; every original function including old ready branches/charge/spawn/state preserved',
   resource_change='native15669MiB startup threshold, original per-file/locks/path/process/disk/RAM guards retained',
   actual_target_SDK_admitted=False,owner_or_payload_or_GO=False,private_lock_or_account_actions=False)
 (R/'OWNER_COMMON_RESOURCE_V86_SOURCE_EXACT_CHANGE_INDEX_ACTUAL.json').write_text(json.dumps(result,indent=2),'utf8')
 print(json.dumps({'source_ready':True,'original_charge_AST_exact':True,'files':len(rows),'GO':False}))
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('ORIGINAL_OWNER_SOURCE_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps({'error':traceback.format_exc(),'no_runtime_change':True},indent=2),'utf8');raise
