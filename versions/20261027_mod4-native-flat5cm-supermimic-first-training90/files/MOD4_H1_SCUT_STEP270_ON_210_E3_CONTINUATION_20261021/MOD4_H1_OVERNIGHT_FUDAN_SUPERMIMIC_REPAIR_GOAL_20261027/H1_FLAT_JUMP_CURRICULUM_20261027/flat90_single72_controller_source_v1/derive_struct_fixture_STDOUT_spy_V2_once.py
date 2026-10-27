from pathlib import Path
import ast,hashlib,json,time
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 old=HERE/'check_flat90_ready_GO_dispatch_account_tiny_CPU_once.py';new=HERE/'check_flat90_ready_GO_dispatch_account_tiny_CPU_V2_once.py';assert not new.exists()
 text=old.read_text('utf8');needle=' class PopenSpy:\n';assert text.count(needle)==1
 changed=text.replace(needle,needle+'  STDOUT=object()\n',1).replace('FLAT90_READY_GO_DISPATCH_ACCOUNT_STRUCT_CPU_ACTUAL_V1.json','FLAT90_READY_GO_DISPATCH_ACCOUNT_STRUCT_CPU_ACTUAL_V2.json').replace('FLAT90_STRUCT_FIXTURE_ORIGINAL_ERROR_','FLAT90_STRUCT_FIXTURE_V2_ORIGINAL_ERROR_')
 new.write_text(changed,encoding='utf8');ast.parse(changed)
 with (HERE/'STRUCT_FIXTURE_STDOUT_SPY_REPAIR_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),old_fixture_SHA=H(old),new_fixture_SHA=H(new),
  old_error='PopenSpy missing STDOUT; fixture only before PopenSpy invocation',only_added_missing_mock_constant_and_distinct_output_names=True,production_source_unchanged=True,no_actual_spawn_or_ledger_IO=True),f,indent=2)
 print(json.dumps(dict(new_fixture=str(new),SHA=H(new),production_source_unchanged=True)))
if __name__=='__main__':main()
