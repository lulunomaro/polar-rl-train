"""Atomic full-state checkpoints and a bounded, checkpoint-safe stopping hook."""
import json
import os
import time
from pathlib import Path


class SavedStop(Exception):
    pass


def install(runner, log_dir):
    original=runner.save
    def save(path, *a, **kw):
        path=Path(path);temp=path.with_suffix(path.suffix+'.partial')
        original(str(temp),*a,**kw)
        os.replace(temp,path)
        state={'checkpoint':str(path),'iteration':int(getattr(runner,'current_learning_iteration',0)),
               'saved_at':time.time(),'log_dir':str(log_dir),'pid':os.getpid()}
        (Path(log_dir)/'latest_complete.json').write_text(json.dumps(state,indent=2))
        deadline=float(os.environ.get('RM_RESCUE_DEADLINE','inf'))
        stop=Path(os.environ.get('RM_RESCUE_STOP_FILE',str(Path(log_dir)/'STOP_AFTER_SAVE')))
        if time.time()>=deadline or stop.exists():
            raise SavedStop('Full checkpoint saved; authorized budget or stop-file reached')
    runner.save=save


def learn(runner, num_learning_iterations, log_dir):
    install(runner,log_dir)
    try:runner.learn(num_learning_iterations=num_learning_iterations,init_at_random_ep_len=True)
    except SavedStop as e:print('[rescue] '+str(e),flush=True)
