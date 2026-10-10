"""Keep the complete129 baseline at its actual prior directory, do not replay it."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;N=D.parent/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010'
def main():
 p=D/'review_wave131_selected_source_actual.py';assert not p.exists()
 s=(N/'review_matched_command130_selected_source_actual.py').read_text(encoding='utf8')
 s=s.replace("R=D/'reports'","R=D/'reports';BASE129=W/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010/reports'")
 s=s.replace("folder=R/'cases'/('clk2500-closure-episode-d3-129","folder=BASE129/'cases'/('clk2500-closure-episode-d3-129").replace("anchor_path=sorted(R.glob('CANDIDATE_129_REVIEW_","anchor_path=sorted(BASE129.glob('CANDIDATE_129_REVIEW_")
 s=s.replace('CANDIDATE_130','CANDIDATE_131').replace('candidate_source365','candidate_wave366').replace('E1-G3-COMMAND-130','E1-WAVE-G3-131')
 ast.parse(s);p.write_bytes(s.encode());print('Prepared actual131 selected complete129 source comparison, no GPU replay')
if __name__=='__main__':main()
