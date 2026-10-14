"""Declared-axis formal worker with original engine-before-RL import order."""
from pathlib import Path
import hashlib,json,os,runpy,sys

def main():
    root=Path(__file__).resolve().parent;runtime=root/'isaac/mod4';sys.path.insert(0,str(root));sys.path.insert(0,str(runtime))
    manifest=json.loads((root/'BODYFRAME_TARGET_ACTUAL_MANIFEST.json').read_bytes())
    assert manifest['mode']=='formal300' and manifest['duration_seconds']==300 and manifest['formal_native_and_fullrestore_admitted'] is True
    assert manifest['actual_parent_pid']==os.getppid() and manifest['actual_target_root']==str(root)
    freeze=root/manifest['sourcefreeze_relative_path'];assert hashlib.sha256(freeze.read_bytes()).hexdigest()==manifest['sourcefreeze_SHA']
    for name,h in json.loads(freeze.read_bytes())['sha256'].items():
        q=root/name;assert q.resolve().is_relative_to(root.resolve()) and hashlib.sha256(q.read_bytes()).hexdigest()==h
    from bodyframe_deferred_original_import_v1 import install,own_launcher
    def checkpoint(module):
        from birth_bodyframe_full_checkpoint_v5 import guard_manifest,patch
        import left_sameidentity_typed13_receipts as typed
        guard_manifest(manifest,False)
        def query(env):
            from wave50_entry_full_pose_reset_v2 import query as actual_query
            return actual_query(env)
        patch(module,manifest,typed,query,fixture=False)
    def rescue(module):
        original_install=module.install
        def own_install(runner,log_dir):
            original_install(runner,log_dir);log=runner.logger.log
            def own_log(*a,**kw):
                result=log(*a,**kw)
                if Path(os.environ['RM_RESCUE_STOP_FILE']).exists():runner.save(str(Path(log_dir)/f'model_{runner.current_learning_iteration}.pt'))
                return result
            runner.logger.log=own_log
        module.install=own_install
    install({'isaaclab.app':own_launcher,'wave50_lifetime_full_checkpoint':checkpoint,'rescue_training':rescue})
    worker=runtime/'train_wave50_lifetime_resume_ppo.py';sys.argv[0]=str(worker);runpy.run_path(str(worker),run_name='__main__')

if __name__=='__main__':main()
