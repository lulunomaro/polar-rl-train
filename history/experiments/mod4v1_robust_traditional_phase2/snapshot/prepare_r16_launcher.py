"""NewR16IDs/runnerforR15softwarefix. Old33consumedIDs/source/errorsuntouched."""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent;s=(R/'launch_r15_jump_roll_train.py').read_text(encoding='utf-8');s=s.replace('r15_jump_roll_train33','r16_jump_roll_train33').replace('prepare_jump_roll_v2.py','prepare_jump_roll_v3.py').replace('run_jump270_roll_v2.py','run_jump270_roll_v3.py').replace("case=f'r15_","case=f'r16_").replace('R15_JUMP_ROLLVMC_TRAIN','R16_JUMP_ROLLVMC_FIXED_API_TRAIN')
old='with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,jobs))';assert old in s;new="""rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 for offset in range(0,len(jobs),4):
  chunk=list(pool.map(run,jobs[offset:offset+4]));rows.extend(chunk)
  (D/'LIVE_ROWS.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
  if any(r['returncode']!=0 for r in chunk):
   (D/'SOFTWARE_ABORT.json').write_text(json.dumps({'reason':'programerrornotphysicalscore','completed_prefix':rows,'remaining_not_started':jobs[offset+4:]},indent=2),encoding='utf-8');raise RuntimeError('softwareerror: preserveprefix, do notconsumequeuedcases')""";s=s.replace(old,new);ast.parse(s);p=R/'launch_r16_jump_roll_train.py';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n');print(p)
