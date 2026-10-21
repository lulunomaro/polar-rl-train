from pathlib import Path
import ast,copy,hashlib,json,math,os,sys,time,traceback,types,torch
T=Path(__file__).resolve().parent;R=T/'reports';N=T/'H1_STEP270_E3_PAIR_V7_20261022';base=N/'current_pair_closed_text/h1/job0/runtime/isaac/mod4';read=lambda p:json.loads(Path(p).read_bytes())
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def selected(source,names):
    return ast.Module(body=[copy.deepcopy(x) for x in ast.parse(source).body if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name in names],type_ignores=[])
try:
    torch.set_num_threads(2);proof=read(R/'V98_H1_FAILED_PREFIX_AND_ACTUAL_COMMAND_SDK_SOURCE_RETURNED_ACTUAL.json');candidate=read(R/'V98_H1_STEP270_EXTERNAL_COMMAND_AUDIT_CANDIDATE_SOURCE_AST_ACTUAL.json')
    s=torch.load(proof['prefix']['local_path'],map_location='cpu',weights_only=False);state=s['H1_step270_task_state'];phase_state=state['phase']
    sdk=next(x for x in proof['actual_installed_SDK_source_texts'] if x['path'].endswith('/velocity_command.py'))
    cls=next(x for x in ast.parse(sdk['text']).body if isinstance(x,ast.ClassDef) and x.name=='UniformVelocityCommand');prop=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='command')
    proxy=ast.ClassDef(name='SDKCommandPropertyCPUProxy',bases=[],keywords=[],body=[copy.deepcopy(prop)],decorator_list=[]);ns=dict(torch=torch);m=ast.Module(body=[proxy],type_ignores=[]);ast.fix_missing_locations(m);exec(compile(m,'actual_SDK_command_property','exec'),ns)
    ns.update(UniformVelocityCommand=ns['SDKCommandPropertyCPUProxy'],math=math,os=os)
    world=selected((base/'h1_original_directional_runtime.py').read_text('utf8'),{'DirectionalSpinCommand','transition_yaw','audit'});exec(compile(ast.fix_missing_locations(world),'actual_original_directional_audit','exec'),ns)
    directional=ns['audit'];ns['original_audit']=directional
    external=selected((base/'h1_external_operator_command_v1.py').read_text('utf8'),{'H1ExternalOperatorCommand','audit'});exec(compile(ast.fix_missing_locations(external),'actual_legacy_zero_audit','exec'),ns);legacy=ns['audit'];Command=ns['H1ExternalOperatorCommand']
    world_module=types.ModuleType('h1_original_directional_runtime');world_module.audit=directional;external_module=types.ModuleType('h1_external_operator_command_v1');external_module.H1ExternalOperatorCommand=Command
    sys.modules['h1_original_directional_runtime']=world_module;sys.modules['h1_external_operator_command_v1']=external_module
    source=Path(candidate['candidate_path']).read_text('utf8');new=selected(source,{'Step270Phase','audit_step270_external_request'});exec(compile(ast.fix_missing_locations(new),'new_task_audit_candidate','exec'),ns);Phase=ns['Step270Phase'];audit=ns['audit_step270_external_request']
    def env_for(age,command):
        term=Command.__new__(Command)
        for k,v in state['external_command'].items():setattr(term,k,v.clone())
        term.vel_command_b=command.clone();term.cfg=types.SimpleNamespace(heading_command=False);term.manual_evaluation_mode=True;term.pure_max=4*math.pi;term.progress_goal=.15
        phase=Phase.__new__(Phase);phase.age_control=age.clone();phase.n=len(age)
        return types.SimpleNamespace(num_envs=len(age),h1_phase=phase,command_manager=types.SimpleNamespace(get_term=lambda name:term)),term
    age=phase_state['tensors']['age_control'];command=state['external_command']['vel_command_b'];env,term=env_for(age,command);rng=torch.get_rng_state().clone();cases=[]
    def rejects(fn,env):
        try:fn(env)
        except (AssertionError,RuntimeError):return True
        return False
    assert rejects(legacy,env);cases.append(dict(name='actual_recorded20000_legacy_zero_rejects',passed=True));value=audit(env);assert value['command_matches_existing_publisher'];cases.append(dict(name='actual_recorded20000_matches_authorized_point8_publisher',passed=True))
    ages=torch.tensor([0,99,100,179,180,2401],dtype=age.dtype).repeat((20000+5)//6)[:20000];commands=torch.zeros_like(command);commands[:,0]=((ages>=100)&(ages<180)).float()*.8
    env,term=env_for(ages,commands);audit(env);cases.append(dict(name='age0_99_100_179_180_2401_boundaries_exact',passed=True))
    for name,change in [('unexpected_forward_outside_request',lambda c:c.__setitem__((0,0),.8)),('wrong_requested_speed',lambda c:c.__setitem__((2,0),.4)),('lateral_command',lambda c:c.__setitem__((2,1),.01)),('yaw_command',lambda c:c.__setitem__((2,2),.1)),('nonfinite_command',lambda c:c.__setitem__((2,0),float('nan')))]:
        env,term=env_for(ages,commands);change(term.vel_command_b);assert rejects(audit,env),name;cases.append(dict(name=name+'_still_rejected',passed=True))
    env,term=env_for(ages,commands);env.h1_phase=object();assert rejects(audit,env);cases.append(dict(name='wrong_phase_still_rejected',passed=True))
    env,term=env_for(ages,commands);term.cfg.heading_command=True;assert rejects(audit,env);cases.append(dict(name='heading_override_still_rejected',passed=True))
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    result=dict(epoch=time.time(),passed=True,scope='isolated actual SDK command property and original audit functions plus recorded failed CPU state; not a Kit or GPU/native run',candidate=candidate,cases=cases,actual20000_recorded_state_tested=True,original_class_and_directional_finite_heading_guards_retained=True,zero_command_legacy_scope_source_unchanged=True,no_RNG_draw_or_actor_forward_or_optimizer_call=True,no_command_publisher_or_physics_reward_threshold_change=True,not_installed=True,no_new_H1_GO_or_270mm_skill_result=True)
    put('V98_H1_STEP270_EXTERNAL_COMMAND_AUDIT_RECORDED_BOUNDARY_CPU_ACTUAL.json',result);print(json.dumps(dict(passed=True,cases=len(cases),candidate_SHA=candidate['candidate_runtime_SHA'],not_installed=True)))
except BaseException:
    put('V98_H1_COMMAND_AUDIT_CANDIDATE_CPU_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_replay_or_source_qualification=True));raise
