"""Focused stdlib AST/mock only. Parent task_and_go executes against RAM stubs.
No real Task/GO/Ready/admission/C file written/read; no PT/SDK/GPU/SSH or locks.
"""
from pathlib import Path,PurePosixPath
import ast,copy,hashlib,json,os,sys,types,traceback
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B))
import w35_posttrain_source_builder_v2 as s
MEM={}
def enc(v):return json.dumps(v,indent=2).encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
class VPath:
    def __init__(self,p):self.p=PurePosixPath(str(p))
    def __str__(self):return str(self.p)
    def __truediv__(self,x):return VPath(self.p/str(x))
    def __eq__(self,x):return str(self)==str(x)
    def resolve(self):return self
    def is_relative_to(self,p):return self.p.is_relative_to(PurePosixPath(str(p)))
    @property
    def suffix(self):return self.p.suffix
    @property
    def name(self):return self.p.name
    def read_bytes(self):return MEM[str(self)]

def loaded_source(path,name):
    raw=Path(path).read_bytes();m=types.ModuleType(name)
    exec(compile(ast.parse(raw.decode('utf-8-sig')),str(path),'exec'),m.__dict__)
    return m

def must_raise(cls,fn):
    try:fn()
    except cls:return
    raise AssertionError('Expected '+cls.__name__)

def ast_constants_and_no_backfill():
    w=loaded_source(B/s.WORKER,'SOURCE_ONLY_WORKER_NOT_MAIN')
    p=loaded_source(B/s.PROTOCOL,'SOURCE_ONLY_PROTOCOL_NOT_MAIN')
    assert (w.SHA,w.BYTES,w.ITER,w.ADAM,w.LR)==(s.SHA,s.BYTES,s.ITER,s.ADAM,s.LR)
    assert (p.SOURCE_SHA,p.SOURCE_BYTES,p.ITER,p.ADAM,p.LR)==(s.SHA,s.BYTES,s.ITER,s.ADAM,s.LR)
    assert w.PRIOR_WINDOW==82 and w.PRIOR_CUMULATIVE==p.PRIOR_UPDATES==162
    assert p.KIND==w.KIND==s.KIND
    tree=ast.parse((B/s.WORKER).read_text(encoding='utf-8-sig'))
    for n in ast.walk(tree):
        if isinstance(n,(ast.Assign,ast.AugAssign,ast.AnnAssign)):
            targets=n.targets if isinstance(n,ast.Assign)else[n.target]
            for t in targets:
                if isinstance(t,ast.Attribute):assert t.attr not in('current_learning_iteration','learning_rate','std_param')
                if isinstance(t,ast.Subscript)and isinstance(t.slice,ast.Constant):assert t.slice.value!='iter'
    calls=[ast.unparse(n.func)for n in ast.walk(tree)if isinstance(n,ast.Call)]
    assert 'original_bounded_learn'in calls and 'runner.learn'not in calls
    assert 'counter.step_returned'in calls and 'counter.after_update'in calls
    text=(B/s.WORKER).read_text(encoding='utf-8-sig')
    assert text.index('assert required_live<=set(live)')<text.index('state=merge_original_omissions(full,live)')
    assert text.index('def log(*args,**kwargs):')<text.index("if stop:save('model_final_complete')")
    # Assignment targets were checked with AST above; do not confuse == with =.
    assert not any(isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='current_learning_iteration' for t in n.targets) for n in ast.walk(tree))
    return dict(actual_8d_consts_checked=True,prior82_and162_distinct=True,no_saved_or_runner_iter_LR_STD_assignment=True,
        original_bounded_learn_preserved=True,known_live_before_merge=True,save_stop_after_logger_boundary=True)

def finite_and_unknown_mock():
    w=loaded_source(B/s.WORKER,'SOURCE_ONLY_COUNTER_MOCK')
    for limit in(1,3,20):
        c=w.FiniteUpdateCounter(limit)
        for _ in range(limit):
            c.before_update()
            for _ in range(20):c.step_returned()
            c.after_update()
        assert c.completed==limit and c.steps==20*limit
        must_raise(AssertionError,c.before_update)
    c=w.FiniteUpdateCounter(20);c.before_update()
    for _ in range(19):c.step_returned()
    must_raise(AssertionError,c.after_update)
    source=dict(unknown=dict(history=[1,2,3]),actor=dict(norm=dict(count=100),w=[1]),cache=dict(old=[0]),iter=32643)
    before=copy.deepcopy(source)
    live=dict(actor=dict(w=[2]),cache=dict(old=[1]),iter=32643)
    merged=w.merge_original_omissions(source,live)
    assert source==before and merged['iter']==live['iter']==32643
    assert merged['unknown']==source['unknown']and merged['actor']['norm']==source['actor']['norm']and merged['cache']==live['cache']
    return dict(mock_only=True,limits=[1,3,20],max_optimizer_returns=400,twenty_first_update_blocked=True,
        wrong19_minibatches_detected=True,source_unchanged_unknown_retained=True,live_raw_iteration_not_relabelled=True)

def parent_w35_join_mock():
    parent_path=B.parent/'parent_source/eight_posttrain_original_owner_v1.py'
    tree=ast.parse(parent_path.read_text(encoding='utf-8-sig'))
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='task_and_go')
    # Extract only source function; no owner main/imports/budget/lock lifecycle.
    parent=types.ModuleType('IN_RAM_PARENT_W35_TASK_GO_MOCK')
    def put(path,value):MEM[str(path)]=enc(value)
    def H(path):return digest(MEM[str(path)])
    def read(path):return json.loads(MEM[str(path)])
    canonical=VPath(s.CANONICAL);MEM[str(canonical)]=enc({'MOCK_NOT_REAL_LEDGER':True})
    parent.__dict__.update(Path=VPath,time=types.SimpleNamespace(time=lambda:1000.),
        os=types.SimpleNamespace(getpid=lambda:700),C=canonical,USD=s.USD,CONTRACT=s.CONTRACT,RESERVE=86412.86069250107,
        put=put,b=types.SimpleNamespace(H=H,read=read),hashlib=hashlib,json=json,require=lambda v,msg: v or (_ for _ in ()).throw(AssertionError(msg)))
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(parent_path),'exec'),parent.__dict__)
    root=VPath('/IN_RAM_MOCK_ONLY/W35');run='MOCK_W35_JOIN'
    for name in(s.WORKER,s.PROTOCOL,s.GPU_CERT_FILE,s.DERIVATION_FILE):MEM[str(root/name)]=(B/name).read_bytes()
    m=dict(kind=s.INSTALL_KIND,source_PT_copied=False,source_model_metadata=s.SOURCE_METADATA,
        asset_USD_SHA=s.USD,asset_contract_SHA=s.CONTRACT,files=[s.source_row(B,n)for n in(s.WORKER,s.PROTOCOL,s.GPU_CERT_FILE,s.DERIVATION_FILE)])
    manifest_file='INSTALL_MOD4V1_POSTTRAIN_ACTUAL.json';MEM[str(root/manifest_file)]=enc(m)
    task,go=s.build_source_templates(job_root=B,run_id=run,role_key='w35_MOCK',manifest_SHA=H(root/manifest_file))
    task['asset_dir']=str(root/'runtime/assets') # same pure builder expression evaluated on future Linux job root
    e=dict(role='W35',source_family='w35',role_key='w35_MOCK',job_root=str(root),source_SHA=s.SHA,
        task_template=task,go_template=go,manifest_file=manifest_file,actual_prior_full20k_proof_file='evidence/PRIOR.mock.json',
        native0pt_evidence_file='evidence/NATIVE.mock.json',target_source_SDK_receipt_file='evidence/SDK.mock.json',
        historical_geometry_evidence_file='evidence/GEOMETRY.mock.json')
    for name in('PRIOR','NATIVE','SDK','GEOMETRY'):MEM[str(root/('evidence/'+name+'.mock.json'))]=enc(dict(MOCK_ONLY=True,passed=True))
    fd=lambda n:types.SimpleNamespace(fileno=lambda:n)
    task,go=parent.task_and_go(e,'MOCK_GPU',dict(authority_generation=s.GENERATION,remaining_training_seconds=999999.,charged_training_seconds=0.),
        run,[31,32],fd(33),fd(34),dict(MOCK_ONLY=True,GPU_UUID='MOCK_GPU'))
    assert task['source_read_purpose']=='NEW_W35_FULL20K_POSTTRAIN20_'+run
    assert task['source_read_plan']==dict(physical_byte_opens=1,decodes=1,source_bytes=s.BYTES)
    assert task['seed']==go['seed']==20260928 and task['steps_per_env']==go['steps_per_env']==24
    protocol=loaded_source(B/s.PROTOCOL,'IN_RAM_W35_PROTOCOL_MOCK')
    seen=[]
    protocol.Path=VPath
    protocol.os=types.SimpleNamespace(environ={'CUDA_VISIBLE_DEVICES':'MOCK_GPU'},getppid=lambda:700,fstat=lambda fd:seen.append(fd))
    protocol.time=types.SimpleNamespace(time=lambda:1000.)
    args=types.SimpleNamespace(mode='train',num_envs=20000,out=root/'production',run_id=run)
    protocol.validate_new_job(task,go,args,root)
    assert seen==[31,32,33,34] and 'derivation_index_SHA'not in m
    for delta in({'source_read_purpose':{'physical_byte_opens':1}}, {'source_SHA':'89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f'},
                  {'source_bytes':17621509},{'source_prior_window_PPO_updates':162},{'source_prior_cumulative_PPO_updates':82},
                  {'seed':42},{'source_LR':.00011390625000000006}):
        bad=dict(task,**delta);must_raise(ValueError,lambda:protocol.validate_new_job(bad,go,args,root))
    old=loaded_source(B.parent/'source_w35/mod4v1_w35_posttrain_protocol_v1.py','OLD_SOURCE_CONTRACT_NEGATIVE')
    old.Path=VPath;old.os=protocol.os;old.time=protocol.time
    must_raise(ValueError,lambda:old.validate_new_job(task,go,args,root))
    return dict(actual_parent_function_source=str(parent_path),mock_RAM_only=True,
        parent_task_go_W35_branch_to_v2_protocol_join_passed=True,
        old_v1_same_parent_join_reproduced_failure=True,generic_manifest_no_top_derivSHA_supported=True,
        actual_fd_or_C_operations=0,no_disk_Task_GO_Ready_admission_files=True,
        source_proof_is_historical_not_new_live_training=True)

def builder_and_index_checks():
    index=json.loads((B/s.DERIVATION_FILE).read_bytes())
    assert index['kind']==s.DERIVATION_KIND and index['source_model_metadata']['SHA']==s.SHA
    assert {r['relative']for r in index['outputs']}=={s.WORKER,s.PROTOCOL}
    assert 'MOD4V1_DERIVATION_INDEX.json'not in{r['relative']for r in index['outputs']}
    t,g=s.build_source_templates(job_root=B,run_id='DRAFT',role_key='w35_DRAFT',manifest_SHA='0'*64)
    assert t['owner_parent_pid']==g['original_owner_pid']==0 and not t['inherited_lock_fds']
    assert g['learning_started_epoch']==0 and t['root_admission_SHA']==g['root_admission_SHA']=='0'*64
    required=json.loads((B/'W35_REQUIRED_PARENT_FIELDS_V2.json').read_bytes())
    assert set(required['Task_required'])<=set(t) and set(required['GO_required'])<=set(g)
    proof=json.loads((B/'evidence/W35_NEW8D_FULL20K_CLOSED_HISTORY_PROOF_V2.json').read_bytes())
    assert proof['actual_not_mock'] and proof['source_SHA']==s.SHA and proof['asset_USD_SHA']==s.USD and proof['asset_contract_SHA']==s.CONTRACT
    assert proof['num_envs']==20000 and proof['whole_state_restore_passed'] and proof['all_own_children_waited'] and proof['returncode']==0
    assert proof['certificate_remote_path']==proof['remote_root']+'/actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json'
    for ref in proof['raw_byte_refs']:
        raw=(B/ref['relative']).read_bytes();assert len(raw)==ref['bytes'] and digest(raw)==ref['SHA']
    assert proof['current_training_live_restore_already_passed']is False
    return dict(exact_parent_interfaces=True,source_derivation_outputs_only_new_worker_protocol=True,
        Drafts_only_in_source_data_not_live_files=True,required_fields_complete=True,
        historical_whole20k_proof_same_root_closed_RC0_allwait_joined=True,no_new_live_training_pass_claim=True)


def main():
    results=[]
    for name,fn in [('actual_8d_constants_and_raw_counter_AST',ast_constants_and_no_backfill),
        ('finite_original_counter_and_unknown_tree_mock',finite_and_unknown_mock),
        ('original_parent_W35_branch_full_field_join_RAM_mock',parent_w35_join_mock),
        ('new_derivation_and_complete_source_builder',builder_and_index_checks)]:
        try:results.append(dict(name=name,passed=True,detail=fn()))
        except BaseException:results.append(dict(name=name,passed=False,error=traceback.format_exc()))
    result=dict(status='SOURCE_ONLY_AST_MOCK_NOT_SDK_PPO_OR_READY',all_passed=all(r['passed']for r in results),tests=results,
        PT_open_stat_hash_decode=0,actual_Torch_SDK_GPU_PPO_calls=0,C_GO_Ready_or_actual_admission_operations=0,
        actual_lock_or_owner_lifecycle_operations=0,SSH_Git_new_agents=0,old_source_or_parent_edits=False)
    with (B/'W35_SOURCE_AST_MOCK_REVIEW_V2_FINAL_SEALED.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
    if not result['all_passed']:raise SystemExit(1)
if __name__=='__main__':main()
