from pathlib import Path
import runpy,sys
N=Path(__file__).resolve().parent
sys.path.insert(0,str(N))
sys.argv=[str(N/'review_three_gpu86b_finals_CPU_unused_once.py'),'--stage',str(N)]
runpy.run_path(sys.argv[0],run_name='__main__')
