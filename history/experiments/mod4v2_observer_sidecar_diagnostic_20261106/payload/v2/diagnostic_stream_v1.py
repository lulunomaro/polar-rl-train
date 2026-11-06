"""Producer-streaming raw receipts and private same-PRE-tick summaries.
No physics/sensor/control imports, no reread of raw files for hashes/analysis.
"""
from pathlib import Path
import hashlib,json,math

class HashText:
    def __init__(self,path):
        self.path=Path(path);self.file=self.path.open('x',encoding='utf-8',buffering=1,newline='\n')
        self.sha=hashlib.sha256();self.bytes=0;self.lines=0
    def write(self,text):
        data=text.encode('utf-8');self.file.write(text);self.sha.update(data)
        self.bytes+=len(data);self.lines+=text.count('\n')
    def flush(self):self.file.flush()
    def close(self):self.file.close()
    def receipt(self):return dict(path=str(self.path),bytes=self.bytes,lines=self.lines,sha256=self.sha.hexdigest(),source='producer streaming,no payload reread')

class MotorAudit:
    def __init__(self,path):
        self.writer=HashText(path);self.windows=0;self.rows=0;self.peak_contact=None
        self.sections={name:self.bucket()for name in ('all','score_2_12','left_low','right_low','whole_low')}
    @staticmethod
    def bucket():return dict(ticks=0,first_dc_changed_ticks6=[0]*6,post_gain_dc_changed_ticks6=[0]*6,
        any_first_dc_changed_ticks=0,any_post_gain_dc_changed_ticks=0,any_dc_changed_ticks=0,
        after_second_dc_to_held_changed_ticks=0,held_abs_peak_tau6_Nm=[0.]*6,speed_abs_peak6_pre=[0.]*6)
    @staticmethod
    def add(b,r):
        b['ticks']+=1;s0,s1=r['clip_stages'];m0=s0['changed6'];m1=s1['changed6']
        for j in range(6):
            b['first_dc_changed_ticks6'][j]+=int(m0[j]);b['post_gain_dc_changed_ticks6'][j]+=int(m1[j])
            b['held_abs_peak_tau6_Nm'][j]=max(b['held_abs_peak_tau6_Nm'][j],abs(r['held_ctrl_tau6'][j]))
            b['speed_abs_peak6_pre'][j]=max(b['speed_abs_peak6_pre'][j],abs(s0['speed6_pre'][j]))
        b['any_first_dc_changed_ticks']+=int(any(m0));b['any_post_gain_dc_changed_ticks']+=int(any(m1))
        b['any_dc_changed_ticks']+=int(any(m0)or any(m1))
        b['after_second_dc_to_held_changed_ticks']+=int(s1['after_tau6']!=r['held_ctrl_tau6'])
    def observe(self,k,request,window,summary,contacts):
        if not summary.get('complete')or len(window)!=20 or summary['driver_tick_delta']!=20:
            raise ValueError('Actual driver observation incomplete; retain prefix')
        self.windows+=1;by_tick={int(round(c['time_s']/.0005)):c for c in contacts}
        for index,original in enumerate(window):
            r=dict(original);tick=int(r['physics_tick_pre'])
            if tick!=20*k+index or len(r['clip_stages'])!=2:raise ValueError('Driver tick/stage mismatch')
            if not all(math.isfinite(v)for v in r['held_ctrl_tau6']):raise ValueError('Nonfinite held diagnostic')
            r.update(control_index=k,private_grading_only=True,controller_or_force_proxy_input=False)
            self.add(self.sections['all'],r);c=by_tick.get(tick)
            if 4000<=tick<24000:
                if c is None:raise ValueError('Missing same-PRE-tick contact sample')
                self.add(self.sections['score_2_12'],r)
                r['contact_cache_normal_N2']=c['main_normal_N2'];r['all_environment_positive_normal_N']=c['all_environment_positive_normal_N']
                for name,yes in (('left_low',c['main_normal_N2'][0]<=1.),('right_low',c['main_normal_N2'][1]<=1.),('whole_low',c['all_environment_positive_normal_N']<=1.)):
                    if yes:self.add(self.sections[name],r)
                magnitude=max(c['main_normal_N2'])
                if self.peak_contact is None or magnitude>self.peak_contact['maximum_main_normal_N']:
                    self.peak_contact=dict(maximum_main_normal_N=magnitude,control_index=k,physics_tick_pre=tick,
                        time_s_pre=r['time_s_pre'],main_normal_N2=c['main_normal_N2'],held_ctrl_tau6_Nm=r['held_ctrl_tau6'],
                        clip_stages=r['clip_stages'],request_tau6_at_command_bin_start_Nm=list(map(float,request)),
                        event_epoch='same actual driver PRE tick; request is earlier100Hz bin,not simultaneous measured torque')
            self.writer.write(json.dumps(r,separators=(',',':'),allow_nan=False)+'\n');self.rows+=1
    def summary(self):
        result={}
        for name,b in self.sections.items():
            c=dict(b);n=b['ticks']
            c['first_dc_changed_duty6']=[x/n for x in b['first_dc_changed_ticks6']]if n else None
            c['post_gain_dc_changed_duty6']=[x/n for x in b['post_gain_dc_changed_ticks6']]if n else None
            c['no_same_tick_dc_change_ticks']=n-b['any_dc_changed_ticks'];result[name]=c
        return dict(observed_control_windows=self.windows,actual_observed_physics_rows=self.rows,
            sections=result,maximum_main_contact_event=self.peak_contact,raw=self.writer.receipt(),
            controller_truth_input=False,measured_hardware_torque=False,
            caveat='DC change is original clip input/output inequality,not rail occupancy/current/temperature/delivery;coincidence cannot prove a unique cause or rule out earlier clipping')
    def flush(self):self.writer.flush()
    def close(self):self.writer.close()
