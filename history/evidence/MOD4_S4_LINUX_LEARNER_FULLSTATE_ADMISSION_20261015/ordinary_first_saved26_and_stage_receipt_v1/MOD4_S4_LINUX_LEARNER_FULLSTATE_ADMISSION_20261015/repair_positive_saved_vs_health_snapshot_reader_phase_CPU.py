"""Keep the original reader false; health writer snapshot is not save phase."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent
def main():
 old=D/'review_first_gate_pinned_positive_local_CPU_actual.py';s=old.read_text()
 a="health=r['actual_live_health_snapshot'];assert health['control_steps']>=controls"
 b="health=r['actual_live_health_snapshot'];assert health['version']==3 and health['control_steps']>0 and health['pid']==s['pid']"
 assert s.count(a)==1;s=s.replace(a,b);ast.parse(s)
 out=D/'review_first_gate_pinned_positive_local_CPU_actual_v2.py';assert not out.exists();out.write_text(s,encoding='utf8')
 receipt=json.loads(sorted((D/'reports').glob('S4_FIRST_GATE_OWN_MODEL25_ALL_INPUTS_TWOHOST_ACTUAL_*.json'))[-1].read_bytes())
 p=D/'reports/S4_POSITIVE_READER_HEALTH600_SAVED624_PHASE_ASSERT_ORIGINAL_ERROR.json';assert not p.exists()
 p.write_text(json.dumps(dict(epoch=time.time(),original_error='AssertionError health control_steps >= savedcontrols; health is a periodically written different phase',
  actual_health_snapshot_controls=receipt['actual_live_health_snapshot']['control_steps'],own_saved_controls=624,
  original_reader_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),new_reader_SHA=hashlib.sha256(out.read_bytes()).hexdigest(),
  original_reader_false_preserved=True,not_physics_or_PPO_failure=True,no_GPU_or_weight_or_budget_mutation=True),indent=2));print(out)
if __name__=='__main__':main()
