from pathlib import Path
import importlib.util,runpy,sys
HERE=Path(__file__).resolve().parent;W=HERE.parents[2]
def main():
 target=HERE/'install_W35_existing72_frozen_source_and_initial_SDK_CPU_once_v1.py';assert len(sys.argv)==1
 path=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py'
 sp=importlib.util.spec_from_file_location('same_authorized_zstd_memory_install_only_W35',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 transport,previous=m.install()
 try:sys.argv=[str(target)];runpy.run_path(str(target),run_name='__main__')
 finally:transport.SESSION=previous
if __name__=='__main__':main()
