"""Complete unused464 launch after its pre-network local-busy refusal.

Same frozen task/source/namespace. No SSH while another known controller is
alive; preserve old local-CIM rejection. Then one FIRST and sole postround.
"""
from pathlib import Path
import importlib.util
import json
import os
import time
import traceback
N=Path(__file__).resolve().parent;R=N/'reports'
spec=importlib.util.spec_from_file_location('h1_run464_controller',N/'run.py')
controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)


def main():
    assert not(R/'RECOVERY_WAIT_ONCE.json').exists()
    assert not(R/'LAUNCH_ONCE.json').exists()and not(R/'OWNER_LAUNCH_ACTUAL.json').exists()
    controller.verify_index('4e8adaf084f3620f1d108a8bde467101f61e822952f978939142c2167ec1e704')
    rows=controller.local_rows();others=[r for r in rows if r['ProcessId']!=os.getpid()]
    controller.put('RECOVERY_WAIT_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),local_only=True,waiting_for=others,original_refusal='LAUNCH_LOCAL_CIM.json',same_frozen_task_and_namespace=True))
    controller.wait_local()
    original_gate=controller.gate
    controller.gate=lambda label:original_gate(label+'_AFTER_LOCAL_RELEASE')
    controller.launch('4e8adaf084f3620f1d108a8bde467101f61e822952f978939142c2167ec1e704')
    controller.first()
    controller.bind()
    controller.put('RECOVERY_COMPLETED_LAUNCH_FIRST_POSTROUND.json',dict(epoch=time.time(),passed=True,same_namespace=True,postround_bound=True))


if __name__=='__main__':
    try:main()
    except BaseException:
        controller.put('RECOVERY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_replay=True));raise
