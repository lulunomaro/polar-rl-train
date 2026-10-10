"""Prepare new read-only own366 and131 readers from proven schema; never replay old cases."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;N=D.parent/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010'
def save(n,s):
 p=D/n;assert not p.exists();ast.parse(s);p.write_bytes(s.encode())
def main():
 s=(N/'read_matched_command_own_save_cpu.py').read_text(encoding='utf8')
 s=s.replace('MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010','MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010').replace('import supervise_e1_command_retention_matched_once as m','import supervise_e1_wave_isolated_revision004_once as m').replace('len(f)==365','len(f)==366').replace('own365freeze_verified','own366freeze_verified').replace('e1_G3_command_retention_matched_PASSED.json','e1_wave_G3_isolated_observation_PASSED.json').replace('COMMAND_MATCHED_OWN_CPU','WAVE_OWN_CPU')
 save('read_wave_own_save_cpu.py',s)
 s=(N/'collect_matched_command130_actual.py').read_text(encoding='utf8').replace('COMMAND_MATCHED_ACTUAL_','WAVE_ACTUAL_').replace('E1_130-e1-g3-command-retention-matched_ASYNC_PUBLISHED.json','E1_131-e1-wave-g3-isolated_ASYNC_PUBLISHED.json').replace('e1_G3_command_retention_matched_PASSED.json','e1_wave_G3_isolated_observation_PASSED.json').replace('CANDIDATE_130','CANDIDATE_131').replace('E1-G3-COMMAND-300S-130','E1-WAVE-G3-300S-131')
 save('collect_wave131_actual.py',s)
 s=(N/'review_matched_command130_actual.py').read_text(encoding='utf8').replace('CANDIDATE_130','CANDIDATE_131').replace('E1-G3-COMMAND-130','E1-WAVE-G3-131').replace('requires_actual_retention_decision_before_more_PPO=True','requires_actual_in_scope_decision_before_more_PPO=True,inherited_flat_skills_diagnostic_E0_separately_frozen=True')
 save('review_wave131_actual.py',s)
 print('Prepared own366 CPU and complete131 matched readers, no GPU replay')
if __name__=='__main__':main()
