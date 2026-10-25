"""Uninstalled readonly CPU landing-record journal fragment; production uses existing NumPy rows."""
class LandingEventJournal:
    FIELDS=('root13','q30','joint_velocity','applied_torque','executed6','raw_sampled6','history5ms','impulse','public_request','step_stable_ticks','step_success','step_wheel_crossed','takeoff_count','landing_count','recovery_count','episode','done')
    def __init__(self,n,pre=16,post=64,cap=64):
        from collections import deque
        self.n=n;self.pre=pre;self.post=post;self.cap=cap;self.ring=deque(maxlen=pre)
        self.cases=[];self.last_control=0;self.landing_records_seen=0;self.landing_delta_seen=0;self.skipped_cap=0;self.errors=[];self.write_errors=[]
    def _copy(self,row,env):
        out={}
        for name in self.FIELDS:
            a=row[name]
            if not isinstance(a,np.ndarray) or a.shape[0]!=self.n or a.dtype.kind not in 'biuf':raise ValueError('Journal row schema '+name)
            value=np.asarray(a[env]).copy()
            if not np.isfinite(value).all():raise ValueError('Journal selected nonfinite '+name)
            out[name]=value
        return out
    def _error(self,error,control):
        if len(self.errors)<16:self.errors.append(dict(type=type(error).__name__,message=str(error),control=control))
    def complete(self,row,landing_ids,landing_deltas,control):
        if control!=self.last_control+1:
            self._error(ValueError('Journal nonsequential completed control'),control);return False
        self.last_control=control
        try:
            for case in self.cases:
                if case['closed_reason'] is not None:continue
                e=case['env_id']
                if int(row['episode'][e])!=case['episode']:
                    case['closed_reason']='episode_changed_censored';continue
                case['rows'].append(self._copy(row,e));case['controls'].append(control);case['post_rows']+=1
                if bool(row['done'][e]):case['closed_reason']='selected_reset_censored'
                elif case['post_rows']>=self.post:case['closed_reason']='post_control_limit'
            for e0 in landing_ids:
                e=int(e0);self.landing_records_seen+=1;self.landing_delta_seen+=int(landing_deltas[e])
                if len(self.cases)>=self.cap:self.skipped_cap+=1;continue
                event=self._copy(row,e);episode=int(row['episode'][e]);pre=[]
                for no,old in reversed(self.ring):
                    if int(old['episode'][e])!=episode or bool(old['done'][e]):break
                    pre.append((no,self._copy(old,e)))
                pre.reverse();case=dict(case_id=len(self.cases),env_id=e,episode=episode,landing_control=control,landing_counter_delta=int(landing_deltas[e]),rows=[x[1] for x in pre]+[event],controls=[x[0] for x in pre]+[control],pre_rows=len(pre),post_rows=0,closed_reason='selected_reset_at_landing_censored' if bool(row['done'][e]) else None,versions=[])
                self.cases.append(case)
        except (KeyError,ValueError,TypeError,IndexError,OverflowError) as error:
            self._error(error,control)
        self.ring.append((control,row))
        return not self.errors
    def snapshot(self):
        summaries=[]
        for case in self.cases:
            summaries.append({k:v for k,v in case.items() if k not in ('rows',)})
        return dict(schema='readonly_landing_event_cpu_journal_v1',completed_control_rows_seen=self.last_control,num_envs=self.n,pre_control_limit=self.pre,post_control_limit=self.post,case_cap=self.cap,selection='First landing-positive completed control/environment records, chronological then ascending env id; cap explicit, original lifetime counts remain uncapped',landing_positive_records_seen=self.landing_records_seen,original_landing_counter_delta_seen=self.landing_delta_seen,cases_started=len(self.cases),skipped_by_case_cap=self.skipped_cap,diagnostic_valid=not self.errors,errors=list(self.errors),write_errors=list(self.write_errors),cases=summaries,only_existing_copied_CPU_rows_no_new_GPU_actor_physics_or_RNG=True,not_full_callback_replay_frozen_policy_or_success_graduation=True)
    def save(self,folder):
        folder=Path(folder)
        try:
            for case in self.cases:
                last=case['controls'][-1]
                if case['versions'] and case['versions'][-1]['last_control']==last:continue
                p=folder/('landing_event_case_'+str(case['case_id']).zfill(4)+'_through_'+str(last)+'.npz');tmp=p.with_suffix('.npz.partial')
                arrays={name:np.stack([row[name] for row in case['rows']]) for name in self.FIELDS};arrays['recorded_control_no']=np.asarray(case['controls'],dtype=np.int64)
                with tmp.open('xb') as f:np.savez_compressed(f,**arrays)
                tmp.replace(p);digest=hashlib.sha256()
                with p.open('rb') as f:
                    for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
                case['versions'].append(dict(path=str(p),bytes=p.stat().st_size,SHA=digest.hexdigest(),last_control=last,recorded_frames=len(case['rows']),closed_reason_at_publish=case['closed_reason']))
            p=folder/'CONTROL_LANDING_EVENT_JOURNAL_ACTUAL.json';tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(self.snapshot(),indent=2),encoding='utf8');os.replace(tmp,p);return True
        except (OSError,ValueError,TypeError,KeyError) as error:
            if len(self.write_errors)<16:self.write_errors.append(dict(type=type(error).__name__,message=str(error),control=self.last_control))
            return False


def validate_landing_journal_extension_AST(B):
    import copy
    B=Path(B);ref=B/'reference_sources/actual79c_counter_original_bytes.txt';raw=ref.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='REPLACE_ORIGINAL_COUNTER_SHA'
    old=ast.parse(raw.decode('utf8'));tree=ast.parse((B/'h1_lifetime_goal_counter_v1.py').read_text('utf8'))
    additions={'LandingEventJournal','validate_landing_journal_extension_AST','installed_landing_journal_CPU_checks'}
    tree.body=[n for n in tree.body if not isinstance(n,(ast.ClassDef,ast.FunctionDef)) or n.name not in additions]
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='LifetimeGoalCounter')
    init=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__');hook=ast.parse('self.landing_journal=LandingEventJournal(self.n)').body[0];assert ast.dump(init.body[-1])==ast.dump(hook);init.body.pop()
    complete=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='complete');hook=ast.parse("self.landing_journal.complete(row,np.flatnonzero(deltas['landing_count']>0),deltas['landing_count'],self.rows)").body[0];assert ast.dump(complete.body[-2])==ast.dump(hook);complete.body.pop(-2)
    save=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='save');tr=next(n for n in save.body if isinstance(n,ast.Try));hook=ast.parse('self.landing_journal.save(folder)').body[0];assert ast.dump(tr.body[-2])==ast.dump(hook);tr.body.pop(-2)
    assert ast.dump(tree)==ast.dump(old)
    return dict(passed=True,only_original_counter_three_readonly_hooks=True,original_event_count_reset_and_persistence_AST_exact=True,trace_reward_actor_physics_unchanged=True)


def installed_landing_journal_CPU_checks(B):
    import torch
    from unittest import mock
    B=Path(B);proof=validate_landing_journal_extension_AST(B);rng=torch.get_rng_state().clone();n=20000;out=B/'reports/landing_journal_CPU_fixture';out.mkdir(parents=True)
    def row(no):
        z=lambda *shape:np.zeros((n,*shape),dtype=np.float32)
        r=dict(root13=z(13),q30=z(30),joint_velocity=z(30),applied_torque=z(30),executed6=z(6),raw_sampled6=z(6),history5ms=z(3,2,3),impulse=z(2,3),public_request=np.ones(n,dtype=bool),step_stable_ticks=np.zeros(n,dtype=np.int64),step_success=np.zeros(n,dtype=bool),step_wheel_crossed=np.zeros((n,2),dtype=bool),takeoff_count=np.zeros(n,dtype=np.int64),landing_count=np.zeros(n,dtype=np.int64),recovery_count=np.zeros(n,dtype=np.int64),episode=np.zeros(n,dtype=np.int64),done=np.zeros(n,dtype=bool))
        r['root13'][:,0]=no*.01;return r
    journal=LandingEventJournal(n,pre=2,post=3,cap=2);inputs=[]
    for no in range(1,7):
        r=row(no);ids=[];delta=np.zeros(n,dtype=np.int64)
        if no==3:ids=[0];delta[0]=1;r['landing_count'][0]=1
        if no==4:ids=[1];delta[1]=1;r['landing_count'][1]=1;r['done'][1]=True
        if no==5:ids=[2];delta[2]=1
        if no==4:r['root13'][0,7]=.4
        saved={k:v.copy() for k,v in r.items()};inputs.append(r);assert journal.complete(r,np.asarray(ids,dtype=np.int64),delta,no)
        assert all(np.array_equal(r[k],v) for k,v in saved.items())
    s=journal.snapshot();assert s['diagnostic_valid'] and s['landing_positive_records_seen']==3 and s['cases_started']==2 and s['skipped_by_case_cap']==1
    assert journal.ring[-1][1] is inputs[-1] and len(journal.ring)==2
    assert journal.cases[0]['controls']==[1,2,3,4,5,6] and journal.cases[0]['closed_reason']=='post_control_limit'
    assert journal.cases[1]['closed_reason']=='selected_reset_at_landing_censored'
    assert journal.save(out);meta=json.loads((out/'CONTROL_LANDING_EVENT_JOURNAL_ACTUAL.json').read_bytes());assert len(meta['cases'])==2
    artifacts=[]
    for case in meta['cases']:
        a=case['versions'][-1];p=Path(a['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==a['SHA']
        with np.load(p,allow_pickle=False) as z:
            assert len(z['root13'])==len(case['controls']) and z['root13'].dtype==np.float32 and z['recorded_control_no'].tolist()==case['controls']
            if case['env_id']==0:assert z['root13'][3,7]==np.float32(.4)
        artifacts.append(a)
    count=len(list(out.glob('*.npz')));assert journal.save(out) and len(list(out.glob('*.npz')))==count
    # Separate optional-journal invalidity never invalidates original event-count accounting.
    counter=LifetimeGoalCounter({k:np.zeros(n,dtype=np.int64) for k in EVENTS},np.zeros((n,2),dtype=bool));minimal={k:np.zeros(n,dtype=np.int64) for k in EVENTS};minimal['landing_count'][0]=1;minimal.update(done=np.zeros(n,dtype=bool),step_wheel_crossed=np.zeros((n,2),dtype=bool));assert counter.complete(minimal) and counter.snapshot()['diagnostic_valid'] and not counter.landing_journal.snapshot()['diagnostic_valid']
    pending=LandingEventJournal(n);r=row(1);d=np.zeros(n,dtype=np.int64);d[0]=1;pending.complete(r,np.array([0]),d,1)
    with mock.patch.object(np,'savez_compressed',side_effect=OSError('EXPECTED_OPTIONAL_JOURNAL_IO_FAILURE')):assert pending.save(out) is False
    assert pending.write_errors and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    return dict(passed=True,AST=proof,synthetic_environments=n,readonly_existing_CPU_array_references_and_selected_copies=True,pre_event_post_event_reset_censoring_and_case_cap_tested=True,original_event_counter_diagnostic_independent=True,optional_IO_error_nonblocking=True,repeat_persist_no_duplicate_binary=True,input_arrays_RNG_and_GPU_untouched=True,synthetic_artifacts=artifacts,not_actual_training_landing_records=True)
