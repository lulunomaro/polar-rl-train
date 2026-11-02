from pathlib import Path
import ast,runpy
R=Path(__file__).resolve().parent;p=R/'build_w35_mod4v1_eval_v2.py';assert not p.exists()
s=(R/'build_w35_mod4v1_eval.py').read_text(encoding='utf-8').replace("D=R/'staged_sources/W35_MOD4V1_EVAL_V1'","D=R/'staged_sources/W35_MOD4V1_EVAL_V2'")
lines=s.splitlines();lines=["old=next(line for line in source.splitlines() if \"guard=read(OUT/'BEFORE_CONSTRUCTOR_CLOSURE10MM_MIMIC01_ACTUAL.json')\" in line)" if line.startswith('old=') else line for line in lines];s='\n'.join(lines)+'\n'
s=s.replace("assert old in source;source=source.replace(old,new)","new=old[:len(old)-len(old.lstrip())]+new.lstrip();assert old in source;source=source.replace(old,new)")
s=s.replace("needle=\"     obs=vec.get_observations();tick=int(real._integrated_contact.tick)\"","needle=\"obs=vec.get_observations();tick=int(real._integrated_contact.tick)\"")
s=s.replace('source.replace(needle,"     obs=vec.get_observations();','source.replace(needle,"obs=vec.get_observations();')
ast.parse(s);p.write_text(s,encoding='utf-8');runpy.run_path(str(p),run_name='__main__')
