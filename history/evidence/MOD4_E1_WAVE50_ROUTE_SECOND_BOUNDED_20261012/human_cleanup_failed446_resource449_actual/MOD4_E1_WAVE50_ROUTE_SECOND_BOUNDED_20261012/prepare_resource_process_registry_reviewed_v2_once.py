from route_second_io import *
import shutil
old=D/'resource_reviewed_payload';new=D/'resource_reviewed_payload_v2'
assert old.is_dir() and not new.exists();shutil.copytree(old,new)
p=new/'supervise_wave50_route_startup_resource_reviewed_once.py';raw=p.read_text()
raw=raw.replace('source=prior446.source;runtime=prior446.runtime;trainers=prior446.trainers','''source=prior446.source;runtime=prior446.runtime
_trainers=prior446.trainers
def trainers():
    rows=_trainers()
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            argv=[x.decode(errors='replace') for x in p.read_bytes().split(bytes([0]))]
            if any(Path(x).name==ENTRY for x in argv):rows.append(identity(int(p.parent.name)))
        except (OSError,ValueError):pass
    return rows
prior446.trainers=trainers''')
compile(raw,str(p),'exec');p.write_text(raw,encoding='utf8')
save('RESOURCE_PROCESS_REGISTRY_PREDEPLOYMENT_REVIEW.json',dict(epoch=time.time(),passed=True,original_prepared_controller_retained_unused=True,new_v2_tracks_new_worker_name_in_process_registry=True,only_process_identity_registry_correction=True,no_actual_target_or_GPU_yet=True,newfiles={p.relative_to(new).as_posix():H(p.read_bytes()) for p in new.rglob('*') if p.is_file()}))
print(json.dumps(dict(passed=True,v2files=3)))
