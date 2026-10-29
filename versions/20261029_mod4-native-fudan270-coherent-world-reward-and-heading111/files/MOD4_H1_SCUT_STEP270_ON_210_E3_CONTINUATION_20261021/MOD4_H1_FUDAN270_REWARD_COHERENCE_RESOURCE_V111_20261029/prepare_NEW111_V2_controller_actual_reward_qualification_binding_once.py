"""NEW controller namespace after positive generated-GO qualification pin refusal."""
from pathlib import Path
import ast
P=Path(__file__).resolve().with_name('prepare_NEW111_actual_CPU_bound_original_writer_and_readers_SOURCE_ONLY_once.py')
s=P.read_text(encoding='utf8')
# Change only NEW unused destination selection in the original builder wrapper.
needle="s=s.replace('TWO106','TWO111').replace('NATIVE106','NATIVE111').replace('NEW106','NEW111').replace('closed106','closed111')"
assert s.count(needle)==1
s=s.replace(needle,needle+"\ns=s.replace('TWO111_FUDAN270_COHERENT_REWARD_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1','TWO111_FUDAN270_COHERENT_REWARD_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V2').replace('TWO111_FUDAN270_COHERENT_REWARD_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1','TWO111_FUDAN270_COHERENT_REWARD_FIRST_CLOSING_INITIAL_CPU_SOURCE_V2')\ns=s.replace(\"'native_learning_seed','goal_conditioning')\",\"'native_learning_seed','goal_conditioning','own_step_objective_qualification_SHA')\")")
ast.parse(s);exec(compile(s,str(P),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
