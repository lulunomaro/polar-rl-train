"""Resume only unused Fudan admission when the actual original peer has closed."""
from pathlib import Path
import hashlib,importlib.util,json,os,time,traceback

N=Path(__file__).resolve().parent
A=N/'fudan_jump_final357_1h'
R=A/'reports'
read=lambda p:json.loads(Path(p).read_bytes())

def put(name,value):
    with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False)

def main():
    assert not(R/'LAUNCH_ONCE.json').exists()and not(A/'INDEX_SOURCE_FROZEN.json').exists()
    context=read(R/'CANONICAL_PEER_CONTEXT.json')
    put('PEER_RELEASE_RESUME_ONCE.json',dict(epoch=time.time(),pid=os.getpid(),
        original_false_preserved=True,only_unused_admission=True,peer=context['run_id']))
    boundary=context['GO']['nominal_end_epoch']+120
    metadata=Path(context['local_metadata'])
    while True:
        actual=read(metadata)
        rows=actual.get('metadata',{})
        released=rows.get('OWNER_EXIT_ACTUAL.json')or{}
        waited=rows.get('OUTER_OWNER_WAIT_ACTUAL.json')or{}
        if(released.get('original_cost_settled')and released.get('all_own_children_waited')
           and released.get('original_private_finite_authority_leases_released')
           and waited.get('original_owner_reaped')):
            break
        if time.time()>=boundary:
            put('PEER_RELEASE_STILL_PENDING.json',dict(epoch=time.time(),peer=context,
                reason='Original actual owner has no terminal release receipt after fixed nominal; no launch/canonical mutation'))
            return
        time.sleep(min(15,boundary-time.time()))
    put('PEER_RELEASE_LOCAL_ACTUAL.json',dict(epoch=time.time(),path=str(metadata),
        bytes=metadata.stat().st_size,SHA=hashlib.sha256(metadata.read_bytes()).hexdigest(),
        release=released,waited=waited))
    admission=R/'admission_resume01';admission.mkdir()
    with(admission/'RELEASED_PEER_CONTEXT.json').open('x',encoding='utf8')as f:
        json.dump(dict(released_peer=context['remote_root'],released_peer_pid=context['owner_pid'],
            actual_exit=released,actual_wait=waited,only_unused_admission_resumed=True),f,indent=2)
    spec=importlib.util.spec_from_file_location('fudan_original_controller',N/'fudan_control.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.HERE=A;module.REPORTS=R;module.ADMISSION_REPORTS=admission
    module.launch()

if __name__=='__main__':
    try:main()
    except BaseException:
        put('FUDAN_RESUME_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
