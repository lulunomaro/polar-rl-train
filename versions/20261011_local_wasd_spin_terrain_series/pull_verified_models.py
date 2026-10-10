"""Read-only exact-SHA checkpoint pull for the human-requested local player."""
from pathlib import Path
import hashlib, importlib.util, json, os, sys, time

D = Path(__file__).resolve().parent
W = D.parent
sys.path.insert(0, str(W / 'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''): h.update(block)
    return h.hexdigest()

def main():
    if (D/'DOWNLOAD_RECEIPT.json').exists():
        raise RuntimeError('Already pulled; use the existing receipt and files.')
    spec = importlib.util.spec_from_file_location('authorized_transport', W/'RM2026_TERRAIN_AUDIT_20261009/reuse_authorized_session_transport.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    secret, _ = helper.recover('RM_SSH_PASSWORD')
    if not secret: raise RuntimeError('Previously authorized connection unavailable')
    os.environ['RM_SSH_PASSWORD'] = secret
    specs = [
        dict(id='e0', label='E0 平地 / 小陀螺 · D7 31903', status='已审 D7 冻结源；本地 MuJoCo 转移需单独验证', sha256='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8', path='/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009/learning_logs/2026-10-09_09-45-49_d7_stable_block1_1791510179560330441/model_31903.pt'),
        dict(id='terrain', label='地形保留源 · 364 / 32063 / 3c97', status='完整129审查；35mm前24/27倒27/27；不是已合格整套MoE', sha256='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e', path='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_EPISODE_REVIEWED_20261010/learning_logs/2026-10-10_21-38-00_e1_G3_command_retention_observation_1791639283265084900/model_32063.pt'),
        dict(id='wave_candidate', label='E1_WAVE 候选 · 366 / 32068 / 2b4', status='131前22/27倒25/27；未合格，手动对照用', sha256='2b4f5a575d3a4d97013b331e215c503ab86e528a63a92d719a3366a684b52284', path='/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010/learning_logs/2026-10-10_23-45-35_e1_wave_G3_isolated_observation_1791646939142916742/model_32068.pt'),
    ]
    receipt = dict(epoch=time.time(), task='human local WASD spin and terrain series', host='authorized 4090', remote_mutations=0, CUDA_initialization=False, canonical_mutations=0, models=[])
    client = None
    try:
        client=connect(); sftp=client.open_sftp()
        (D/'models').mkdir(exist_ok=True)
        for item in specs:
            target=D/'models'/(item['id']+'.pt')
            if target.exists():
                raise RuntimeError('New pull must not overwrite: '+str(target))
            remote_size=sftp.stat(item['path']).st_size
            with sftp.open(item['path'],'rb') as src, target.open('xb') as dst:
                while True:
                    b=src.read(1024*1024)
                    if not b: break
                    dst.write(b)
            actual=sha(target)
            assert target.stat().st_size==remote_size and actual==item['sha256'], item['id']
            item.update(local_path=str(target), bytes=remote_size, local_sha256=actual)
            receipt['models'].append(item)
            print(item['id'],remote_size,actual,flush=True)
        sftp.close()
        (D/'DOWNLOAD_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    finally:
        if client: client.close()
        os.environ.pop('RM_SSH_PASSWORD',None)

if __name__=='__main__': main()
