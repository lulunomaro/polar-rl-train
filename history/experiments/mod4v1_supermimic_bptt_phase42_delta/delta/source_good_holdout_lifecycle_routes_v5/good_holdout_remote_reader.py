"""Future read-only good-holdout metadata routes; no native/main call on import.

Own complete JSON is hashed, parsed once and kept in one cache. Unlike Phase1,
there is no FINAL projection: rows, metrics, source_cache and unknown fields stay.
Original producer source-grade and independent outer actual wait remain separate.
"""
from pathlib import Path
import hashlib
import importlib
import json
import os
import stat
import sys
import time
import good_holdout_contract as C

BIG = ('FINAL.json', 'TERMINAL_ROWS.json') + tuple('cases/'+r+'/FINAL.json' for r in C.REQUESTED)
GROUP_SMALL = ('GROUP_PLAN.json', C.STAGE_NAME, C.STARTED, C.DISPATCH, C.WAITED, C.ERROR,
    'PARENT_STARTED.json', 'ACTUAL_GROUP_ADMISSION.json', 'CHILDREN.json',
    'GROUP_BARRIER_STATUS.json', 'GROUP_EVAL_START.json', 'BOUNDED_ORIGINAL_RESOURCE_WAIT.json',
    'GROUP_ABORT.json', 'GROUP_STARTUP_ABORT.json', 'PARENT_ORIGINAL_ERROR.json',
    'PARENT_EXIT_SCOPE.json', C.GRADE)
CASE_SMALL_NAMES = ('task.json', 'WORKER_SCENE_READY.json', 'WORKER_EVAL_STARTED.json', 'PRE_CLOSE.json',
    'ENV_CLOSE_RETURNED_A1_EVAL_V2.json', 'APP_CLOSE_RETURNED_A1_EVAL_V2.json',
    'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json', 'WORKER_ERROR.json')
SMALL = GROUP_SMALL + tuple('cases/'+r+'/'+name for r in C.REQUESTED for name in CASE_SMALL_NAMES)
LOGS = ('GOOD_HOLDOUT_CONTROLLER_STDOUT_STDERR.log', 'GOOD_HOLDOUT_PARENT_FULL_STDOUT_STDERR.log') + tuple('cases/'+r+'/SDK_FULL_STDOUT_STDERR.log' for r in C.REQUESTED)
MUTABLE = {'GROUP_BARRIER_STATUS.json', 'BOUNDED_ORIGINAL_RESOURCE_WAIT.json'}
FORBIDDEN = {'torch','numpy','isaaclab','isaacsim','omni','pxr','carb','warp','rsl_rl','tensordict','psutil','fcntl'}


def maximum(name):
    if name in ('cases/CURB_PROTECTED878/FINAL.json', 'cases/SLOPE135/FINAL.json'):
        return C.CASE_FINAL_MAX
    if name == 'GROUP_PLAN.json' or name.startswith('cases/'):
        return C.PLAN_MAX
    return C.GROUP_MAX


class MetadataReader:
    """Allowlisted own metadata; complete terminal files have one read attempt."""
    def __init__(self, root):
        self.root=Path(root); self.cache={}; self.info={}; self.signatures={}; self.errors=[]; self.raw_cache={}
        self.secondary_errors={r:[] for r in C.REQUESTED}

    def path(self, name):
        C.need(name in SMALL+BIG+LOGS, 'nonmetadata alias rejected')
        path=self.root/name
        C.need(not self.root.is_symlink() and path.resolve().is_relative_to(self.root.resolve()), 'own metadata escapes root')
        cursor=path
        while cursor!=self.root:
            C.need(not cursor.is_symlink(), 'metadata ancestor symlink rejected')
            cursor=cursor.parent
        return path

    def read(self, name, *, terminal=False):
        C.need(name in SMALL+BIG, 'metadata alias rejected')
        if name in BIG:
            C.need(terminal, 'whole FINAL reads only at terminal/cap')
        try:
            path=self.path(name); before=path.stat()
            C.need(stat.S_ISREG(before.st_mode), 'metadata not regular')
            signature=(before.st_size,before.st_mtime_ns)
            if name in BIG and self.info.get(name,{}).get('read_count',0):
                C.need(name in self.cache and self.signatures.get(name)==signature,
                       'immutable terminal metadata changed after its sole read: '+name)
                return self.cache[name]
            if name in self.cache and self.signatures[name]==signature:
                return self.cache[name]
            C.need(name not in self.cache or name in MUTABLE, 'immutable metadata changed: '+name)
            limit=maximum(name); C.need(before.st_size<=limit, 'original metadata bound exceeded: '+name)
            count=self.info.get(name,{}).get('read_count',0)+1
            self.info[name]=dict(status='READ_ATTEMPTED',read_count=count,bytes=before.st_size,SHA256=None)
            with path.open('rb') as stream: raw=stream.read(limit+1)
            after=path.stat()
            C.need(len(raw)<=limit and len(raw)==before.st_size and (after.st_size,after.st_mtime_ns)==signature,
                   'metadata changed during complete bounded read: '+name)
            value=json.loads(raw)
            self.info[name].update(status='READ',SHA256=C.H(raw),whole_JSON_read=True,
                terminal_full_original_bytes=name in BIG,projection_applied=False)
            self.cache[name]=value; self.signatures[name]=signature
            if name in ('GROUP_PLAN.json',C.STAGE_NAME): self.raw_cache[name]=raw
            return value
        except FileNotFoundError:
            if name in self.cache or self.info.get(name,{}).get('read_count',0):
                self.errors.append(dict(file=name,error='immutable metadata disappeared after observation: '+name))
                self.info.setdefault(name,dict(read_count=0,bytes=None,SHA256=None))['status']='ERROR'
            else:
                self.info.setdefault(name,dict(status='MISSING',read_count=0,bytes=None,SHA256=None))
        except Exception as exc:
            self.errors.append(dict(file=name,error=type(exc).__name__+': '+str(exc)))
            self.info.setdefault(name,dict(read_count=0,bytes=None,SHA256=None))['status']='ERROR'
        return None

    def observe_secondary_errors(self):
        for role in C.REQUESTED:
            directory=self.root/'cases'/role
            if not directory.exists(): continue
            C.need(not directory.is_symlink() and directory.resolve().is_relative_to(self.root.resolve()),'secondary error directory escapes root')
            names=sorted(p.name for p in directory.glob('WORKER_ERROR_SECONDARY_*.json'))
            C.need(len(names)<=128,'bounded secondary error inventory exceeded')
            self.secondary_errors[role]=names  # Presence alone blocks qualification; no unrelated files are read.

    def tail(self, name, limit=16384):
        try:
            path=self.path(name); info=path.stat(); C.need(stat.S_ISREG(info.st_mode),'log not regular')
            with path.open('rb') as stream:
                stream.seek(max(0,info.st_size-limit)); raw=stream.read(limit)
            return dict(source_bytes=info.st_size,bytes_read=len(raw),tail=raw.decode('utf-8','replace'))
        except FileNotFoundError:
            return dict(source_bytes=None,bytes_read=0,tail=None)
        except Exception as exc:
            return dict(source_bytes=None,bytes_read=None,tail=None,error=type(exc).__name__+': '+str(exc))


def load_metadata_closure(root):
    """Import WHOLE fixed original good20 metadata modules, not a selected AST.

    The native parent, original worker main, factories and actor are never called.
    No old producer file grader is called: its published original grade is retained.
    """
    C.require_final_pins(); root=Path(root)
    C.need(root.is_dir() and not root.is_symlink(), 'actual staged own root required')
    checked=[]; parent_raw=None
    for relative,pin in C.OVERLAY_PINS.items():
        path=root/relative
        C.need(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),'good20 SOURCE alias escapes root')
        with path.open('rb') as stream: raw=stream.read(pin[0]+1)
        C.need((len(raw),C.H(raw))==tuple(pin),'whole fixed good20 SOURCE differs: '+relative)
        checked.append(dict(relative=relative,bytes=len(raw),SHA256=C.H(raw)))
        if relative==C.PARENT_NAME: parent_raw=raw
    sys.dont_write_bytecode=True; sys.path[:0]=[str(root),str(root/'worker_sources/e1')]
    def audit(event,args):
        if event=='import' and str(args[0]).split('.')[0] in FORBIDDEN:
            raise ValueError('native import in metadata-only closure: '+str(args[0]))
        if event in ('subprocess.Popen','os.system','socket.connect','os.kill','os.killpg','os.remove','os.rename','os.mkdir','os.rmdir','os.link','os.symlink','os.truncate','fcntl.flock'):
            raise ValueError('lifecycle/network/mutation/lock in read-only collector')
        if event=='open':
            path=args[0]
            if not isinstance(path,int):
                text=os.fspath(path); leaf=Path(text).name.lower()
                C.need(Path(text).suffix.lower() not in ('.pt','.pth','.ckpt','.safetensors','.onnx','.npz','.npy','.jsonl')
                       and 'budget' not in leaf and not leaf.endswith('.lock'),'nonmetadata artifact access')
            C.need(not(len(args)>1 and type(args[1]) is str and any(c in args[1] for c in 'wax+')),'read-only closure never writes')
            C.need(not(len(args)>2 and type(args[2]) is int and args[2]&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)),'read-only descriptors only')
    sys.addaudithook(audit)
    runtime=importlib.import_module('good_expert_holdout_runtime_v1'); core=runtime._base
    app=core._pinned_module('app_close_semantics_v5',core.APP_PIN); base=app._base
    modules={'runtime':runtime,'core':core,'app':app,'base':base,'reference':runtime._ref,'guard':runtime._guard}
    aliases={'runtime':'good_expert_holdout_runtime_v1.py','core':'a1_frozen_eval_runtime_v2.py',
        'app':'app_close_semantics_v5.py','base':'resume_runtime_contracts_v3.py',
        'reference':'embedded_teacher_reference_v1.py','guard':'producer_teacher_guard_v1.py'}
    for label,module in modules.items():
        C.need(Path(module.__file__).resolve()==root/aliases[label],'actual full module origin differs: '+label)
    C.need(core.APP_PIN==tuple(C.OVERLAY_PINS['app_close_semantics_v5.py'])
           and app._base is base and app.SOURCE_CODE_VERSION=='V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES',
           'real complete AppV6/Base closure binding differs')
    C.need(not any(name.split('.')[0] in FORBIDDEN for name in sys.modules),'native module unexpectedly loaded')
    return dict(runtime=runtime,core=core,app=app,base=base,reference=runtime._ref,guard=runtime._guard,parent_raw=parent_raw,
        receipt=dict(kind='WHOLE_ORIGINAL_GOOD20_METADATA_CLOSURE_V1',source_aliases=20,
            sources=checked,full_original_modules=True,AST_cropped_or_stubbed=False,
            full_AppV6_Base_imported=True,helper_base_is_actual_module=True,native_modules_loaded=[],
            parent_or_worker_main_called=False,old_producer_IO_predicates_rerun=False))


def _complete(info, name):
    value=info.get(name,{})
    C.need(value.get('status')=='READ' and type(value.get('read_count')) is int and value['read_count']==1 and value.get('whole_JSON_read') is True
           and value.get('projection_applied') is False and type(value.get('bytes')) is int and 0<value['bytes']<=maximum(name) and C.sha(value.get('SHA256')),
           'complete once-cached original bytes required: '+name)
    return value


def _baseline_metadata(runtime, entry):
    """Additional cached-data consistency check, not a substitute original grader.

    No resolve/stat/open of a producer checkpoint/FINAL or old TASK is performed.
    Complete original producer/source guards remain in the parent and its grade.
    """
    producer=entry['a1_producer']; final=producer['FINAL']; cp=final['checkpoint']; teacher=final['teacher']
    expected=runtime.BASELINE_IDENTITIES[entry['role']]
    C.need(final.get('actual_BPTT_policy_steps')==0 and type(final.get('actual_BPTT_policy_steps')) is int
           and type(cp.get('iteration')) is int and cp['iteration']==0
           and type(final.get('counts')) is dict and final['counts']
           and all(type(v) is int and v==0 for v in final['counts'].values()),'published actual0 baseline identity differs')
    for key,source_key in (('path','source_path'),('bytes','source_bytes'),('SHA','source_SHA')):
        C.need(type(cp.get(key)) is type(expected[source_key]) and cp[key]==expected[source_key], 'fixed source-container identity differs: '+key)
    for key in ('source_path','source_bytes','source_SHA'):
        C.need(teacher.get(key)==expected['mother_'+key],'original motherteacher provenance differs: '+key)
    C.need(cp.get('teacher_source')==teacher and entry.get('original_bootstrap_teacher')==teacher
           and teacher.get('teacher_frozen') is True,'mother/container distinction differs')
    return producer,cp


def validate_case_cache(documents, file_info, role, entry, plan, closure, secondary):
    """Layer cached metadata gates over the untouched published original grade."""
    runtime=closure['runtime']; app=closure['app']; prefix='cases/'+role+'/'
    C.need(prefix+'WORKER_ERROR.json' not in documents and not secondary.get(role), 'durable worker ERROR remains: '+role)
    data=documents.get(prefix+'FINAL.json'); info=_complete(file_info,prefix+'FINAL.json')
    C.need(type(data) is dict and data.get('passed_execution') is True and data.get('role')==role
           and data.get('group_id')==plan['group_id'] and data.get('integration')==runtime.INTEGRATION,
           'complete successful own role/group FINAL required')
    C.need(type(data.get('num_envs')) is int and data['num_envs']==80 and type(data.get('controls')) is int
           and data['controls']==750 and data.get('policy_variant')==C.POLICY
           and data.get('evaluation_purpose')==C.purpose(plan['seed']), 'original finite teacher/seed scope differs')
    role_entry=dict(entry,seed=plan['seed'],holdout_protocol=plan['holdout_protocol'],paired_reset_protocol=plan['paired_reset_protocol'])
    task=documents.get(prefix+'task.json')
    C.need(type(task) is dict and task.get('role')==role and task.get('group_id')==plan['group_id']
           and task.get('GPU_UUID')==plan['GPU_UUID'] and task.get('seed')==plan['seed']
           and task.get('batch_purpose')==C.purpose(plan['seed']), 'actual task/seed/GPU/purpose differs')
    C.need(prefix+'WORKER_SCENE_READY.json' in documents,'actual original scene-ready record missing')
    started=documents.get(prefix+'WORKER_EVAL_STARTED.json',{})
    C.need(started.get('role')==role and started.get('group_id')==plan['group_id'] and started.get('GPU_UUID')==plan['GPU_UUID']
           and type(started.get('seed')) is int and started['seed']==plan['seed'] and started.get('batch_purpose')==C.purpose(plan['seed']),
           'actual original worker common-start record differs')
    runtime._validate_batch_members(task,role)
    runtime._validate_e1_execution(data,role_entry)
    producer,checkpoint=_baseline_metadata(runtime,entry)
    source=data['source_cache']; runtime._validate_approved_reference(source)
    C.need(all(source.get(k)==checkpoint[v] for k,v in (('source_path','path'),('source_SHA','SHA'),('source_bytes','bytes')))
           and source.get('admitted_producer_run_id')==producer['run_id']
           and type(source.get('actual_BPTT_policy_steps')) is int and source['actual_BPTT_policy_steps']==0,
           'actual own source_cache identity differs')
    C.need(all(type(source.get(k)) is int and source[k]==1 for k in ('physical_byte_opens','SHA_calculations','CPU_decodes'))
           and type(source.get('mother_checkpoint_opens')) is int and source['mother_checkpoint_opens']==0
           and source.get('whole_root_CPU_unchanged') is True
           and source.get('replay_or_saved_history_sliced_or_restored') is False
           and source.get('live_optimizer_WM_critic_replay_created') is False, 'original single whole CPU cache integrity differs')
    C.need(type(source.get('actual_eval_RSL_source_binding')) is dict
           and all(type(source['actual_eval_RSL_source_binding'].get(k)) is type(v)
                   and source['actual_eval_RSL_source_binding'][k]==v for k,v in runtime.APPROVED_RSL_MODEL_SOURCE.items()),
           'actual evaluator RSL SOURCE binding differs')
    evidence=entry.get('producer_teacher_freeze_evidence'); reference=source.get('embedded_teacher_reference')
    closure['reference'].validate_reference_semantics(reference,expected_role=role,expected_source_sha=checkpoint['SHA'],
        expected_bootstrap_teacher_sha=entry['original_bootstrap_teacher']['source_SHA'],expected_actor_calls=750)
    C.need(type(evidence) is dict and reference.get('producer_teacher_state_guard')==evidence
           and source.get('producer_teacher_freeze_evidence')==evidence and 'frozen_mean' not in source
           and source.get('policy_variant')==C.POLICY and source.get('policy_family')=='EMBEDDED_ORIGINAL_TEACHER_MEAN'
           and source.get('original_bootstrap_teacher')==entry['original_bootstrap_teacher'], 'teacher state/normalization/actor provenance differs')
    paired=reference.get('paired_reset_protocol')
    C.need(type(paired) is dict and paired.get('candidate_pose_installed') is True
           and paired.get('protocol')==runtime.validate_paired_protocol(plan['paired_reset_protocol']), 'original pose/reset protocol differs')
    C.need(prefix+'PRE_CLOSE.json' in documents and documents.get(prefix+'ENV_CLOSE_RETURNED_A1_EVAL_V2.json',{}).get('closed') is True,
           'original preclose/env close proof missing')
    intent=None; returned=documents.get(prefix+'APP_CLOSE_RETURNED_A1_EVAL_V2.json')
    if returned is not None:
        C.need(type(returned) is dict and returned.get('returned') is True and type(returned.get('binding')) is dict,
               'actual returned App close record differs')
        binding=returned['binding']
    else:
        intent=documents.get(prefix+'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json')
        C.need(type(intent) is dict and intent.get('kind')=='PINNED_A1_EVAL_FAST_CLOSE_INTENT_V2'
               and intent.get('role')==role and intent.get('group_id')==plan['group_id']
               and type(intent.get('final_bytes')) is int and intent['final_bytes']==info['bytes']
               and intent.get('final_SHA')==info['SHA256'] and intent.get('original_env_close_returned') is True
               and intent.get('publication')=='FSYNC_ATOMIC_METADATA_BEFORE_ORIGINAL_APP_CLOSE',
               'original fast-close intent whole FINAL hash/binding differs')
        binding=intent['binding']
    C.need(type(binding) is dict, 'actual App binding is required')
    if binding.get('fast_shutdown') is True:
        app._validate_binding_receipt(binding)
    else:
        C.need(intent is None, 'non-fast mode requires an actual returned close, not a fast intent')
        closure['core']._validate_returned_app_binding(binding,app)
    return dict(role=role,passed_cached_metadata=True,complete_original_FINAL_SHA256=info['SHA256'],
        complete_original_FINAL_bytes=info['bytes'],old_producer_IO_predicates_rerun=False,
        producer_original_grade_not_replaced=True,metrics=data['metrics'],source_cache=source,
        absolute_original_scope=runtime._absolute_skill(role,data))


def validate_terminal_cache(documents, file_info, dispatch, closure, secondary_errors):
    """Good-specific rows/source-grade/close gates; never create original grade."""
    C.validate_dispatch(dispatch); C.need(type(closure) is dict and 'runtime' in closure,'whole original metadata closure required')
    runtime=closure['runtime']; plan=documents.get('GROUP_PLAN.json'); root=dispatch['root']
    selected=C.plan_identity(plan,root,dispatch['group_id'],dispatch['seed'],dispatch['GPU_UUID'],runtime=True)
    runtime._batch_fields(plan); runtime._stage_file_metadata(plan)
    C.need(runtime.validate_paired_protocol(plan.get('paired_reset_protocol'))['seed']==dispatch['seed'],'original paired protocol seed differs')
    for name in ('PARENT_ORIGINAL_ERROR.json','GROUP_ABORT.json','GROUP_STARTUP_ABORT.json',C.ERROR):
        C.need(name not in documents,'durable original/controller ERROR remains: '+name)
    grade=documents.get(C.GRADE)
    C.need(type(grade) is dict and grade.get('kind')=='CLOSED_EMBEDDED_TEACHER_REFERENCE_SOURCE_GRADE_V1'
           and grade.get('passed_closed_reference_source_grade') is True and grade.get('original_error') is False
           and grade.get('reasons')==[] and grade.get('checked_roles')==list(C.REQUESTED)
           and grade.get('group_root')==root and grade.get('policy_variant')==C.POLICY
           and grade.get('batch_purpose')==C.purpose(dispatch['seed'])
           and grade.get('external_executing_parent_actual_wait_required') is True
           and grade.get('external_parent_wait_proof_created_here') is False,'untouched original producer source grade did not pass')
    final=documents.get('FINAL.json'); _complete(file_info,'FINAL.json'); _complete(file_info,'TERMINAL_ROWS.json')
    C.need(type(final) is dict and 'terminal' not in final and final.get('kind')=='ACTUAL_GOOD_EXPERT_HOLDOUT_C878_S135_V1',
           'good holdout FINAL requires original rows, not Phase1 terminal')
    runtime._batch_fields(final)
    C.need(final.get('seed')==dispatch['seed'] and final.get('batch_purpose')==C.purpose(dispatch['seed'])
           and final.get('group_id')==dispatch['group_id'] and final.get('GPU_UUID')==dispatch['GPU_UUID']
           and final.get('original_eight_role_catalog')==plan['roles']
           and final.get('all_requested_actual_execution_complete') is True
           and final.get('requested_ready_before_start') is True,'complete own good batch metadata differs')
    admission=documents.get('ACTUAL_GROUP_ADMISSION.json',{})
    C.need(admission.get('group_id')==dispatch['group_id']
           and admission.get('resource',{}).get('GPU_UUID')==dispatch['GPU_UUID']
           and admission.get('original_private_GPU_EX_held') is True and admission.get('original_global_finite_EX_held') is True
           and type(admission.get('canonical_writes')) is int and admission['canonical_writes']==0
           and admission.get('canonical_owner_at_read') is None,'original resource admission differs')
    parent_started=documents.get('PARENT_STARTED.json',{})
    C.need(parent_started.get('pid')==dispatch['parent']['pid'] and parent_started.get('GPU_UUID')==dispatch['GPU_UUID']
           and parent_started.get('kind')=='ONEGPU_GOOD_EXPERT_HOLDOUT_C878_S135_V1'
           and parent_started.get('requested_roles')==list(C.REQUESTED) and parent_started.get('deferred_roles')==list(C.DEFERRED),
           'original executing parent start/identity differs')
    start=documents.get('GROUP_EVAL_START.json',{})
    runtime._batch_fields(start)
    C.need(start.get('group_id')==dispatch['group_id'] and start.get('GPU_UUID')==dispatch['GPU_UUID']
           and start.get('seed')==dispatch['seed'] and start.get('batch_purpose')==C.purpose(dispatch['seed'])
           and start.get('all_members_ready') is True and set(start.get('members',[]))==set(C.REQUESTED)
           and len(start['members'])==2,'original two-member ready barrier differs')
    exit_scope=documents.get('PARENT_EXIT_SCOPE.json',{})
    C.need(all(exit_scope.get(k) is True for k in ('all_own_children_waited','original_single_GPU_private_EX_released','original_global_finite_EX_released'))
           and exit_scope.get('errors')==[] and type(exit_scope.get('canonical_writes')) is int and exit_scope['canonical_writes']==0,
           'own child waits and both original EX releases must separately qualify')
    waits=exit_scope.get('child_waits'); rows=documents.get('TERMINAL_ROWS.json'); children=documents.get('CHILDREN.json')
    for label,values in (('waits',waits),('rows',rows),('children',children)):
        C.need(type(values) is list and len(values)==2 and all(type(v) is dict for v in values)
               and {v.get('role') for v in values}==set(C.REQUESTED),'exact original two-role '+label+' required')
    C.need(final.get('rows')==rows,'complete group FINAL rows differ from terminal cache')
    checked=[]
    for entry in selected:
        role=entry['role']; row=next(v for v in rows if v['role']==role); waited=next(v for v in waits if v['role']==role)
        child=next(v for v in children if v['role']==role)
        C.need(waited.get('actual_waited') is True and type(waited.get('returncode')) is int and waited['returncode']==0
               and type(waited.get('pid')) is int and waited['pid']==row.get('pid')==child.get('pid')
               and child.get('GPU_UUID')==dispatch['GPU_UUID'] and child.get('root')==root+'/cases/'+role,
               'actual own original child wait/identity differs: '+role)
        C.need(runtime._terminal_success(row) and type(row.get('returncode')) is int and row['returncode']==0
               and row.get('error') is None and row.get('GPU_UUID')==dispatch['GPU_UUID'],'original child terminal/error gate differs')
        C.need(row.get('data')==documents.get('cases/'+role+'/FINAL.json'),'whole cached role FINAL differs from terminal row')
        checked.append(validate_case_cache(documents,file_info,role,entry,plan,closure,secondary_errors))
    C.need(final.get('absolute_original_scope_results')=={v['role']:v['absolute_original_scope'] for v in checked},
           'published conditional scope summary differs from complete original role metrics')
    outer=documents.get(C.WAITED)
    C.need(type(outer) is dict and outer.get('kind')==C.WAITED_KIND and outer.get('actual_parent_p_wait_returned') is True
           and type(outer.get('returncode')) is int and outer['returncode']==0 and outer.get('controller_errors')==[]
           and outer.get('original_parent_resource_close_wait_not_replaced') is True
           and type(outer.get('actual_native_parent_Popen_calls')) is int and outer['actual_native_parent_Popen_calls']==1,
           'independent executing outer actual Popen.wait is required, not PID absence or RC0 alone')
    C.need(documents.get(C.STARTED,{}).get('kind')==C.STARTED_KIND,'exact own outer controller start kind required')
    for name in (C.STARTED,C.WAITED):
        value=documents.get(name,{})
        C.need(type(value.get('controller_resource_SDK_model_C_lock_or_signal_operations')) is int
               and value['controller_resource_SDK_model_C_lock_or_signal_operations']==0,'outer controller must not replace resources/SDK/locks/signals')
    for name in (C.STARTED,C.DISPATCH,C.WAITED):
        value=documents.get(name,{})
        C.need(value.get('controller')==dispatch['controller'],'outer controller pid/startticks differs')
        if name!=C.STARTED: C.need(value.get('parent')==dispatch['parent'],'own parent pid/startticks differs')
        for key in ('root','group_id','seed','GPU_UUID','evaluation_purpose','parent_source_SHA','controller_source_SHA','stage_receipt_SHA256','GROUP_PLAN_bytes','GROUP_PLAN_SHA256'):
            C.need(value.get(key)==dispatch.get(key),'outer record binding differs: '+name+':'+key)
    C.need(documents.get(C.DISPATCH)==dispatch,'actual dispatch cache differs from supplied dispatch')
    plan_info=_complete(file_info,'GROUP_PLAN.json'); stage_info=_complete(file_info,C.STAGE_NAME)
    C.need((plan_info['bytes'],plan_info['SHA256'])==(dispatch['GROUP_PLAN_bytes'],dispatch['GROUP_PLAN_SHA256'])
           and stage_info['SHA256']==dispatch['stage_receipt_SHA256'],'own raw plan/materialization receipt binding differs')
    return dict(kind='GOOD_HOLDOUT_INDEPENDENT_CACHED_METADATA_VALIDATION_V1',passed=True,
        checked_roles=list(C.REQUESTED),cases=checked,producer_source_grade_preserved=True,
        ownchild_waits_and_both_EX_verified=True,independent_outer_actual_wait_verified=True,
        original_thresholds_changed=False,whole_skill_rate=None,relative_improvement=None)


def watch(reader, *, cap_seconds=6000, interval_seconds=20, monotonic=time.monotonic, sleep=time.sleep):
    C.need(type(cap_seconds) is int and 1<=cap_seconds<=6000 and type(interval_seconds) is int and 1<=interval_seconds<=20,
           'collector polling/cap only; native deadlines are not extended')
    started=monotonic()
    while True:
        for name in SMALL: reader.read(name)
        if C.WAITED in reader.cache or monotonic()-started>=cap_seconds: break
        sleep(interval_seconds)
    for name in BIG: reader.read(name,terminal=True)
    reader.observe_secondary_errors()
    return dict(collector_cap_reached=C.WAITED not in reader.cache,outer_wait_observed=C.WAITED in reader.cache,
        native_deadline_extended=False,cap_seconds=cap_seconds,interval_seconds=interval_seconds)


def remote_main(dispatch, *, cap_seconds=6000, interval_seconds=20):
    C.validate_dispatch(dispatch); reader=MetadataReader(dispatch['root']); closure=None; validation=None; errors=[]
    polling=dict(collector_cap_reached=None,outer_wait_observed=None,native_deadline_extended=False)
    try:
        closure=load_metadata_closure(reader.root)
    except Exception as exc:
        errors.append(dict(check='full_SOURCE_closure',type=type(exc).__name__,message=str(exc)))
    try:
        # Preserve actual outer/child/error metadata even when SOURCE closure fails.
        polling=watch(reader,cap_seconds=cap_seconds,interval_seconds=interval_seconds)
        C.need(closure is not None,'full original metadata closure is missing; original errors stay visible')
        C.validate_stage(reader.raw_cache[C.STAGE_NAME],reader.raw_cache['GROUP_PLAN.json'],closure['parent_raw'],
            root=dispatch['root'],group_id=dispatch['group_id'],seed=dispatch['seed'],gpu_uuid=dispatch['GPU_UUID'],
            stage_sha=dispatch['stage_receipt_SHA256'])
        validation=validate_terminal_cache(reader.cache,reader.info,dispatch,closure,reader.secondary_errors)
        validation['materialization_raw_receipt_and_plan_validated']=True
    except Exception as exc:
        errors.append(dict(check='cached_metadata',type=type(exc).__name__,message=str(exc)))
    packet=dict(kind='GOOD_HOLDOUT_OWN_METADATA_PACKET_V1',root=dispatch['root'],group_id=dispatch['group_id'],seed=dispatch['seed'],
        evaluation_purpose=dispatch['evaluation_purpose'],documents=reader.cache,file_metadata=reader.info,
        secondary_worker_errors=reader.secondary_errors,collector_errors=reader.errors+errors,
        metadata_closure=None if closure is None else closure['receipt'],cached_validation=validation,polling=polling,
        whole_original_FINALs_read_once=all(reader.info.get(n,{}).get('status')=='READ' and reader.info[n].get('read_count')==1 for n in BIG),
        FINAL_projection_applied=False,read_only_own_metadata=True,logs={name:reader.tail(name) for name in LOGS})
    raw=json.dumps(packet,allow_nan=False)
    C.need(len(raw.encode('utf-8'))<=C.EXPORT_MAX,'complete own metadata packet exceeds bounded export; no projection fallback')
    print(raw)
    return packet
