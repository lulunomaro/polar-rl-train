"""R28 freeze new cases before any model/physics; original M0 and gates unchanged."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
D=R/'T01_NOMINAL_BAND_TRAIN_V1';SRC=R/'T01_NOMINAL_BAND_M0_V1'
def main():
 if D.exists():raise RuntimeError('TRAIN prefix already prepared; never prepare twice')
 protocol=json.loads((SRC/'PROTOCOL.json').read_text(encoding='utf-8'))
 old_gates=protocol['gates'].copy();old_windows=protocol['windows'].copy()
 specs=[dict(id='nominal_band_stand',seed=520181,nominal=True,profile='stand'),
  dict(id='train_dr_stand_1',seed=520182,nominal=False,profile='stand'),
  dict(id='train_dr_slow_1',seed=520183,nominal=False,profile='slow'),
  dict(id='train_dr_stand_2',seed=520184,nominal=False,profile='stand'),
  dict(id='train_dr_slow_2',seed=520185,nominal=False,profile='slow')]
 sources=['runtime_v2.py','bridge_v2.py','dr_v2.py','model_builder_v2.py','v2_linearization.py','nominal_gain_v2.json',
  'controller_base_v2.py','controller_coord_v2.py','controller_roll_v2.py','controller_heading_v2.py',
  'observed_bridge_v1.py','actuation_telemetry_v1.py','public_signal_adapter_v1.py','signal_alignment_v1.py','diagnostic_stream_v1.py','SENSOR_TIME_METADATA_V1/publisher.py']
 pins=[dict(path=str(R/rel),sha256=hashlib.sha256((R/rel).read_bytes()).hexdigest(),bytes=(R/rel).stat().st_size)for rel in sources]
 protocol.update(id='MOD4V2_HW300N60_T01_NOMINAL_BAND_M0_TRAIN_SCREEN_001',
  status='frozen_before_new_nominal_stand_and_bounded_TRAIN_DR',formal_cases=specs,
  scope='Same M0/source-band/original gates. Bounded new TRAIN only, not T36 holdout/reliability or robust corridor certificate.',
  frozen_small_sources=pins,
  execution_policy=dict(max_parallel_physics_workers=2,threads_per_worker=1,
   nominal_first=520181,nominal_failure_pauses_all_DR=True,
   wave1=[520182,520183],wave2=[520184,520185],
   wave2_requires_wave1_original_screen_and_observed_scope_pass=True,
   software_error_stop_no_retry=True,no_seed_redraw_or_parameter_change=True,
   D0_nominal_branch_not_full_nominal=True,old_520112_to_520115_still_unused=True),
  replay_of_old_case=False,training_only=True)
 protocol['notes']+=['Five new fixed seeds selected without sampling or score search; FullDR draws once on fresh model per case.',
  'D0-only 20% nominal branch leaves D1-D7 active; report actual drawn delays/gains rather than claiming all delay values were covered.',
  'Original contact/attitude gates and the separate observed-scope diagnostic stay unchanged. No robustness certificate created.',
  'Pause wave2 when wave1 fails; no gain changes or additional scenario changes during this frozen screen.']
 assert protocol['gates']==old_gates and protocol['windows']==old_windows
 text=(SRC/'run_nominal_band_m0.py').read_text(encoding='utf-8')
 a="    protocol = json.loads((D/'PROTOCOL.json').read_text(encoding='utf-8'))"
 b=a+"\n    import hashlib\n    for pin in protocol['frozen_small_sources']:\n        source=Path(pin['path'])\n        if source.stat().st_size!=pin['bytes'] or hashlib.sha256(source.read_bytes()).hexdigest()!=pin['sha256']:\n            raise RuntimeError('Frozen small source changed before case: '+str(source))"
 if text.count(a)!=1:raise RuntimeError('Protocol anchor changed')
 text=text.replace(a,b,1)
 a="status='NEW_NOMINAL_BAND_M0_NOT_ROBUST_CORRIDOR_OR_OLD_ROUTE_COMPARISON_OR_T01_GRADUATION'"
 if text.count(a)!=1:raise RuntimeError('Status anchor changed')
 text=text.replace(a,"status='FROZEN_NOMINAL_BAND_M0_TRAIN_SCREEN_NOT_T36_OR_ROBUST_CORRIDOR_CERTIFICATE'",1)
 compile(text,str(D/'run_band_train_case.py'),'exec')
 D.mkdir(exist_ok=False)
 (D/'run_band_train_case.py').write_text(text,encoding='utf-8')
 (D/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
 (D/'PREPARATION.json').write_text(json.dumps(dict(models=0,physics_steps=0,old_raw_reads=0,
  controller_changed=False,old_gates_and_windows_unchanged=True,source= str(SRC/'run_nominal_band_m0.py'),
  changed_runner_parts=['small-source identity guard before prefix/model','result scope label only'],
  seeds_frozen_before_drawing=[s['seed']for s in specs],prepared_not_executed=True),indent=2),encoding='utf-8')
 print('FROZEN_NEW_BAND_TRAIN_001',len(specs),'newcases; no model/physics/DR sampling/old raw; nominal first, then <=2 workers')
if __name__=='__main__':main()
