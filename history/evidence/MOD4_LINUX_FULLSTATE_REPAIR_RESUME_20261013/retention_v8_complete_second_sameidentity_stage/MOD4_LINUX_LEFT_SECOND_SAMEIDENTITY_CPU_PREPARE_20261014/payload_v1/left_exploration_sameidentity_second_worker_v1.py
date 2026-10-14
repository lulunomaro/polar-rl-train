"""Formal-onlysecondsameidentity worker; original RLworker and learn unchanged."""
import os,sys,runpy,json,time,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
def main():
    assert not os.environ.get('MOD4_LEFT_ADMISSION_MODE'),'NoSDKnativefreshreplay'
    worker=R/'isaac/mod4/train_wave50_lifetime_resume_ppo.py'
    sys.path.insert(0,str(worker.parent))
    import wave50_lifetime_full_checkpoint
    from left_exploration_sameidentity_resume_contract_v2 import patch
    patch(wave50_lifetime_full_checkpoint,R)
    import rescue_training
    original_install=rescue_training.install
    def install(runner,log_dir):
        original_install(runner,log_dir)
        original_log=runner.logger.log
        def log(*a,**kw):
            original_log(*a,**kw)
            if Path(os.environ['RM_RESCUE_STOP_FILE']).exists():runner.save(str(Path(log_dir)/f'model_{runner.current_learning_iteration}.pt'))
        runner.logger.log=log
    rescue_training.install=install
    sys.argv[0]=str(worker)
    runpy.run_path(str(worker),run_name='__main__')
if __name__=='__main__':main()
