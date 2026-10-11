"""Finish only the CPU action not reached by duplicate local receipt rejection."""
from second50_io import *
import ast
source=D/'stage_second_scope_and_cpu_once.py'
tree=ast.parse(source.read_text(encoding='utf8'))
calls=[x for x in ast.walk(tree) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='run']
assert len(calls)==2
# Extract the second remote CPU code literally; staging and copying are not replayed.
node=next(x for x in calls if 'CPU_private_command_disk_roundtrip_exact' in ast.unparse(x))
arg=node.args[1]
while isinstance(arg,ast.Call) and isinstance(arg.func,ast.Attribute) and arg.func.attr=='replace':arg=arg.func.value
assert isinstance(arg,ast.Constant);code=arg.value
old='text=inspect.getsource(own.prior.train);assert "\'train_wave50_same_scope_resume_ppo.py\'" in text and "terrain[\'terrain_state_restored_exact\']" in text'
assert code.count(old)==1
new='''original_text=(D/'supervise_wave50_independent_scope_once.py').read_text();tree=ast.parse(original_text);node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='train');text=ast.get_source_segment(original_text,node)
a="assert not terrain['terrain_state_restored_exact'] and terrain['explicit_G3_to_WAVE50_geometry_transition'] and terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']"
b="assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G3_to_WAVE50_geometry_transition'] and not terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']"
assert text.count(a)==1;text=text.replace(a,b).replace("else 'train_wave50_full_resume_ppo.py'","else 'train_wave50_same_scope_resume_ppo.py'")
env=dict(own.prior.__dict__);exec(compile(text,'CPU_same50_expected_train','exec'),env)
assert env['train'].__code__.co_code==own.prior.train.__code__.co_code and env['train'].__code__.co_consts==own.prior.train.__code__.co_consts
assert ('train_wave50_fresh_preflight_ppo.py','train_wave50_full_resume_ppo.py','train_wave50_same_scope_resume_ppo.py') in own.prior.guardian.__code__.co_consts'''
code=code.replace(old,new)
def main():
 assert not (R/'SECOND_TARGET_CPU_PASSED.json').exists()
 assert list(R.glob('SECOND_STAGE_ERROR_[0-9]*.json'))
 save('LOCAL_CANDIDATE_RECEIPT_WBX_REJECTION_REVIEW.json',dict(epoch=time.time(),original_source=str(source),original_source_SHA=H(source.read_bytes()),already_saved_candidate_number_local_duplicate_rejected=True,actual_root_sources_and_all_remote_reports_staged_once=True,CPU_action_not_executed_before_rejection=True,only_unexecuted_CPU_continued=True,dynamic_controller_CPU_reader_bound_to_actual_compiled_function_bytecode_and_constants=True,no_stage_copy_dispatch_GPU_budget_or_old_once_replay=True))
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:assert not f.listdir(ROOT+'/reports').count('SECOND_TARGET_CPU_PASSED.json')
  result=run(n,code.replace('ROOT_TOKEN',repr(ROOT)).replace('SHA_TOKEN',repr(SOURCE_SHA)))
  save('SECOND_TARGET_CPU_PASSED.json',result);print(json.dumps(dict(CPU_passed=True,root=ROOT,source_count=386,no_GPU_or_dispatch=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('CPU_BINDING_CONTINUATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise
