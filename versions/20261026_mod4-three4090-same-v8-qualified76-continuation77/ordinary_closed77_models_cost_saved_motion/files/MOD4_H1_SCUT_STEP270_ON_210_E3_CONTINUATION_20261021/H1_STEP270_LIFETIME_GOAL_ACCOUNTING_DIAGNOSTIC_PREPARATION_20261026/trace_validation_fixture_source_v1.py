def canonical_V8_trace_tree(path):
    tree=ast.parse(Path(path).read_text('utf8'))
    expected_import=ast.parse('from h1_lifetime_goal_counter_v1 import LifetimeGoalCounter, EVENTS').body[0]
    matches=[n for n in tree.body if ast.dump(n)==ast.dump(expected_import)];assert len(matches)==1;tree.body.remove(matches[0])
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='H1ControlPrefixTrace')
    install=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='install')
    expected_init=ast.parse("self.lifetime_goal_counter=LifetimeGoalCounter({k:getattr(self.env.h1_phase,k).detach().cpu().numpy().copy() for k in EVENTS},self.env.h1_phase.crossed.detach().cpu().numpy().copy())").body[0]
    matches=[n for n in install.body if ast.dump(n)==ast.dump(expected_init)];assert len(matches)==1 and install.body.index(matches[0])==1;install.body.remove(matches[0])
    step=next(n for n in install.body if isinstance(n,ast.FunctionDef) and n.name=='step');tr=next(n for n in step.body if isinstance(n,ast.Try))
    expected_complete=ast.parse('self.lifetime_goal_counter.complete(self.rows[-1])').body[0]
    matches=[n for n in tr.body if ast.dump(n)==ast.dump(expected_complete)];assert len(matches)==1
    pos=tr.body.index(matches[0]);assert isinstance(tr.body[pos-1],ast.AugAssign) and ast.dump(tr.body[pos-1].target)==ast.dump(ast.parse('self.total',mode='eval').body) and isinstance(tr.body[pos+1],ast.If)
    tr.body.remove(matches[0])
    persist=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='persist')
    expected_save=ast.parse('self.lifetime_goal_counter.save(self.folder)').body[0]
    assert ast.dump(persist.body[-1])==ast.dump(expected_save);persist.body.pop()
    original=base64.b64decode(ORIGINAL_V8_TRACE_BASE64)
    assert hashlib.sha256(original).hexdigest()==ORIGINAL_V8_TRACE_SHA
    assert ast.dump(tree)==ast.dump(ast.parse(original.decode('utf8')))
    return tree

def installed_counter_CPU_checks(B):
    import torch,types,time,traceback
    from unittest import mock
    B=Path(B);rng=torch.get_rng_state().clone();n=20000;out=B/'reports/lifetime_goal_diagnostic_CPU_fixture';out.mkdir(parents=True)
    phase=types.SimpleNamespace(**{k:torch.zeros(n,dtype=torch.long) for k in EVENTS},crossed=torch.zeros(n,2,dtype=torch.bool))
    env=types.SimpleNamespace(h1_phase=phase,_h1_sampled_excess_training_active=False,_h1_sampled_actions_for_reward=None)
    actions=torch.zeros(n,6);actions[:,0]=106.;original=actions.clone();calls=[];errors=[];persists=[];holder={}
    witness=types.SimpleNamespace(env=env,frame=None,observed={'policy35':torch.zeros(n,35),'critic38':torch.zeros(n,38)},rows=[],total=0,folder=out,persist=lambda:persists.append('original_persist_called'))
    tree=ast.parse((B/'h1_production_control_prefix_trace_v1.py').read_text('utf8'));cls=next(x for x in tree.body if isinstance(x,ast.ClassDef));install=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='install')
    init=install.body[1];scope={'self':witness,'LifetimeGoalCounter':LifetimeGoalCounter,'EVENTS':EVENTS}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[init],type_ignores=[])),'actual_counter_init','exec'),scope)
    def old_step(value):
        assert value is actions and torch.equal(value,original) and env._h1_sampled_excess_training_active
        assert env._h1_sampled_actions_for_reward.data_ptr()!=value.data_ptr() and torch.equal(env._h1_sampled_actions_for_reward,value)
        rowno=len(calls);calls.append(value.data_ptr());done=torch.zeros(n,dtype=torch.bool)
        if rowno<2:phase.takeoff_count[0]+=1;phase.crossed[0]=True
        if rowno==0:done[0]=True
        if rowno==1:phase.landing_count[0]=1
        if rowno==2:phase.recovery_count[0]=1
        witness.frame={k:getattr(phase,k).clone() for k in EVENTS};witness.frame['step_wheel_crossed']=phase.crossed.clone();witness.frame['executed6']=value.clamp(-6,6)
        result=({'policy':torch.zeros(n,35)},torch.full((n,),.5),done,{})
        for k in EVENTS:getattr(phase,k)[done]=0
        phase.crossed[done]=False;holder['result']=result;return result
    step=next(x for x in install.body if isinstance(x,ast.FunctionDef) and x.name=='step')
    scope={'self':witness,'old_step':old_step,'torch':torch,'np':np,'time':time,'traceback':traceback,'put':lambda p,v:errors.append(v)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[step],type_ignores=[])),'actual_complete_step','exec'),scope)
    for _ in range(3):
        result=scope['step'](actions);assert result is holder['result'] and torch.equal(actions,original)
        assert env._h1_sampled_actions_for_reward is None and not env._h1_sampled_excess_training_active
    s=witness.lifetime_goal_counter.snapshot();assert s['events']==dict(takeoff_count=2,landing_count=1,recovery_count=1) and s['both_leading_edges_cross_event_count']==2 and s['complete_control_rows']==3 and s['diagnostic_valid']
    for _ in range(21):scope['step'](actions)
    assert witness.total==24 and len(persists)==1 and witness.lifetime_goal_counter.rows==24 and witness.lifetime_goal_counter.snapshot()['events']==s['events']
    def failed(value):raise RuntimeError('EXPECTED_CPU_ORIGINAL_STEP_FAILURE')
    scope['old_step']=failed
    try:scope['step'](actions)
    except RuntimeError as error:assert str(error)=='EXPECTED_CPU_ORIGINAL_STEP_FAILURE'
    else:raise AssertionError('Original failure swallowed')
    assert len(errors)==1 and len(persists)==2 and witness.total==24 and witness.lifetime_goal_counter.rows==24 and env._h1_sampled_actions_for_reward is None and not env._h1_sampled_excess_training_active
    # Real unwrapped persist ordering: original index publication must succeed before optional accounting save.
    pd=out/'persist_success';pd.mkdir();counter=witness.lifetime_goal_counter;events=[]
    test=types.SimpleNamespace(rows=[{'x':np.arange(4)}],folder=pd,index=[],source_models=[{'synthetic_fixture':True}],total=24,terms=[],lifetime_goal_counter=counter)
    def put(p,v):events.append('original_index');Path(p).write_text(json.dumps(v),encoding='utf8')
    persist=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='persist')
    def writer(f,rows,compresslevel):np.savez_compressed(f,x=np.stack([r['x'] for r in rows]))
    ps={'self':test,'write_trace_rows_npz':writer,'H':lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest(),'put':put,'time':time}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[persist],type_ignores=[])),'actual_persist_order','exec'),ps);ps['persist'](test)
    saved=json.loads((pd/'CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json').read_bytes());assert saved['complete_control_rows']==24 and events==['original_index'] and not (pd/'CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json.partial').exists()
    failure=out/'persist_failure';failure.mkdir();test.folder=failure;test.rows=[]
    def original_failure(p,v):raise RuntimeError('EXPECTED_ORIGINAL_PERSIST_FAILURE')
    ps['put']=original_failure
    try:ps['persist'](test)
    except RuntimeError as error:assert str(error)=='EXPECTED_ORIGINAL_PERSIST_FAILURE'
    else:raise AssertionError('Original persistence failure swallowed')
    assert not (failure/'CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json').exists()
    # Optional diagnostic I/O errors never replace original training/persistence failures.
    with mock.patch.object(Path,'write_text',side_effect=OSError('EXPECTED_DIAGNOSTIC_WRITE_FAILURE')):assert counter.save(pd) is False
    assert len(counter.write_errors)==1 and counter.save(pd) is True
    malformed={k:v.copy() for k,v in witness.rows[-1].items()};malformed['done']=np.zeros(2,dtype=bool);assert counter.complete(malformed) is False and not counter.snapshot()['diagnostic_valid']
    negative=LifetimeGoalCounter({k:np.ones(n,dtype=np.int64) for k in EVENTS},np.zeros((n,2),dtype=bool));zero={k:np.zeros(n,dtype=np.int64) for k in EVENTS};zero.update(done=np.zeros(n,dtype=bool),step_wheel_crossed=np.zeros((n,2),dtype=bool));assert negative.complete(zero) and not negative.snapshot()['diagnostic_valid']
    original_text=(B/'h1_production_control_prefix_trace_v1.py').read_text('utf8');negative_sources=[]
    for name,text in [('forwarding',original_text.replace('old_step(actions)','old_step(actions.clamp(-5,5))')),('clear',original_text.replace('self.env._h1_sampled_actions_for_reward=None','self.env._h1_sampled_actions_for_reward=raw')),('duplicate_complete',original_text.replace('self.lifetime_goal_counter.complete(self.rows[-1])','self.lifetime_goal_counter.complete(self.rows[-1]);self.lifetime_goal_counter.complete(self.rows[-1])')),('skip_save',original_text.replace('self.lifetime_goal_counter.save(self.folder)','self.lifetime_goal_counter.save(self.folder.parent)'))]:
        p=out/(name+'.negative_source.txt');p.write_text(text,encoding='utf8')
        try:canonical_V8_trace_tree(p)
        except AssertionError:negative_sources.append(name)
        else:raise AssertionError('Unexpected trace change accepted: '+name)
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    artifacts=[{'path':str(p),'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()} for p in pd.iterdir() if p.is_file()]
    return {'passed':True,'synthetic_environments':n,'actual_trace_step_forwarding_and_reset_row_order_tested':True,'same_original_actions_object_values_and_output_tuple':True,'no_partial_failed_control_counted':True,'original_persist_before_optional_counter_publish_and_original_errors_preserved':True,'diagnostic_IO_error_nonblocking_and_recorded':True,'invalid_counter_diagnostic_not_training_gate':True,'negative_source_cases_rejected':negative_sources,'no_GPU_RNG_policy_model_or_physics':True,'not_actual_runtime_goal_events':True,'synthetic_artifacts':artifacts}
