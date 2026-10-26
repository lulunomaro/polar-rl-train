from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;T=S.parent;B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
def main():
 old=B/'same_authorized_session_compressed_transport_v178.py';s=old.read_text('utf8')
 needle="        'close_actual_three86B_original_cost_fixed_paths_unused_once.py',"
 assert s.count(needle)==1
 s=s.replace(needle,needle+"\n        'run_qualified_native86_single_frozen_attempt_on72_finite_unused_once.py',",1)
 ast.parse(s);p=B/'same_authorized_session_compressed_transport_v179.py'
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 with (S/'reports/REPLAY179_EXACT_ENTRY_TRANSPORT_SOURCE_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),old_path=str(old),old_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),new_path=str(p),new_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),only_exact_replay_basename_added=True,no_pins_secrets_protocol_or_original_closing_changes=True,not_yet_run=True),f,indent=2)
 print('transport179 source prepared; no replay executed')
if __name__=='__main__':main()
