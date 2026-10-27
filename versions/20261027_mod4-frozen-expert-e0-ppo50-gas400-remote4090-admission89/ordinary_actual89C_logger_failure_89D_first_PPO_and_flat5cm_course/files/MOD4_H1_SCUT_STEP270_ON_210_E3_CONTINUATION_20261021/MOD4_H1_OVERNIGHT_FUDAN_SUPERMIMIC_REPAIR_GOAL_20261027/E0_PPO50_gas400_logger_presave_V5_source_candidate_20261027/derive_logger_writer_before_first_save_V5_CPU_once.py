"""Minimal V4→V5 logger init move; no model/SDK/GPU/remote/account operation."""
from pathlib import Path
import ast,copy,hashlib,json,time,types

HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent
OLD=L/'E0_PPO50_gas400_single72_controller_source_preparation_v1/E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py'
ERROR=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027/reports/E0_FIRST_ACTUAL_4090_PPO_V4_FULLRESTORE_CLOCK_GAS400_RETURNED_ACTUAL.json'
def H(raw):return hashlib.sha256(raw).hexdigest()
def work_node(raw):
 return next(n for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.FunctionDef) and n.name=='work')
def writer_assignment(node):
 return isinstance(node,ast.Assign) and len(node.targets)==1 and ast.dump(node.targets[0],include_attributes=False)==ast.dump(ast.parse('runner.logger.writer=None').body[0].targets[0],include_attributes=False)
def main():
 target=HERE/'E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py';assert not target.exists()
 before=OLD.read_bytes();assert H(before)=='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19'
 marker=b' def work(runner,n,log_dir):\n'
 early=marker+b'  runner.logger.writer=None\n'
 late=b'  runner.logger.writer=None;completed=0;oldlog=runner.logger.log;original_step=vec.step'
 late_fixed=b'  completed=0;oldlog=runner.logger.log;original_step=vec.step'
 assert before.count(marker)==before.count(late)==1
 after=before.replace(marker,early).replace(late,late_fixed)
 assert after.replace(early,marker).replace(late_fixed,late)==before
 old_tree=ast.parse(before);new_tree=ast.parse(after);old_work=work_node(before);new_work=work_node(after)
 old_assign=[(i,n) for i,n in enumerate(old_work.body) if writer_assignment(n)]
 new_assign=[(i,n) for i,n in enumerate(new_work.body) if writer_assignment(n)]
 assert len(old_assign)==len(new_assign)==1 and new_assign[0][0]==0
 a=copy.deepcopy(old_tree);b=copy.deepcopy(new_tree)
 aw=next(n for n in ast.walk(a) if isinstance(n,ast.FunctionDef) and n.name=='work')
 bw=next(n for n in ast.walk(b) if isinstance(n,ast.FunctionDef) and n.name=='work')
 aw.body=[n for n in aw.body if not writer_assignment(n)];bw.body=[n for n in bw.body if not writer_assignment(n)]
 assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
 # Execute only the actual relocated assignment against a fake logger. The
 # logger guard reproduces actual RSL logger.py:268 before any torch/PT I/O.
 events=[]
 class FakeLogger:
  def save_model(self,path,iteration):
   if self.writer is not None and self.logger_type in ['neptune','wandb']:
    self.writer.save_model(path,iteration)
   events.append(('logger_save_model_returned',path,iteration))
 class FakeRunner:
  def __init__(self):self.logger=FakeLogger()
  def save(self,path):events.append(('runner_save',path));self.logger.save_model(path,0)
 broken=FakeRunner()
 try:broken.save('startup0_fake_no_file')
 except AttributeError as exc:
  assert "writer" in str(exc);original_error_reproduced=str(exc)
 else:raise AssertionError('Original missing-writer ordering did not fail')
 runner=FakeRunner();events.clear()
 assignment=copy.deepcopy(new_assign[0][1]);ast.fix_missing_locations(assignment)
 exec(compile(ast.Module(body=[assignment],type_ignores=[]),'<actual V5 first work statement>','exec'),dict(runner=runner))
 assert runner.logger.writer is None
 runner.save('startup0_fake_no_file');events.append(('native24_simulated_no_physics',24))
 # As in RSL learn, logging initialization may later replace None. The moved
 # assignment does not run again and cannot clear that newly initialized writer.
 live_writer=object();runner.logger.writer=live_writer;runner.logger.logger_type='tensorboard'
 runner.save('first_update_fake_no_file');assert runner.logger.writer is live_writer
 target.write_bytes(after)
 old_error=json.loads(ERROR.read_bytes());assert old_error['passed_first_PPO'] is False
 proof=dict(attempt_id='E0_ACTUAL89C_LOGGER_WRITER_ABSENT_PRESAVE_ERROR_SOURCE_REPAIR_V5_20261027',epoch=time.time(),
  original_V4=dict(path=str(OLD),bytes=len(before),SHA=H(before)),V5=dict(path=str(target),bytes=len(after),SHA=H(after)),
  original_actual_error=dict(path=str(ERROR),bytes=ERROR.stat().st_size,SHA=H(ERROR.read_bytes())),
  actual89C_GPU_fullrestore_reported_passed_by_root=True,actual89C_no_native24_or_newPPO=True,
  failed89C_is_resource_cost_only_not_a_new_model_source=True,source_model_still_original_typed54f=True,
  only_change='Move the existing runner.logger.writer=None assignment to the first work statement, before any save; remove its late occurrence.',
  inverse_entire_V4_bytes_exact=True,AST_identical_after_removing_one_moved_assignment=True,
  old_work_writer_assignment_index=old_assign[0][0],new_work_writer_assignment_index=new_assign[0][0],
  fake_logger_fixture=dict(original_missing_writer_error_reproduced=original_error_reproduced,V5_startup_save_passed=True,
   post_learn_writer_not_cleared=True,events=events,actual_files_or_physics_not_used=True),
  original_LR_scalar_actions_physics_optimizer_fullsave_chain_caps_and_account_paths_unchanged=True,
  no_PT_normalizer_GPU_SDK_remote_or_ledger_IO=True,previous_actual_own_cost_allout_locks_settlement_still_root_owned=True,
  Git_status='ordinary_supplement_existing89trial_no_new_record_tag')
 report=HERE/'E0_V5_LOGGER_PRESAVE_EXACT_MOVE_CPU_ACTUAL.json';assert not report.exists();report.write_text(json.dumps(proof,indent=2),encoding='utf8')
 print(json.dumps(dict(V5=proof['V5'],only_moved_assignment=True,source_AST_otherwise_exact=True,fake_logger_fixture_passed=True)))
if __name__=='__main__':main()
