"""Use existing authenticated host access; transfer only this task's sources."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shlex
import time
import zipfile
import sys


def main():
    local=Path(sys.argv[1]);local.mkdir(parents=True,exist_ok=True)
    sources=Path(__file__).resolve().parent
    root=Path('F:/RMPOLAR-RL/mod4v3_scut_semantics_20261106')
    task=Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103')
    sys.path.insert(0,str(task/'scut_native_v36'))
    from host_access import connect
    from host86_prepare import query
    client,restore,python=connect('72')
    try:
        base='/home/lc01/Zonglin Li/zonglin2'
        remote=base+'/tasks/MOD4V3_PHYSX_WARP_STANDING_'+str(time.time_ns())
        sftp=client.open_sftp()
        def mkdir(path):
            parts=PurePosixPath(path).parts
            current='/'
            for part in parts[1:]:
                current=str(PurePosixPath(current)/part)
                try:sftp.mkdir(current)
                except OSError:sftp.stat(current)
        mkdir(remote+'/code/mod4v3_ppo')
        rows=[]
        for path in sources.glob('*.py'):
            if path.name=='deploy.py':continue
            dst=remote+'/code/mod4v3_ppo/'+path.name;sftp.put(str(path),dst)
            rows.append(dict(source=str(path),destination=dst,SHA=hashlib.sha256(path.read_bytes()).hexdigest()))
        sftp.put(str(task/'scut_native_v40_easy_stand/easy_terrain.py'),remote+'/code/easy_terrain.py')
        archive=root/'MOD4v3_HW300N60_SCUT_semantics_R3.zip'
        sftp.put(str(archive),remote+'/asset.zip')
        code='import pathlib,zipfile,json;root=pathlib.Path('+repr(remote)+');z=zipfile.ZipFile(root/"asset.zip");z.extractall(root/"asset");print(json.dumps(z.namelist()[:8]))'
        listing=query(client,python,code)
        # The release archive contains the portable package at its top level.
        asset=query(client,python,'import pathlib,json;root=pathlib.Path('+repr(remote)+');print(json.dumps(str(next((root/"asset").rglob("runtime_config.json")).parent)))')
        plan=dict(run_id=Path(remote).name,remote_root=remote,host='72',python=base+'/run-python.sh',
            runtime=base+'/tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400/runtime/isaac/mod4',
            shared_package=base+'/tasks/MOD4V1_SCUT_STEP270_2H_1793711274668684600/package',
            package=asset,support=remote+'/code',
            source_paths=base+'/tasks/MOD4V1_SCUT_STEP270_2H_1793711274668684600/env20000_1h/SOURCE_PATHS.json',
            reset_bank=base+'/tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400/runtime/isaac/mod4/reset_bank.json',
            GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',
            gpu_lock=base+'/state/three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock',
            seed=66,num_envs=4096,seconds=3600,
            algorithm='PPO',backend='PhysX TGS32/4',sampling='Warp fused closure/mimic preallocated CUDA Graph',
            supermimic=False,full_DR=False,initialization='fresh actor/critic/STD/Adam; v3 semantic action order',
            target=dict(vx=.35,L0=.334,theta=-2.),
            asset_identity=dict(zip_SHA=hashlib.sha256(archive.read_bytes()).hexdigest(),
                usd_SHA='e057969b136fd75613bb8d77985d43d043f54faae62dc060afb718ebabbe1c1c'),
            source_files=rows,prior_work_order=str(task/'CURRENT_WORK_ORDER.json'))
        (local/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        sftp.put(str(local/'PLAN.json'),remote+'/PLAN.json')
        bootstrap='import runpy,sys;sys.path.insert(0,'+repr(remote+'/code')+');sys.argv=["owner",'+repr(remote+'/PLAN.json')+'];runpy.run_module("mod4v3_ppo.owner",run_name="__main__")'
        command='nohup '+shlex.quote(python)+' -B -c '+shlex.quote(bootstrap)+' > '+shlex.quote(remote+'/owner.log')+' 2>&1 < /dev/null &'
        i,o,e=client.exec_command(command,timeout=20);i.close();o.channel.recv_exit_status()
        sftp.close();print(json.dumps(dict(remote_root=remote,plan=str(local/'PLAN.json'),submitted=True)))
    finally:client.close();restore()


if __name__=='__main__':main()
