"""Read-only E0 command lifetimes; initial starts UNKNOWN, no synthetic commands."""
import json
from pathlib import Path
from e0_early_original_resample_passthrough_observer_v1 import produce_typed_instance_JSONL_with_stream_SHA
from e0_original_profile_catalog_v1 import PROFILES,TRANSITION_PHASES,transition_phase

class CommandInstances:
    def __init__(self,t,n,device):
        self.t=t;self.n=n;self.ids=t.arange(n,device=device)
        self.active=t.zeros(n,device=device,dtype=t.bool);self.known=self.active.clone()
        self.uid=t.zeros(n,device=device,dtype=t.long);self.ep=self.uid.clone();self.key=self.uid.clone();self.start=self.uid.clone()
        self.count=self.uid.clone();self.error=t.zeros(n,3,device=device);self.phase=t.zeros(n,9,device=device,dtype=t.long)
        self.ref=t.zeros(n,3,device=device);self.direction=t.zeros(n,device=device);self.yaw=self.direction.clone()
        self.closed=t.zeros(10,n,device=device,dtype=t.long);self.complete=self.closed.clone();self.reset=self.closed.clone();self.left=self.closed.clone();self.right=self.closed.clone();self.full12=self.closed.clone()
        self.acted=self.closed.clone();self.zero=self.closed.clone();self.acted_left=self.closed.clone();self.acted_reset=self.closed.clone();self.acted_right=self.closed.clone();self.all_instance_controls=self.closed.clone()
        self.complete_controls=self.closed.clone();self.complete_errors=t.zeros(10,3,n,device=device)
        self.complete_phase=t.zeros(10,9,n,device=device,dtype=t.long)
        self.records=[];self.record_count=0;self.max_records=n*4;self.retention_limited=False
        self.control=0

    def open(self,ids,context,known_start):
        assert not bool(self.active[ids].any())
        self.active[ids]=True;self.known[ids]=known_start
        for dest,key in ((self.uid,'command_uid'),(self.ep,'episode'),(self.key,'key')):dest[ids]=context[key][ids]
        self.start[ids]=self.control;self.count[ids]=0;self.error[ids]=0;self.phase[ids]=0
        self.ref[ids]=context['command'][ids];self.direction[ids]=context['direction'][ids];self.yaw[ids]=context['signed_yaw'][ids]

    def observe(self,c,after):
        ids=self.ids[~self.active]
        if len(ids):self.open(ids,c,False)
        assert self.t.equal(self.uid,c['command_uid']) and self.t.equal(self.ep,c['episode'])
        assert self.t.equal(self.key,c['key']),'Profile changed inside observed original command'
        self.count+=1;self.error+=self.t.stack(after['errors'],1)
        take=((c['key']==6)|(c['key']==7))&c['written_phase_valid'];ids=self.ids[take]
        if len(ids):self.phase[ids,transition_phase(self.t,c['written_phase'][ids])]+=1

    def close(self,ids,reason):
        assert reason in ('resample','reset','window_end')
        ids=ids[self.active[ids]]
        if not len(ids):return
        t=self.t;key=self.key[ids];idx=(key,ids);known=self.known[ids];count=self.count[ids]
        full=known&(count>0)&(reason=='resample')
        acted=count>0
        self.acted[idx]+=acted.long();self.zero[idx]+=(~acted).long();self.all_instance_controls[idx]+=count
        self.acted_left[idx]+=(acted&~known).long();self.acted_reset[idx]+=acted.long()*int(reason=='reset');self.acted_right[idx]+=acted.long()*int(reason=='window_end')
        self.closed[idx]+=1;self.complete[idx]+=full.long();self.reset[idx]+=int(reason=='reset')
        self.left[idx]+=(~known).long();self.right[idx]+=int(reason=='window_end')
        self.complete_controls[idx]+=t.where(full,count,t.zeros_like(count))
        for j in range(3):self.complete_errors[key,j,ids]+=t.where(full,self.error[ids,j],t.zeros_like(self.error[ids,j]))
        # Exposure, NOT a tolerance/skill gate. Full12 means every original pre12 bin observed.
        transition=(key==6)|(key==7);has12=(self.phase[ids,:8]>0).all(1)
        self.full12[idx]+=(full&transition&has12).long()
        for j in range(9):self.complete_phase[key,j,ids]+=t.where(full,self.phase[ids,j],t.zeros_like(count))
        room=self.max_records-self.record_count;take=ids[:max(0,room)]
        if len(take)<len(ids):self.retention_limited=True
        if len(take):
            # Small immutable records only at actual boundaries, no per-control host transfer.
            columns=dict(env_id=take,episode=self.ep[take],command_uid=self.uid[take],profile=self.key[take],
                         start_observed=self.known[take],first_control=self.start[take],population_controls=self.count[take],
                         errors_sum=self.error[take],transition_phase_controls=self.phase[take],sampled_body_command3=self.ref[take],
                         sampled_world_direction=self.direction[take],sampled_signed_yaw_rad_s=self.yaw[take])
            self.records.append((reason,{k:v.detach().cpu().clone() for k,v in columns.items()}));self.record_count+=len(take)
        self.active[ids]=False

    def finish(self,out,source_SHA):
        self.close(self.ids,'window_end');t=self.t;rows=[]
        for k,label in enumerate(PROFILES):
            den=int(self.complete_controls[k].sum());total=int(self.closed[k].sum())
            rows.append(dict(profile=k,label=label,closed_instance_events=total,unique_env_with_closed_instance=int((self.closed[k]>0).sum()),acted_instance_events=int(self.acted[k].sum()),zero_control_instance_events=int(self.zero[k].sum()),unique_env_with_acted_instance=int((self.acted[k]>0).sum()),unique_env_with_zero_control_instance=int((self.zero[k]>0).sum()),all_acted_instance_population_controls=int(self.all_instance_controls[k].sum()),acted_initial_left_censored_events=int(self.acted_left[k].sum()),acted_reset_ended_events=int(self.acted_reset[k].sum()),acted_window_end_events=int(self.acted_right[k].sum()),
                fully_observed_resample_to_resample_instance_events=int(self.complete[k].sum()),unique_env_with_complete_instance=int((self.complete[k]>0).sum()),
                complete_instance_population_controls=den,complete_instance_seconds=den*.02,
                complete_instance_body_forward_MAE=float(self.complete_errors[k,0].sum())/den if den else None,
                complete_instance_yaw_MAE=float(self.complete_errors[k,1].sum())/den if den else None,
                complete_instance_height_MAE=float(self.complete_errors[k,2].sum())/den if den else None,
                left_censored_instance_events=int(self.left[k].sum()),window_end_right_censored_instance_events=int(self.right[k].sum()),
                reset_ended_instance_events=int(self.reset[k].sum()),complete_transition_instances_with_all_pre12_bins=int(self.full12[k].sum()),
                complete_instance_transition_phase_controls=self.complete_phase[k].sum(-1).cpu().tolist(),
                no_exposure_is_pending_not_pass=den==0,events_not_unique_env=True))
        def record_rows():
            for reason,columns in self.records:
                data={k:v.tolist() for k,v in columns.items()}
                for i in range(len(data['env_id'])):
                    row={k:v[i] for k,v in data.items()};row['end_reason']=reason
                    row['acted_instance']=row['population_controls']>0
                    row['fully_observed_original_command_lifetime']=bool(row['start_observed'] and reason=='resample' and row['acted_instance'])
                    row['start_control_is_first_observation_not_original_start']=not row['start_observed']
                    yield row
        p=Path(out)/'E0_OBSERVED_COMMAND_INSTANCE_RECORDS_ACTUAL.jsonl'
        producer=produce_typed_instance_JSONL_with_stream_SHA(out,p.name,record_rows(),source_SHA=source_SHA)
        return dict(profiles=rows,typed_JSONL_producer_index=producer,acted_and_zero_control_denominators_separate=True,instance_record_rows=self.record_count,instance_record_capacity=self.max_records,
                    instance_record_retention_limited=self.retention_limited,initial_instances_left_censored=True,
                    full_command_definition='Observed original resample boundary to next original resample, same env/episode; reset/end are incomplete; no initial start inferred',
                    transition_phase_names=TRANSITION_PHASES,complete_command_metrics_distinct_from_sampled_2pi_windows=True,
                    episode_reset_is_new_instance_no_cross_reset_credit=True,no_added_actor_RNG_physics_or_command_write=True,
                    record_file=p.name,complete_WM_dataset=False,skill_graduation=False)
