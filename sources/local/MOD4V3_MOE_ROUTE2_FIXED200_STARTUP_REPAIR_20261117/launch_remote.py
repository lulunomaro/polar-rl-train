from pathlib import Path
import runpy,sys
sys.argv=[str(Path(__file__).with_name('remote_control.py')),'train']+sys.argv[1:]
runpy.run_path(sys.argv[0],run_name='__main__')
