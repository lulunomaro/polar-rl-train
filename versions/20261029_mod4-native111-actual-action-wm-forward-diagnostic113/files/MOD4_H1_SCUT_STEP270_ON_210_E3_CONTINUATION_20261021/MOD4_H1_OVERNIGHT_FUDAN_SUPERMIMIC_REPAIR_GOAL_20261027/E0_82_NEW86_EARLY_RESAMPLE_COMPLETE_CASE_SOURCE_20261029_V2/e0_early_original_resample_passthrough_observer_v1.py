"""NEW-source observer before E0 constructor/resume; never invokes new resampling.

The old late-observer left-censored reports stay unchanged. Actual target SDK
method-AST admission and real logs are mandatory before any new start is known.
"""
from pathlib import Path
import ast,hashlib,json,traceback
MODEL='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'

def method_ast(raw,cls,name):
    c=next(x for x in ast.parse(raw).body if isinstance(x,ast.ClassDef) and x.name==cls)
    fn=next(x for x in c.body if isinstance(x,ast.FunctionDef) and x.name==name)
    if fn.body and isinstance(fn.body[0],ast.Expr) and isinstance(fn.body[0].value,ast.Constant) and isinstance(fn.body[0].value.value,str):fn.body.pop(0)
    return ast.dump(fn,include_attributes=False)

def validate_actual_target_source(command_raw,reference_contract):
    got={name:hashlib.sha256(method_ast(command_raw,'CommandTerm',name).encode()).hexdigest() for name in ('reset','_resample','compute')}
    assert got==reference_contract['CommandTerm_method_AST_SHAs'],'Target original reset/resample ABI/source differs; no fallback'
    return dict(passed=True,actual_target_command_source_SHA=hashlib.sha256(command_raw).hexdigest(),method_AST_SHAs=got,reference_fullfile_not_claimed_identical=True)

class EarlyResampleObserver:
    def __init__(self,t,out,expected_n=20000):
        self.t=t;self.out=Path(out);self.expected_n=expected_n;self.scope=None;self.eligible=None;self.errors=[];self.events=[];self.limited=False;self.reset_depth={};self.undo=[]

    def ids(self,term,ids):
        allids=self.t.arange(term.num_envs,device=term.device)
        return allids if ids is None else allids[ids] if isinstance(ids,slice) else self.t.as_tensor(ids,device=term.device,dtype=self.t.long)

    def log(self,event,**values):
        try:
            if len(self.events)>=256:self.limited=True;return
            self.events.append(dict(event=event,**values))
        except BaseException:self.errors.append(traceback.format_exc())

    def original_resample_returned(self,term,ids):
        try:
            ids=self.ids(term,ids);env=term._env;scope=self.scope
            self.log('ORIGINAL_RESAMPLE_RETURNED',env_identity=id(env),ids_count=len(ids),counter_min=int(term.command_counter[ids].min()) if len(ids) else None,physics_tick=int(env._sim_step_counter),in_resume_scope=bool(scope and scope['env'] is env),in_original_reset=self.reset_depth.get(id(term),0)>0)
            if not (scope and scope['env'] is env and self.reset_depth.get(id(term),0)>0):return
            # Retain the real draw only; no guessed initial age/timer, no fresh sample.
            packet=dict(term=term,ids=ids.detach().clone(),time_left=term.time_left[ids].detach().clone(),counter=term.command_counter[ids].detach().clone(),phase=term.phase_elapsed[ids].detach().clone(),command=term.command[ids].detach().clone(),signed_yaw=term.signed_yaw[ids].detach().clone(),direction=term.world_direction[ids].detach().clone(),standing=term.is_standing_env[ids].detach().clone(),pure=term.is_pure_spin[ids].detach().clone(),moving=term.is_moving_spin[ids].detach().clone(),transition=term.is_transition_spin[ids].detach().clone(),physics_tick=int(env._sim_step_counter))
            scope['observed_actual_resamples'].append(packet)
        except BaseException:self.errors.append(traceback.format_exc())

    def install(self,DirectionalSpinCommand,sensor_resume_module):
        observer=self;had_resample='_resample' in DirectionalSpinCommand.__dict__;had_reset='reset' in DirectionalSpinCommand.__dict__
        old_sample=DirectionalSpinCommand._resample;old_reset=DirectionalSpinCommand.reset;old_resume=sensor_resume_module.resume_sensor_new_episode
        def sample(term,ids):
            result=old_sample(term,ids)
            observer.original_resample_returned(term,ids)
            return result
        def reset(term,*args,**kwargs):
            observer.reset_depth[id(term)]=observer.reset_depth.get(id(term),0)+1
            if observer.scope and observer.scope['env'] is term._env:observer.scope['actual_original_reset_count']+=1
            try:return old_reset(term,*args,**kwargs)
            finally:observer.reset_depth[id(term)]-=1
        def resume(runner,env,path,log_dir):
            assert observer.scope is None,'Observer scope cannot nest'
            scope=dict(env=env,source_path=str(path),actual_original_reset_count=0,observed_actual_resamples=[]);observer.scope=scope;value=None
            try:
                value=old_resume(runner,env,path,log_dir)
                try:
                    packets=scope['observed_actual_resamples']
                    source_ok=bool(value and value.get('source_sha256')==MODEL and value.get('new_physical_episode') and value.get('global_CPU_CUDA_streams_restored'))
                    valid=source_ok and scope['actual_original_reset_count']==1 and len(packets)==1 and not observer.errors
                    if valid:
                        p=packets[0];ids=p['ids'];valid=bool(len(ids)==observer.expected_n and observer.t.equal(ids,observer.t.arange(observer.expected_n,device=ids.device)) and p['physics_tick']==0 and bool((p['phase']==0).all()) and bool((p['counter']==1).all()) and bool(((p['time_left']>=12)&(p['time_left']<=16)).all()))
                    observer.eligible=packets[0] if valid else None
                    observer.log('ORIGINAL_RESUME_RETURNED',source_SHA=value.get('source_sha256') if value else None,real_reset_count=scope['actual_original_reset_count'],real_resample_batches=len(packets),new_initial_start_eligible=valid,NO_reclassification_of_old_late_observer=True)
                except BaseException:
                    observer.eligible=None;observer.errors.append(traceback.format_exc())
                return value
            finally:observer.scope=None
        DirectionalSpinCommand._resample=sample;DirectionalSpinCommand.reset=reset;sensor_resume_module.resume_sensor_new_episode=resume
        def restore():
            if had_resample:DirectionalSpinCommand._resample=old_sample
            else:del DirectionalSpinCommand._resample
            if had_reset:DirectionalSpinCommand.reset=old_reset
            else:del DirectionalSpinCommand.reset
            sensor_resume_module.resume_sensor_new_episode=old_resume
        self.undo.append(restore)

    def verify_current_unchanged_at_first_control(self,term):
        p=self.eligible
        if p is None:return False
        if p['term'] is not term or int(term._env._sim_step_counter)!=0:return False
        pairs={'time_left':'time_left','counter':'command_counter','phase':'phase_elapsed','command':'command','signed_yaw':'signed_yaw','direction':'world_direction','standing':'is_standing_env','pure':'is_pure_spin','moving':'is_moving_spin','transition':'is_transition_spin'}
        return all(self.t.equal(p[key],getattr(term,attr)[p['ids']]) for key,attr in pairs.items())

    def adopt_only_actually_observed_start(self,panel):
        assert self.verify_current_unchanged_at_first_control(panel.cmd),'No real observed unchanged post-restoration start; retain left censor'
        assert not bool(panel.instances.active.any()) and panel.real is panel.cmd._env
        panel.instances.control=1;panel.instances.open(self.eligible['ids'],panel.instance_context(),True)
        # The original declared _resample_command actually reset phase0 and called
        # _write_dynamic; source contract verifies that sequence, not a guessed age.
        panel.written_phase.copy_(self.eligible['phase']);panel.written_valid[self.eligible['ids']]=True
        self.log('NEW_PANEL_ADOPTED_REAL_INITIAL_RESAMPLE',ids_count=len(self.eligible['ids']),not_policy_or_physics_change=True)

    def finish(self):
        for undo in reversed(self.undo):undo()
        self.undo=[];self.out.mkdir(exist_ok=False)
        p=self.eligible
        result=dict(kind='E0_real_initial_postrestore_resample_observer_receipt_v1',source_SHA=MODEL,diagnostic_valid=not self.errors,errors=self.errors,events=self.events,event_retention_limited=self.limited,new_initial_start_eligible=p is not None,old_reports_left_censored_unchanged=True,SDK_target_source_admission_independent=True,no_extra_reset_resample_actor_RNG_or_physics=True)
        if p is not None:
            result.update(ids_count=len(p['ids']),sampled_timer_min=float(p['time_left'].min()),sampled_timer_max=float(p['time_left'].max()),actual_phase_zero=bool((p['phase']==0).all()),physics_tick=p['physics_tick'])
            fields={k:v.detach().cpu().tolist() for k,v in p.items() if self.t.is_tensor(v)}
            rows=({k:v[i] for k,v in fields.items()} for i in range(len(p['ids'])))
            result['real_initial_sampled_command_JSONL_producer']=produce_typed_instance_JSONL_with_stream_SHA(self.out,'E0_REAL_INITIAL_SAMPLED_COMMANDS_ACTUAL.jsonl',rows)
        with (self.out/'E0_REAL_POSTRESTORE_ORIGINAL_RESAMPLE_OBSERVER_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2,allow_nan=False)
        return result

def produce_typed_instance_JSONL_with_stream_SHA(out,name,rows,source_SHA=MODEL,maximum_bytes=256*1024**2):
    """New caller producer only; future collector defaults to INDEX ONLY, not raw."""
    root=Path(out).resolve();assert root.is_dir() and Path(name).name==name and name.endswith('.jsonl')
    path=root/name;h=hashlib.sha256();count=0;size=0;limited=False
    with path.open('xb') as f:
        for row in rows:
            raw=(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n').encode()
            if size+len(raw)>maximum_bytes:limited=True;break
            f.write(raw);h.update(raw);size+=len(raw);count+=1
        f.flush()
    assert path.stat().st_size==size
    value=dict(path=str(path),bytes=size,SHA=h.hexdigest(),rows=count,source_SHA=source_SHA,producer_stream_SHA_no_reread=True,retention_limited=limited,maximum_bytes=maximum_bytes,collector_mode='producer_path_bytes_SHA_metadata_only',content_transfer_default=False,not_complete_WM_dataset=True)
    with (root/(name+'.PRODUCER_INDEX_ACTUAL.json')).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
    return value
