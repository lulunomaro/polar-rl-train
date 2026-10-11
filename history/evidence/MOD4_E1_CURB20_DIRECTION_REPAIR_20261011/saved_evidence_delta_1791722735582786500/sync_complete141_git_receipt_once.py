from direction_io import *

p=R/'COMPLETE141_STAGE_GIT_RECORDED.json';raw=p.read_bytes();v=json.loads(raw)
assert v['remote_main_tag_peeled_verified'] and not v['push_pending']
n,w=io.connect_both()
try:
    path=io.E+'/reports/E1_CURB20_DIRECTION141_WAVE_EXPOSURE_STAGE_GIT_RECORDED.json'
    with n.open_sftp() as f:
        io.put(f,path,raw)
        with f.open(path,'rb') as q:assert q.read()==raw
    save('COMPLETE141_STAGE_GIT_RECEIPT_CENTRAL_BYTES_VERIFIED.json',dict(epoch=time.time(),actual_central_path=path,bytes=len(raw),sha256=H(raw),source_commit=v['commit'],source_tag=v['tag'],actual_bytes_exact=True,no_GPU_PPO_or_budget_write=True))
    print(json.dumps(dict(central_receipt_exact=True,commit=v['commit'])))
finally:io.cleanup(n,w)
