from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;T=S.parent;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 previous=json.loads((S/'reports/FROZEN_NATIVE86_SINGLE_COMPLETE_ATTEMPT_RETURNED_ACTUAL.json').read_bytes())
 assert previous['actual_finite_returned'] and previous['all_own_children_actual_out'] and previous['actual_result'] is None and previous['actual_original_SDK_admission'] is None
 assert "No module named 'h1_step270_sdk_runtime_candidate'" in previous['original_error']['error']
 D=T/'H1_STEP270_NATIVE86_FULL_SINGLE_ATTEMPT_REPLAY_R3_20261027';D.mkdir();(D/'reports').mkdir()
 for name in ('driver.py','run_native86_replay_R2_original_environment_once.py'):
  target='run_native86_replay_R3_original_root_import_once.py' if name.startswith('run_') else name
  with (D/target).open('xb') as f:f.write((S/name).read_bytes())
 entry=(S/'native86_frozen_single_sdk_entry_v1.py').read_text('utf8');old="sys.path[:0]=[str(B/'source'),str(B/'source/sm_deps'),str(B/'lib'),str(J/'runtime/isaac/mod4'),str(HERE)]"
 new="sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'lib'),str(J/'runtime/isaac/mod4'),str(HERE)]"
 assert entry.count(old)==1;entry=entry.replace(old,new,1);ast.parse(entry)
 with (D/'native86_frozen_single_sdk_entry_v1.py').open('x',encoding='utf8',newline='\n') as f:f.write(entry)
 q=json.loads((S/'BINDING.json').read_bytes());q.update(remote_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1native86_complete_single_replay_20261027r3',entry_SHA=H(D/'native86_frozen_single_sdk_entry_v1.py'),previous_R2_missing_module_before_any_actor=True)
 with (D/'BINDING.json').open('x',encoding='utf8') as f:json.dump(q,f,ensure_ascii=False,indent=2)
 with (D/'reports/R3_ORIGINAL_WORKER_ROOT_PATH_FIX_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),previous_R2_original_returncode=previous['returncode'],previous_R2_primary_error_preserved=True,rc0_not_interpreted_as_test_success=True,only_source_root_import_path_added=True,original_environment_AST_and_driver_exact=True,actual_policy_attempts_so_far=0,no_physical_replay_yet=True),f,indent=2)
 B=T/'H1_STEP270_REWARD_PATH_V1_20261022';s=(B/'same_authorized_session_compressed_transport_v180.py').read_text('utf8');needle="        'run_native86_replay_R2_original_environment_once.py',";assert s.count(needle)==1
 s=s.replace(needle,needle+"\n        'run_native86_replay_R3_original_root_import_once.py',",1);ast.parse(s)
 with (B/'same_authorized_session_compressed_transport_v181.py').open('x',encoding='utf8',newline='\n') as f:f.write(s)
 print('R3 source prepared, only original worker root sys.path added; no actor run')
if __name__=='__main__':main()
