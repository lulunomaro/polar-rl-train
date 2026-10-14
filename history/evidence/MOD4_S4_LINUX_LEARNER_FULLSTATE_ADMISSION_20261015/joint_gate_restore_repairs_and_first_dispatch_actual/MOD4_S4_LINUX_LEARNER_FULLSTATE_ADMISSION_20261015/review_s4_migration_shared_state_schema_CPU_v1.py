"""Negative schemas and owned cache disk checks. No SDK/GPU/optimizer update."""
from pathlib import Path
import os,sys,json,copy,torch,tempfile,time,ast
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;W=D.parent
sys.path[:0]=[str(D),str(W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015'),str(W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014')]
from tensordict import TensorDict
from s4_original_fullstate_migration_v1 import SharedControlState,SCHEMA,verify_original_restore,sha

def main():
    n=13;x=torch.zeros(n,35);x[:,28]=1
    td=TensorDict(dict(policy=x,critic=torch.zeros(n,38)),batch_size=[n]);s=SharedControlState(td)
    z=torch.arange(n)%2;s.begin(td,z)
    raw=torch.sin(torch.arange(n*6).reshape(n,6).float())
    end=torch.arange(n)%3==0;next_td=td.clone();next_td['policy'][:,22:28]=raw;next_td['policy'][end,22:28]=0
    s.finish(raw,raw,end,next_td)
    out=D/'S4_SHARED_STATE_CPU_FIXTURE.pt';assert not out.exists();torch.save(s.save(),out)
    new=SharedControlState(td);new.restore(torch.load(out,map_location='cpu',weights_only=False))
    assert torch.equal(new.cache['policy'],next_td['policy']) and torch.equal(new.previous,next_td['policy'][:,22:28])
    assert new.completed_controls==1 and (new.z[end]==-1).all()
    bad=0
    # Exact typed original receipts, including legacy exact flags, no passed field.
    fixture=D/'original_receipt_schema_CPU_fixture';assert not fixture.exists();fixture.mkdir()
    source=fixture/'NOT_A_TRAINING_SOURCE.txt';source.write_text('CPU receipt schema only')
    receipt={name:dict(pid=os.getpid(),source_sha256=sha(source),PhysX_exact_resume_claimed=False,**{k:True for k in fields}) for name,fields in SCHEMA.items()}
    def write(rows):
        for name,v in rows.items():(fixture/name).write_text(json.dumps(v))
    write(receipt);verify_original_restore(fixture,source)
    for name,fields in SCHEMA.items():
        for field in (*fields,'pid','source_sha256','PhysX_exact_resume_claimed'):
            rows=copy.deepcopy(receipt)
            rows[name][field]=False if field in fields else (-1 if field=='pid' else '0'*64 if field=='source_sha256' else True)
            write(rows)
            try:verify_original_restore(fixture,source)
            except AssertionError:bad+=1
            else:raise AssertionError('Bad receipt accepted '+name+':'+field)
    write(receipt)
    tree=ast.parse((D/'s4_linux20k_missing_native_fullstate_worker_v1.py').read_text())
    text=(D/'s4_linux20k_missing_native_fullstate_worker_v1.py').read_text()
    assert text.index('old=resume_e1_new_episode')<text.index('runtime_state,proof=migrate_first')
    assert 'run_name=\'s4_original_configuration_only\'' in text
    for p in (D/'s4_missing_native_fullstate_parent_v1.py',D/'s4_original_fullstate_migration_v1.py',D/'s4_linux20k_missing_native_fullstate_worker_v1.py'):compile(p.read_bytes(),str(p),'exec')
    report=dict(epoch=time.time(),passed=True,typed_original_receipt_files=len(SCHEMA),typed_negative_cases=bad,
        original_no_generic_passed_field_schema=True,selected_reset_previous_actual_action_cache_disk_roundtrip=True,
        original_fullrestore_precedes_explicit_new_gate_critic_optimizer=True,synthetic_CPU_only=True,
        optimizer_updates=0,GPU=False,target_native_fullstate_pending=True,learning_admitted=False)
    p=D/'reports/S4_MIGRATION_ORIGINAL_TYPED8_AND_SHARED_STATE_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(passed=True,report=str(p),bad_cases=bad,typed_files=len(SCHEMA))))
if __name__=='__main__':main()
