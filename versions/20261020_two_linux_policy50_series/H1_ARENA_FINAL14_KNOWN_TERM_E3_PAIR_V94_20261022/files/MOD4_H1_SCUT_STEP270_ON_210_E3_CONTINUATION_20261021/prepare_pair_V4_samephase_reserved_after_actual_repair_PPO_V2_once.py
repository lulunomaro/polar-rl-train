from pathlib import Path
import ast
T=Path(__file__).resolve().parent
src=(T/'prepare_pair_V4_samephase_reserved_after_actual_repair_PPO_once.py').read_text('utf8')
assert src.count('+new=new.replace')==1
src=src.replace('+new=new.replace','new=new.replace');ast.parse(src)
(T/'PAIR_V4_GENERATOR_V2_EXECUTED_SOURCE.py').open('x',encoding='utf8').write(src)
exec(compile(src,'PAIR_V4_GENERATOR_V2_EXECUTED_SOURCE.py','exec'),dict(__file__=__file__,__name__='__main__'))
