"""W35 original lifecycle passthrough. Does not own/sample/modify any command.

This component proves an initial origin only when the actual W35 outer restore,
original sensor restore/reset and retained write/resample chain are all observed.
The command-instance/cycle accumulator is a separate observer-only consumer.
"""
from pathlib import Path
import ast, hashlib, json, traceback

MODEL='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
PROFILE='E1_G3_verified_plane_signed_straight_world05_yaw12_v1'
FIELDS={
    'timer':'time_left','counter':'command_counter','phase':'phase_elapsed',
    'command':'command','signed_yaw':'signed_yaw','direction':'direction',
    'world_direction':'world_direction','standing':'is_standing_env',
    'linear':'linear','moving':'moving','eligible':'eligible_flat','family':'family',
    'linear_vx':'linear_vx','written_heading':'_command_heading',
    'pure':'is_pure_spin','transition':'is_transition_spin',
}

def method_AST_SHA(raw,cls,name):
    c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef) and n.name==cls)
    fn=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name==name)
    if fn.body and isinstance(fn.body[0],ast.Expr) and isinstance(fn.body[0].value,ast.Constant) and isinstance(fn.body[0].value.value,str):fn.body.pop(0)
    return hashlib.sha256(ast.dump(fn,include_attributes=False).encode()).hexdigest()

def validate_actual_target_sources(command_raw,actual_source_by_relative,contract):
    got={name:method_AST_SHA(command_raw,'CommandTerm',name) for name in ('reset','_resample','compute')}
    assert got==contract['CommandTerm_method_AST_SHAs']
    for relative,wanted in contract['original_domain_source_SHAs'].items():
        assert hashlib.sha256(actual_source_by_relative[relative]).hexdigest()==wanted,relative
    assert contract['model_SHA']==MODEL and contract['original_num_envs']==20000
    assert contract['moving_yaw_abs_range']==[1.,2.] and contract['straight_abs_vx_range']==[1.,1.5]
    assert contract['original_command_timer_seconds']==[12.,16.]
    assert contract['original_world_progress_nominal_m_s']==.5
    return dict(passed=True,actual_target_CommandTerm_AST=got,
        actual_target_command_source_SHA=hashlib.sha256(command_raw).hexdigest(),
        exact_W35_retained_G3_and_saved_episode_baseline_source_pinned=True,
        source_check_NOT_GPU_or_initial_origin_proof=True)

class W35EarlyObserver:
    def __init__(self,t,out,expected_n=20000):
        self.t=t;self.out=Path(out);self.n=expected_n
        self.expected_profile=PROFILE
        self.inner=None;self.outer=None;self.eligible=None;self.outer_receipt=None
        self.reset_depth={};self.seen_terms={};self.events=[];self.errors=[];self.limited=False;self.undo=[]
        self.event_counts={};self.consumer=None

    def ids(self,term,ids):
        all_ids=self.t.arange(term.num_envs,device=term.device)
        return all_ids if ids is None else all_ids[ids] if isinstance(ids,slice) else self.t.as_tensor(ids,device=term.device,dtype=self.t.long)

    def log(self,event,**values):
        self.event_counts[event]=self.event_counts.get(event,0)+1
        if len(self.events)>=256:self.limited=True;return
        self.events.append(dict(event=event,**values))

    def notify(self,event,term,ids,**metadata):
        if self.consumer is not None:
            try:self.consumer(event,term,ids,**metadata)
            except BaseException:self.errors.append(traceback.format_exc())

    def packet(self,term,ids):
        p={key:getattr(term,name)[ids].detach().clone() for key,name in FIELDS.items()}
        p.update(term=term,ids=ids.detach().clone(),tick=int(term._env._sim_step_counter),
            private_mode_rng=term._mode_rng.get_state().clone(),
            private_retention_rng=term._retention_rng.get_state().clone())
        return p

    def install(self,Command,sensor_module,retention_module):
        obs=self;old_sample=Command._resample;old_reset=Command.reset;old_write=Command._write_dynamic
        old_sensor=sensor_module.resume_sensor_new_episode;old_retention=retention_module.resume_e1_new_episode
        inherited={key:key not in Command.__dict__ for key in ('_resample','reset','_write_dynamic')}

        def write(term,ids):
            obs.seen_terms[id(term)]=term;scope=obs.inner;phase=None;selected=None
            try:
                # The superclass's intermediate write is intentionally suppressed
                # by ORIGINAL W35 _retention_resampling. Do not count it as a write.
                if scope and scope['env'] is term._env and obs.reset_depth.get(id(term),0) and not term._retention_resampling:
                    selected=obs.ids(term,ids);phase=term.phase_elapsed[selected].detach().clone()
            except BaseException:obs.errors.append(traceback.format_exc())
            result=old_write(term,ids)
            try:
                if phase is not None:scope['writes'].append(dict(term=term,ids=selected.detach().clone(),phase=phase,tick=int(term._env._sim_step_counter)))
            except BaseException:obs.errors.append(traceback.format_exc())
            return result

        def sample(term,ids):
            obs.seen_terms[id(term)]=term
            before_timer=None;before_counter=None
            try:
                selected=obs.ids(term,ids)
                before_timer=term.time_left[selected].detach().clone()
                before_counter=term.command_counter[selected].detach().clone()
            except BaseException:obs.errors.append(traceback.format_exc())
            result=old_sample(term,ids)
            try:
                selected=obs.ids(term,ids);scope=obs.inner
                within_reset=bool(obs.reset_depth.get(id(term),0))
                obs.log('ORIGINAL_W35_RESAMPLE_RETURNED',ids_count=len(selected),tick=int(term._env._sim_step_counter),within_original_reset=within_reset)
                if scope and obs.outer and scope['env'] is term._env and obs.outer['env'] is term._env and within_reset:
                    scope['packets'].append(obs.packet(term,selected))
                obs.notify('AFTER_ORIGINAL_RESAMPLE',term,selected,within_original_reset=within_reset,
                    original_prior_timer=before_timer,original_prior_counter=before_counter)
            except BaseException:obs.errors.append(traceback.format_exc())
            return result

        def reset(term,*args,**kwargs):
            obs.reset_depth[id(term)]=obs.reset_depth.get(id(term),0)+1
            if obs.inner and obs.inner['env'] is term._env:obs.inner['resets']+=1
            try:
                ids=kwargs.get('env_ids',args[0] if args else None)
                obs.notify('BEFORE_ORIGINAL_RESET',term,obs.ids(term,ids))
                return old_reset(term,*args,**kwargs)
            finally:obs.reset_depth[id(term)]-=1

        def sensor(runner,env,path,log_dir):
            assert obs.inner is None
            s=dict(env=env,resets=0,packets=[],writes=[]);obs.inner=s
            try:
                result=old_sensor(runner,env,path,log_dir)
                try:
                    valid=bool(obs.outer and obs.outer['env'] is env and result.get('source_sha256')==MODEL and result.get('new_physical_episode') and result.get('global_CPU_CUDA_streams_restored') and s['resets']==1 and len(s['packets'])==len(s['writes'])==1 and not obs.errors)
                    if valid:
                        p=s['packets'][0];w=s['writes'][0];ids=p['ids']
                        valid=bool(len(ids)==obs.n and obs.t.equal(ids,obs.t.arange(obs.n,device=ids.device))
                            and p['tick']==w['tick']==0 and obs.t.equal(ids,w['ids']) and w['term'] is p['term']
                            and bool((p['counter']==1).all()) and bool((p['phase']==0).all()) and obs.t.equal(w['phase'],p['phase'])
                            and bool(((p['timer']>=12)&(p['timer']<=16)).all()))
                        moving=p['moving'];linear=p['linear'];standing=p['standing']
                        valid=valid and bool(((p['signed_yaw'][moving].abs()>=1)&(p['signed_yaw'][moving].abs()<=2)).all())
                        valid=valid and bool(((p['linear_vx'][linear].abs()>=1)&(p['linear_vx'][linear].abs()<=1.5)).all())
                        valid=valid and not bool((p['pure']|p['transition']).any()) and not bool(((moving|linear)&(~p['eligible']|standing)).any())
                    obs.eligible=s['packets'][0] if valid else None
                    obs.log('ORIGINAL_W35_SENSOR_RESUME_RETURNED',initial_origin_candidate=valid,
                        original_resets=s['resets'],original_resample_batches=len(s['packets']),effective_retained_write_batches=len(s['writes']))
                except BaseException:obs.eligible=None;obs.errors.append(traceback.format_exc())
                return result
            finally:obs.inner=None

        def retention(runner,env,path,log_dir):
            assert obs.outer is None
            obs.outer=dict(env=env)
            try:
                result=old_retention(runner,env,path,log_dir)
                try:
                    fields=('source_sha256','command_profile','predecessor_command_state_restored_exact',
                        'actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact',
                        'old_full_D1_D7_optimizer_global_named_streams_verified','one_new_physical_episode','E1_episode_incremented_once')
                    valid=bool(result.get('source_sha256')==MODEL and result.get('command_profile')==obs.expected_profile
                        and all(result.get(k) is True for k in fields[2:]))
                    obs.outer_receipt={k:result.get(k) for k in fields}
                    if not valid:obs.eligible=None
                    obs.log('ORIGINAL_W35_COMPLETE_RETENTION_RESUME_RETURNED',source_private_command_and_episode_valid=valid,
                        initial_origin_eligible=obs.eligible is not None)
                except BaseException:obs.eligible=None;obs.errors.append(traceback.format_exc())
                return result
            finally:obs.outer=None

        Command._resample=sample;Command.reset=reset;Command._write_dynamic=write
        sensor_module.resume_sensor_new_episode=sensor;retention_module.resume_e1_new_episode=retention
        def restore():
            for name,old in (('_resample',old_sample),('reset',old_reset),('_write_dynamic',old_write)):
                if inherited[name]:delattr(Command,name)
                else:setattr(Command,name,old)
            sensor_module.resume_sensor_new_episode=old_sensor;retention_module.resume_e1_new_episode=old_retention
            for term in obs.seen_terms.values():
                shadow=term.__dict__.get('_write_dynamic')
                if getattr(shadow,'__func__',None) is write:del term.__dict__['_write_dynamic']
        self.undo.append(restore)

    def verify_current_unchanged(self,term):
        p=self.eligible
        if p is None or self.outer_receipt is None or self.errors:return False
        if p['term'] is not term or int(term._env._sim_step_counter)!=0 or term.manual_evaluation_mode or term._dt!=.02 or term.progress_goal!=.5:return False
        return all(self.t.equal(p[key],getattr(term,name)[p['ids']]) for key,name in FIELDS.items()) and self.t.equal(p['private_mode_rng'],term._mode_rng.get_state()) and self.t.equal(p['private_retention_rng'],term._retention_rng.get_state())

    def adopt_original_origin(self,term,on_observed_start):
        if not self.verify_current_unchanged(term):
            self.log('INITIAL_W35_ORIGIN_NOT_ADOPTED_LEFT_CENSORED');return False
        # Consumer writes only its own metadata/accumulators; never Command fields.
        on_observed_start(self.eligible)
        self.log('ACTUAL_W35_POSTRESTORE_INITIAL_ORIGIN_ADOPTED',ids_count=len(self.eligible['ids']))
        return True

    def finish(self):
        for undo in reversed(self.undo):undo()
        self.undo=[];self.consumer=None;self.out.mkdir(exist_ok=False)
        result=dict(kind='W35_original_retained_postrestore_resample_observer_source_v1',source_SHA=MODEL,
            diagnostic_valid=not self.errors,errors=self.errors,events=self.events,event_counts=self.event_counts,
            bounded_event_examples_truncated=self.limited,initial_origin_eligible=self.eligible is not None,
            original_W35_resume_selected_fields=self.outer_receipt,
            no_extra_original_sampler_reset_write_actor_RNG_physics=True,
            no_new_standing_pure_yaw_or_E2_command_task=True,not_skill_or_WM_qualification=True)
        if self.eligible is not None:
            p=self.eligible;result.update(ids_count=len(p['ids']),timer_min=float(p['timer'].min()),timer_max=float(p['timer'].max()),
                phase_zero=bool((p['phase']==0).all()),physics_tick=p['tick'])
        with (self.out/'W35_ORIGINAL_EARLY_RETAINED_RESAMPLE_OBSERVER_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2,allow_nan=False)
        return result
