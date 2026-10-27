from pathlib import Path
import ast,hashlib,json,time
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=HERE/'INDEX.json';assert not p.exists()
 for name in ('EXACT88C_SOURCE_PINNING_AND_RESTORE_AST_ACTUAL.json','TYPED88C_FLAT_RESTORE_STRUCTURAL_CPU_ACTUAL_V1.json','NEW_FLAT_PUBLICATION_SCHEMA_CPU_ACTUAL_V1.json'):
  assert json.loads((HERE/name).read_bytes())['passed']
 for src in HERE.glob('*.py'):ast.parse(src.read_bytes())
 T=HERE.parents[2];L=HERE.parents[1]
 q=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/payloads/h1/job0/runtime/isaac/mod4/action_delay_physics_queue.py'
 reader=L/'native88C_fullstate_qualification_reader_repair_v2/native88_initial_CPU_reader_primitives_v1.py'
 cpu=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/reports/NATIVE88C_READER_REPAIRED_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json'
 assert "control_us=self.control_us" in q.read_text('utf8') and "state['control_us']==10000" in q.read_text('utf8')
 assert "saved=s['physical_action_delay_state']" in reader.read_text('utf8') and 'q.validate_state(dict(saved,rng=' in reader.read_text('utf8')
 qualified=json.loads(cpu.read_bytes())['models']['h1']['original_saved_D0_D7'];assert qualified['passed'] and qualified['original_D3_D4_D5_D6_D7_validator_AST_exact']
 with (HERE/'QUEUE_STATE_CONTROL_US_ACTUAL88C_SAVED_CPU_EVIDENCE.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),
  actual_saved_CPU_qualification=qualified,saved_state_key='physical_action_delay_state.control_us',value=10000,
  receipt_and_recipe_other_key='control_period_us',not_interchangeable=True,
  original_actual_CPU_used_saved_state_in_exact_original_queue_validate=True,
  evidence=[dict(path=str(x),bytes=x.stat().st_size,SHA=H(x)) for x in (q,reader,cpu)],
  no_PT_read_or_revalidation=True),f,indent=2)
 rows=[dict(relative=x.name,bytes=x.stat().st_size,SHA=H(x)) for x in sorted(HERE.iterdir()) if x.is_file()]
 with p.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),schema='mod4.native88C_to_flat05.exact_source_frozen.v1',files=rows,
  source_frozen=True,actual_model_restore_SDK_resource_GPU_GO_and_publication_pending=True,Git_status='ordinary_supplement_pending_root'),f,indent=2)
 print(json.dumps(dict(index_SHA=H(p),module_SHA=H(HERE/'native88C_to_flat_migration_v1.py'),pins_SHA=H(HERE/'native88C_flat_pins_v1.py'),files=len(rows),source_only=True)))
if __name__=='__main__':main()
