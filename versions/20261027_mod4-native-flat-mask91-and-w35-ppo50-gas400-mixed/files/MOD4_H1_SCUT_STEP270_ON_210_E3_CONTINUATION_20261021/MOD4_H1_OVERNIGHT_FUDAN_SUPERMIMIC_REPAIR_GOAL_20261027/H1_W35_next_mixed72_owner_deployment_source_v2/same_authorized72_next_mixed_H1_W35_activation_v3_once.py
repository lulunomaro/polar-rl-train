from pathlib import Path
import importlib.util,runpy,sys
HERE=Path(__file__).resolve().parent;W=HERE.parents[2]
def main():
 assert len(sys.argv)==1
 p=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py'
 s=importlib.util.spec_from_file_location('same_authorized_session_memory_mixed_activation_v2',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);t,old=m.install()
 try:sys.argv=[str(HERE/'install_and_activate_next_H1_W35_mixed72_once_v3_posix_request.py')];runpy.run_path(sys.argv[0],run_name='__main__')
 finally:t.SESSION=old
if __name__=='__main__':main()
