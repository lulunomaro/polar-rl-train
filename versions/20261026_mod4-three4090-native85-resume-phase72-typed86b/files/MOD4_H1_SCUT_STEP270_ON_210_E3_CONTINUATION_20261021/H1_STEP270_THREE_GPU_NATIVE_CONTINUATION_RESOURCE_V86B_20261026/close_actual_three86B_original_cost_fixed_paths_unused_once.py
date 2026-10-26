from pathlib import Path
import runpy,sys
N=Path(__file__).resolve().parent
sys.path.insert(0,str(N))
sys.argv=[str(N/'collect_three_gpu86b_finals_actual_cost_unused_once.py'),'--stage',str(N),'--go-report',str(N/'reports/THREE_GPU86B_FIRST_GO_PPO_NATIVE_POLICY_PHASE_ACTUAL.json')]
runpy.run_path(sys.argv[0],run_name='__main__')
