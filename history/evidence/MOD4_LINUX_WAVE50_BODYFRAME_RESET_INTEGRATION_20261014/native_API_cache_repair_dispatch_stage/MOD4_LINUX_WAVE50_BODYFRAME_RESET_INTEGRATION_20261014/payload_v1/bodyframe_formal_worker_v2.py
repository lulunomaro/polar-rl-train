"""New declared-axis formal worker; original normal learner/optimizer unchanged."""
from pathlib import Path
import hashlib,json,os,runpy,sys

def main():
    root=Path(__file__).resolve().parent
    sys.path.insert(0,str(root));runtime=root/'isaac/mod4';sys.path.insert(0,str(runtime))
    from birth_bodyframe_full_checkpoint_v2 import guard_manifest,patch
    manifest=json.loads((root/'BODYFRAME_TARGET_ACTUAL_MANIFEST.json').read_bytes())
    guard_manifest(manifest,False)
    assert manifest['mode']=='formal300' and manifest['duration_seconds']==300
    assert manifest['formal_native_and_fullrestore_admitted'] is True
    assert manifest['actual_parent_pid']==os.getppid() and manifest['actual_target_root']==str(root)
    freeze=root/manifest['sourcefreeze_relative_path']
    assert hashlib.sha256(freeze.read_bytes()).hexdigest()==manifest['sourcefreeze_SHA']
    for name,h in json.loads(freeze.read_bytes())['sha256'].items():
        p=root/name;assert p.resolve().is_relative_to(root.resolve()) and hashlib.sha256(p.read_bytes()).hexdigest()==h
    import wave50_lifetime_full_checkpoint as original
    import left_sameidentity_typed13_receipts as typed
    def query(env):
        from wave50_entry_full_pose_reset_v2 import query as actual_query
        return actual_query(env)
    patch(original,manifest,typed,query,fixture=False)
    import rescue_training
    install=rescue_training.install
    def own_install(runner,log_dir):
        install(runner,log_dir);log=runner.logger.log
        def own_log(*a,**kw):
            result=log(*a,**kw)
            if Path(os.environ['RM_RESCUE_STOP_FILE']).exists():
                runner.save(str(Path(log_dir)/f'model_{runner.current_learning_iteration}.pt'))
            return result
        runner.logger.log=own_log
    rescue_training.install=own_install
    worker=runtime/'train_wave50_lifetime_resume_ppo.py';sys.argv[0]=str(worker)
    runpy.run_path(str(worker),run_name='__main__')

if __name__=='__main__':main()
