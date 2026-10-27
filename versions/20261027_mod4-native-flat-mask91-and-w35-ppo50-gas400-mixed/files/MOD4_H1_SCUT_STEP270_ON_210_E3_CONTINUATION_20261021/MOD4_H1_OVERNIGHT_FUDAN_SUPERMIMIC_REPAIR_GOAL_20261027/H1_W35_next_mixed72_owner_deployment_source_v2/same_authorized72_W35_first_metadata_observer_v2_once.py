from pathlib import Path
import importlib.util,runpy,sys
HERE=Path(__file__).resolve().parent;W=HERE.parents[2]
def main():
 assert len(sys.argv)==1
 p=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py'
 s=importlib.util.spec_from_file_location('same_authorized_memory_observer_first_v2',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);t,old=m.install()
 try:sys.argv=[str(HERE/'observe_W35_first_or_mixed_natural_closing_once_v2.py'),'first'];runpy.run_path(sys.argv[0],run_name='__main__')
 finally:t.SESSION=old
if __name__=='__main__':main()
