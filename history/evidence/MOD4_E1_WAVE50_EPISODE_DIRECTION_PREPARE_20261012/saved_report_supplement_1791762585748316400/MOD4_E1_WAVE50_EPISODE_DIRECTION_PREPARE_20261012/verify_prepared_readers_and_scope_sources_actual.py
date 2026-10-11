"""Validate reader syntax and required scope snapshots without executing future audits."""
from wave_direction_io import *
import ast,importlib.util
def main():
 files=['read_direction_own_formal_cpu_actual.py','verify_direction_saved_PPO_cpu_actual.py','collect_direction_candidate_actual.py','review_direction_candidate_actual.py','review_direction_direct149_prefix_actual.py','review_direction_complete_dynamic_family_trace_actual.py']
 for name in files:ast.parse((D/name).read_text())
 tree=ast.parse((D/'review_direction_complete_dynamic_family_trace_actual.py').read_text())
 code=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CODE' for x in n.targets));compile(code,'<future-readonly-trace-CODE>','exec')
 proof=json.loads((R/'DIRECTION_TARGET_CPU_PASSED.json').read_bytes());freeze=json.loads((R/'SOURCE_FREEZE.json').read_bytes())['sha256'];payload={p.relative_to(D/'payload').as_posix():H(p.read_bytes()) for p in (D/'payload').rglob('*') if p.is_file()}
 assert all(freeze[k]==v for k,v in payload.items()) and len(payload)==12 and len(freeze)==424
 save('READERS_SYNTAX_AND_SOURCE_BINDING_ACTUAL_'+str(time.time_ns())+'.json',dict(epoch=time.time(),passed=True,reader_files_AST_parsed=files,remote_trace_CODE_syntax_valid=True,payload12_new_direction_file_bytes_match_actual_sourcefreeze424=True,targetCPU_actualpass_ref=str(R/'DIRECTION_TARGET_CPU_PASSED.json'),prepared_readers_not_future_final_candidate_or_trace_pass=True,no_GPU_or_budget_write=True))
 print(json.dumps(dict(readonly_reader_syntax_passed=True,scope_payload_sourcefreeze_exact=True,not_future_pass=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('PREPARED_READER_SYNTAX_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_oldstage_replay=True));raise
