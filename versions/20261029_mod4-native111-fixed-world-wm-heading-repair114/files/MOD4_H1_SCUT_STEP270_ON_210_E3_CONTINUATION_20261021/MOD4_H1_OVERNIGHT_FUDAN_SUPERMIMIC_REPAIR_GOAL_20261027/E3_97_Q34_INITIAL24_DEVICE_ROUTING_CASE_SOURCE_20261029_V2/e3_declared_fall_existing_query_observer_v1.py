"""NEW-purpose diagnostic overlay only. No extra SDK/actor/RNG/physics calls.

Existing closure_errors pos/quaternion reads are tapped, not duplicated. Therefore
there is NO pre-first-physics or per-substep closure claim: those remain unknown.
Caller must bind source/task/restore and actual limits from the ORIGINAL existing
get_dof_limits read, and install before the initial place_declared_fall call.
"""
from pathlib import Path
import ast,hashlib,json,traceback

TASK_SHA='30ce41126a1a9b78a1c2b446281b28f4555c28052bfaa7c0e9a76079cf561fc5'
BANK_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'

def closure_overlay_source(source_raw):
    assert hashlib.sha256(source_raw).hexdigest()==TASK_SHA
    tree=ast.parse(source_raw);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='closure_errors')
    original=ast.dump(fn,include_attributes=False)
    assert isinstance(fn.body[-1],ast.Return) and isinstance(fn.body[-1].value,ast.Name) and fn.body[-1].value.id=='out'
    # Original getter assignment pos,quat appears once; tap consumes THESE locals.
    assert sum(isinstance(n,ast.Attribute) and n.attr=='body_pos_w' for n in ast.walk(fn))==1
    assert sum(isinstance(n,ast.Attribute) and n.attr=='body_quat_w' for n in ast.walk(fn))==1
    tap=ast.parse('_E3_DECLARED_FALL_EXISTING_QUERY_TAP(env,pos,quat,out)').body[0]
    ast.copy_location(tap,fn.body[-1]);fn.body.insert(-1,tap)
    inverse=ast.parse(ast.unparse(fn)).body[0];inverse.body.pop(-2)
    assert ast.dump(inverse,include_attributes=False)==original
    return ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),dict(passed=True,one_added_tap_call_only=True,original_numeric_AST_exact_after_tap_removed=True,original_body_position_and_quaternion_getters_once_each=True,no_extra_closure_or_SDK_query=True)

def diagnostic_select(t,value,index):
    # Index dtype follows the index, never the floating target tensor.
    assert t.is_tensor(index) and index.dtype in (t.long,t.bool)
    return value[index.to(device=value.device,dtype=index.dtype)]

def diagnostic_outside_actual_limits(q,limits):
    # This copy is diagnostic-only; neither original cache q nor limits changes.
    compare_q=q.to(device=limits.device)
    return (compare_q[None]<limits[:,:,0])|(compare_q[None]>limits[:,:,1])

class ExistingQueryObserver:
    def __init__(self,e,t,out,existing_gas_limits,authored_evaluate,maximum_rows=256):
        self.e=e;self.t=t;self.out=Path(out);self.out.mkdir(exist_ok=False)
        self.limit=int(maximum_rows);assert 1<=self.limit<=256
        self.evaluator=authored_evaluate;self.rows=[];self.errors=[];self.limited=False;self.seen=set();self.undo=[];self.bytes=0
        assert e.num_envs==20000 and e.physics_dt==.0025 and e.step_dt==.02
        assert e._e3_fixed_reset_cache.pick==34 and e._e3_fixed_reset_cache.source_sha==BANK_SHA
        self.gas_limits=None;self.gas_ids=list(e._spring_pressure.ids)
        assert len(self.gas_ids)==2
        if existing_gas_limits is not None:self.bind_original_limit_read(existing_gas_limits)
        p=e.recovery.recipe
        self.ids=t.cat([(p==k).nonzero(as_tuple=True)[0][:2] for k in range(13)])
        self.original_joint=e.scene['robot'].write_joint_state_to_sim;self.original_root=e.scene['robot'].write_root_state_to_sim
        self.original_apply=e._physics_action_delay.queue.apply;self.current_place=None

    def bind_original_limit_read(self,limits):
        """Caller supplies the ORIGINAL worker readback; never initiates a query."""
        assert limits.shape==(20000,2,2) and self.gas_limits is None
        self.gas_limits=limits.detach().clone()

    def snapshot(self,x):
        if hasattr(x,'torch'):x=x.torch
        if self.t.is_tensor(x):return dict(shape=list(x.shape),dtype=str(x.dtype),value=x.detach().cpu().tolist())
        if isinstance(x,dict):return {str(k):self.snapshot(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [self.snapshot(v) for v in x]
        if x is None or isinstance(x,(str,int,float,bool)):return x
        raise TypeError('Unsupported actual diagnostic value '+type(x).__name__)

    def safe(self,event,**data):
        # Diagnostic invalid is explicit; never change original physical/error flow.
        try:
            if len(self.rows)>=self.limit:self.limited=True;return
            row=dict(event=event,physics_tick=int(self.e._sim_step_counter),public_recovery_age=self.snapshot(diagnostic_select(self.t,self.e.recovery.age,self.ids)),values=self.snapshot(data))
            size=len(json.dumps(row,separators=(',',':'),allow_nan=False).encode())
            if self.bytes+size>16*1024**2:self.limited=True;return
            self.rows.append(row);self.bytes+=size
        except BaseException:self.errors.append(traceback.format_exc())

    def before_place(self,ids):
        ids=self.t.as_tensor(ids,device=self.e.device,dtype=self.t.long)
        selected=ids[self.t.isin(ids,self.ids)];self.current_place=selected
        if len(selected):
            c=self.e._e3_fixed_reset_cache;recipe=diagnostic_select(self.t,self.e.recovery.recipe,selected);q=c._q[self.gas_ids]
            limits=None if self.gas_limits is None else diagnostic_select(self.t,self.gas_limits,selected)
            self.safe('DECLARED_FALL_BEFORE_ORIGINAL_WRITE',ids=selected,recipe=recipe,cached_q30=c._q,cached_gas_q2=q,original_actual_limits2=limits,
                      original_limit_read_not_yet_bound=limits is None,cached_q_gas_outside_actual_limits=None if limits is None else diagnostic_outside_actual_limits(q,limits),cached_recipe_quat_xyzw=diagnostic_select(self.t,c._quat,recipe),
                      cached_sampled_minimum=diagnostic_select(self.t,c._minimum,recipe),declared_root_z=.0001-diagnostic_select(self.t,c._minimum,recipe),env_origins_z=diagnostic_select(self.t,self.e.scene.env_origins,selected)[:,2],
                      original74_reset_q=diagnostic_select(self.t,self.e._rescue_reset_q,selected),bank_pose_index=34,bank_SHA=BANK_SHA,
                      qerr_before_this_placement_is_NOT_after_placement_proof=True,sampled_minimum_NOT_cooked_manifold_proof=True)

    def install_robot_queue(self):
        observer=self;robot=self.e.scene['robot']
        def joint(q,dq,*args,**kw):
            try:
                if observer.current_place is not None and len(observer.current_place):
                    ids=kw['env_ids'];mask=observer.t.isin(ids,observer.ids.to(device=ids.device,dtype=ids.dtype))
                    observer.safe('ORIGINAL_JOINT_WRITE_REQUEST',q30=diagnostic_select(observer.t,q,mask),dq30=diagnostic_select(observer.t,dq,mask),env_ids=ids[mask],args_omitted_from_log=len(args))
            except BaseException:observer.errors.append(traceback.format_exc())
            return observer.original_joint(q,dq,*args,**kw)
        def root(state,*args,**kw):
            try:
                if observer.current_place is not None and len(observer.current_place):
                    ids=kw['env_ids'];mask=observer.t.isin(ids,observer.ids.to(device=ids.device,dtype=ids.dtype))
                    observer.safe('ORIGINAL_ROOT_WRITE_REQUEST',root13=diagnostic_select(observer.t,state,mask),env_ids=ids[mask],args_omitted_from_log=len(args))
            except BaseException:observer.errors.append(traceback.format_exc())
            return observer.original_root(state,*args,**kw)
        def apply(key,tick):
            result=observer.original_apply(key,tick)
            # Original result is logged AFTER original apply selection, before caller integration.
            if int(tick)<16:observer.safe('ORIGINAL_QUEUE_APPLY_RESULT',group=key,tick=int(tick),value=diagnostic_select(observer.t,result,observer.ids))
            return result
        robot.write_joint_state_to_sim=joint;robot.write_root_state_to_sim=root;self.e._physics_action_delay.queue.apply=apply
        self.undo.extend([(robot,'write_joint_state_to_sim',self.original_joint),(robot,'write_root_state_to_sim',self.original_root),(self.e._physics_action_delay.queue,'apply',self.original_apply)])

    def existing_closure(self,e,pos,quat,errors):
        if e is not self.e:return
        try:
            tick=int(e._sim_step_counter)
            if tick in self.seen or tick>192:return
            self.seen.add(tick)
            if len(self.rows)>=self.limit:self.limited=True;return
            # Pure authored shape math using original closure query's cached pos/quat.
            pp=pos.torch if hasattr(pos,'torch') else pos;qq=quat.torch if hasattr(quat,'torch') else quat
            ids=self.ids;clear=self.evaluator(diagnostic_select(self.t,pp,ids),diagnostic_select(self.t,qq,ids),e.e3_shapes)
            self.safe('ORIGINAL_CLOSURE_QUERY_CACHED_INPUT_AND_RESULT',ids=ids,recipe=diagnostic_select(self.t,e.recovery.recipe,ids),episode_length_buf=diagnostic_select(self.t,e.episode_length_buf,ids),
                      pos31=diagnostic_select(self.t,pp,ids),quat31_xyzw=diagnostic_select(self.t,qq,ids),per_loop_anchor_residual={k:diagnostic_select(self.t,v,ids) for k,v in errors.items()},
                      authored_cached_clearance34=clear,authored_floor_z=0.,NOT_cooked_contact_manifold=True,
                      no_pre_first_physics_or_per_substep_claim=True)
        except BaseException:self.errors.append(traceback.format_exc())

    def finish(self):
        for obj,name,old in reversed(self.undo):setattr(obj,name,old)
        self.undo=[]
        value=dict(kind='E3_original_reset_request_existing_closure_query_diagnostic_v1',diagnostic_valid=not self.errors,errors=self.errors,records=self.rows,retention_limited=self.limited,
                   payload_bytes=self.bytes,payload_capacity16MiB=True,original_placement_guard_physics_action_model_unchanged=True,no_extra_SDK_actor_RNG_or_physics_call=True,
                   initial_requested_pose_not_actual_FK_or_manifold=True,original_query_at_control_end_not_each_physics_callback=True,
                   no_unique_root_cause_inferred=True,no_PPO_Cwrite_or_skill_credit=True)
        with (self.out/'E3_RESET_REQUEST_EXISTING_CLOSURE_QUERY_DIAGNOSTIC_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
        return value

def install_before_resume(RecoveryEnv,task_module,task_source_raw,observer_factory):
    """Typed NEW task integration point; restores class/module at finish, no disk edit."""
    old_place=RecoveryEnv.place_declared_fall;old_closure=task_module.closure_errors;registry={}
    tree,proof=closure_overlay_source(task_source_raw)
    old_tap=task_module.__dict__.get('_E3_DECLARED_FALL_EXISTING_QUERY_TAP');had_tap='_E3_DECLARED_FALL_EXISTING_QUERY_TAP' in task_module.__dict__
    def tap(env,pos,quat,result):
        observer=registry.get(id(env))
        if observer is not None:observer.existing_closure(env,pos,quat,result)
    task_module.__dict__['_E3_DECLARED_FALL_EXISTING_QUERY_TAP']=tap
    exec(compile(tree,old_closure.__code__.co_filename,'exec'),task_module.__dict__)
    def place(env,ids):
        if id(env) not in registry:
            observer=observer_factory(env);registry[id(env)]=observer;observer.install_robot_queue()
        observer=registry[id(env)]
        try:observer.before_place(ids)
        except BaseException:observer.errors.append(traceback.format_exc())
        try:return old_place(env,ids)
        finally:observer.current_place=None
    RecoveryEnv.place_declared_fall=place
    def finish():
        RecoveryEnv.place_declared_fall=old_place;task_module.closure_errors=old_closure
        if had_tap:task_module.__dict__['_E3_DECLARED_FALL_EXISTING_QUERY_TAP']=old_tap
        else:task_module.__dict__.pop('_E3_DECLARED_FALL_EXISTING_QUERY_TAP',None)
        return [observer.finish() for observer in registry.values()]
    def bind_limits(env,limits):registry[id(env)].bind_original_limit_read(limits)
    return finish,proof,bind_limits
