"""Retain rejected fixture; use explicit 35-to50 command identity view only in CPU fixture."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'complete_unexecuted_target_cpu_exact_function_once.py').read_text()
anchor="code=code.replace('import test_wave50_entry_target_cpu as test',prefix+'import test_wave50_entry_target_cpu as test')"
assert s.count(anchor)==1
sub='''fixture_path=own.CODE/'test_wave50_entry_target_cpu.py'
fixture_text=fixture_path.read_text()
anchor="out=dict(ck,E1_terrain_state=state);out[KEY]=identity(state)"
assert fixture_text.count(anchor)==1
fixture_text=fixture_text.replace(anchor,"out=dict(ck,E1_terrain_state=state);out[KEY]=identity(state);out['E1_retained_flat_command_state']=dict(ck['E1_retained_flat_command_state'],assignment_sha256=state['entry_assignment_sha256'])")
test=types.ModuleType('explicit_assignment_CPU_fixture');test.__file__=str(fixture_path)
exec(compile(fixture_text,str(fixture_path)+'::explicit_new_assignment_fixture_only','exec'),test.__dict__)
'''
s=s.replace(anchor,"code=code.replace('import test_wave50_entry_target_cpu as test',prefix+"+repr(sub)+")")
exec(compile(s,'<only-unexecuted-CPU-fixture-view>','exec'),{'__file__':str(D/'complete_unexecuted_target_cpu_exact_function_once.py'),'__name__':'__main__'})
