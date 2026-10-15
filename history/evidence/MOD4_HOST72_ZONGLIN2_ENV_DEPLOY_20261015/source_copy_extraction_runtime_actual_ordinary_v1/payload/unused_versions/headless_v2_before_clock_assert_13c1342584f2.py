"""Finite deployment checks only: two sequential tiny CUDA checks and one SDK startup.

This is not a MOD4 task, physical contract, policy evaluation, PPO or fullstate restore.
No deletion, process signals, driver/system mutation or parallel GPU workers.
"""
from pathlib import Path
import fcntl
import json
import os
import subprocess
import sys
import time

ROOT = Path('/home/lc01/Zonglin Li/zonglin2')


def put(name, value):
    with (ROOT / 'audit' / name).open('x') as f:
        json.dump(value, f, indent=2)


TORCH_CODE = r'''
from pathlib import Path
import json,os,time,torch
root=Path('/home/lc01/Zonglin Li/zonglin2');gpu=int(os.environ['ZONGLIN2_PHYSICAL_GPU'])
assert torch.cuda.is_available() and torch.cuda.device_count()==1
x=torch.arange(16,dtype=torch.float32,device='cuda:0').reshape(4,4)
y=x*2+1;torch.cuda.synchronize()
expected=torch.arange(16,dtype=torch.float32).reshape(4,4)*2+1
assert torch.equal(y.cpu(),expected) and bool(torch.isfinite(y).all())
v=dict(epoch=time.time(),passed=True,physical_GPU=gpu,visible_CUDA_devices=torch.cuda.device_count(),
 name=torch.cuda.get_device_name(0),torch=torch.__version__,built_CUDA=torch.version.cuda,
 tensor_shape=[4,4],actual_tiny_CUDA_elementwise_kernel_and_CPU_result_exact=True,
 not_performance_benchmark_MOD4_physics_or_training=True)
with (root/('audit/TORCH_GPU'+str(gpu)+'_TINY_KERNEL_COMPLETE_ACTUAL.json')).open('x') as f:json.dump(v,f,indent=2)
print(json.dumps(v),flush=True)
'''

SDK_CODE = r'''
from pathlib import Path
import json,time
import sys,isaacsim
from isaacsim import SimulationApp
sys.argv += ['--/app/renderer/enabled=false','--/renderer/enabled=false','--/app/window/enabled=false','--/app/livestream/enabled=false']
headless=Path(isaacsim.__file__).parent/'apps/isaacsim.exp.base.python.physics.headless.kit'
config=dict(headless=True,hide_ui=True,width=64,height=64,multi_gpu=False,active_gpu=0,physics_gpu=0,disable_viewport_updates=True)
app=SimulationApp(config,experience=str(headless)) if headless.is_file() else SimulationApp(config)
from isaacsim.core.api import World
from pxr import UsdGeom,UsdPhysics,Gf
import omni.usd
world=World(physics_dt=.0025,rendering_dt=.01,stage_units_in_meters=1.0,backend='numpy',device='cpu')
stage=omni.usd.get_context().get_stage()
ground=UsdGeom.Cube.Define(stage,'/World/OwnedProbeGround');ground.CreateSizeAttr(1.)
ground.AddScaleOp().Set(Gf.Vec3f(10.,10.,.1));ground.AddTranslateOp().Set(Gf.Vec3d(0.,0.,-.5))
UsdPhysics.CollisionAPI.Apply(ground.GetPrim())
box=UsdGeom.Cube.Define(stage,'/World/OwnedProbeBox');box.CreateSizeAttr(.1)
box.AddTranslateOp().Set(Gf.Vec3d(0.,0.,1.))
UsdPhysics.CollisionAPI.Apply(box.GetPrim());UsdPhysics.RigidBodyAPI.Apply(box.GetPrim())
world.reset()
for i in range(24):world.step(render=False)
v=dict(epoch=time.time(),passed=True,SDK_SimulationApp_constructed=True,own_primitive_scene_steps=24,
 actual_physics_dt=world.get_physics_dt(),headless=True,multi_gpu=False,rendering_disabled_supported_SDK_flags=True,physics_headless_experience=str(headless) if headless.is_file() else None,
 SDK_only_CPU_PhysX_primitive_scene=True,not_MOD4_GPU_PhysX_query_contact_hardware_or_fullstate_admission=True,
 no_policy_optimizer_training_or_budget=True)
with (Path('/home/lc01/Zonglin Li/zonglin2')/'audit/SDK_PRIMITIVE_PROBE_DATA_COMPLETE_ACTUAL.json').open('x') as f:json.dump(v,f,indent=2)
print(json.dumps(v),flush=True)
app.close()
'''


def identity(pid):
    try:
        stat=(Path('/proc')/str(pid)/'stat').read_text()
        ticks=int(stat.rsplit(') ',1)[1].split()[19])
        boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '))
        return dict(pid=pid,creation_ticks=ticks,creation_epoch=boot+ticks/os.sysconf('SC_CLK_TCK'),actual_cmdline=(Path('/proc')/str(pid)/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace'))
    except FileNotFoundError:
        return dict(pid=pid,already_exited_before_identity_snapshot=True)


def launch(script_name, code, launcher, gpu, timeout):
    p = ROOT / 'audit' / script_name
    assert not p.exists()
    p.write_text(code)
    env = dict(os.environ)
    env.update(CUDA_VISIBLE_DEVICES=str(gpu), ZONGLIN2_PHYSICAL_GPU=str(gpu),
               ISAACSIM_ACCEPT_EULA='Y', OMNI_KIT_ACCEPT_EULA='YES')
    stdout_path = ROOT / 'logs' / (script_name + '.stdout.log')
    stderr_path = ROOT / 'logs' / (script_name + '.stderr.log')
    with stdout_path.open('xb') as out, stderr_path.open('xb') as err:
        child = subprocess.Popen([str(launcher), str(p)], cwd=ROOT, env=env, stdout=out, stderr=err)
        put(script_name + '_STARTED.json', dict(epoch=time.time(), pid=child.pid, argv=[str(launcher), str(p)],
            physical_GPU=gpu, actual_process_identity=identity(child.pid), output_paths=[str(stdout_path),str(stderr_path)], own_deployment_test_only=True))
        try:
            rc = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            put(script_name + '_TIMEOUT_NO_SIGNAL.json', dict(epoch=time.time(), pid=child.pid,
                no_kill_signal_or_second_worker_launched=True, actual_own_process_state_required=True))
            raise
    v = dict(epoch=time.time(), pid=child.pid, returncode=rc, parent_wait_confirmed_child_exit=True,
        stdout=str(stdout_path), stderr=str(stderr_path), no_PPO_budget_or_process_signal=True)
    put(script_name + '_EXIT_ACTUAL.json', v)
    print(json.dumps(v), flush=True)
    assert rc == 0, stderr_path.read_text(errors='replace')[-12000:]


def main():
    assert ROOT.resolve() == ROOT
    assert not (ROOT / 'audit/FINITE_DEPLOYMENT_VALIDATION_V2_HEADLESS_STARTED.json').exists()
    compat = ROOT / 'run-python-compat.sh'
    launcher = compat if compat.exists() else ROOT / 'run-python-native.sh'
    assert launcher.is_file()
    p = subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],
        capture_output=True,text=True,check=True)
    assert not p.stdout.strip(), 'Existing compute processes: do not launch deployment checks.'
    with (ROOT / 'state/finite_environment_validation.lock').open('xb') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        put('FINITE_DEPLOYMENT_VALIDATION_V2_HEADLESS_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),launcher=str(launcher),actual_process_identity=identity(os.getpid()),
            two_tiny_CUDA_tests_sequential_then_one_CPU_PhysX_SDK_probe=True,no_training_MOD4_admission_or_budget=True))
        for gpu in (0,1):
            launch('owned_torch_gpu'+str(gpu)+'_tiny_v2.py',TORCH_CODE,launcher,gpu,90)
        launch('owned_SDK_primitive_probe_v2_headless.py',SDK_CODE,launcher,0,180)
        for name in ('TORCH_GPU0_TINY_KERNEL_COMPLETE_ACTUAL.json','TORCH_GPU1_TINY_KERNEL_COMPLETE_ACTUAL.json',
                     'SDK_PRIMITIVE_PROBE_DATA_COMPLETE_ACTUAL.json'):
            assert json.loads((ROOT/'audit'/name).read_bytes())['passed']
        put('FINITE_DEPLOYMENT_VALIDATION_V2_HEADLESS_COMPLETE.json',dict(epoch=time.time(),passed=True,
            both_actual_tiny_CUDA_kernels_passed=True,SDK_headless_primitive_scene24_steps_passed=True,
            all_three_children_actual_waited_exit0=True,private_validation_lock_held_until_complete=True,
            no_MOD4_GPU_PhysX_fullstate_policy_PPO_budget_or_performance_claim=True))
        fcntl.flock(lock, fcntl.LOCK_UN)
    print(json.dumps(dict(deployment_checks_passed=True,no_training_or_MOD4_qualification=True)),flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        import traceback
        put('FINITE_DEPLOYMENT_VALIDATION_V2_HEADLESS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),
            error=traceback.format_exc(),no_system_driver_delete_signal_or_blind_replay=True))
        raise
