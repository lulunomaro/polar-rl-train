"""Create a new-source diagnostic preparer from the unchanged previous protocol."""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019'
s=(P/'prepare_fifteenth_closed_source_local_diagnostic_CPU_once.py').read_text('utf8')
s=s.replace('FIFTEENTH_','SIXTEENTH_').replace('FOURTEENTH_','FIFTEENTH_').replace('THIRTEENTH_','FOURTEENTH_')
s=s.replace('fifteenth','sixteenth').replace('fourteenth','fifteenth').replace('after_reward_hour15','after_reward_hour16').replace('after_reward_hour14','after_reward_hour15')
ast.parse(s)
with (B/'prepare_sixteenth_closed_source_local_diagnostic_CPU_once.py').open('x',encoding='utf8',newline='\n') as f:f.write(s)
