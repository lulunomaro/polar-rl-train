"""Reconstruct original recovery clocks/modes/events from saved pre-reset rows."""
from pathlib import Path
import sys,numpy as np,torch

def audit(B,folder,steps):
    A=B/folder/'out'
    runtime=B/'E3_recovery104_native60_payload/job0/runtime/isaac/mod4'
    sys.path.insert(0,str(runtime));from e3_public_recovery_phase_v1 import RecoveryPhase
    c=np.load(A/'CONTROL_ACTUAL.npz',allow_pickle=False)
    p=np.load(A/'PHYSICAL_CALLBACK_ACTUAL.npz',allow_pickle=False)
    phase=RecoveryPhase(104,'cpu');ids=torch.arange(104)
    angle=torch.tensor([-90.,-60.,-30.,30.,60.,90.])[phase.recipe.clamp(max=11)%6]*torch.pi/180
    angle[phase.recipe==12]=0;upright=(1+torch.cos(angle))/2
    phase.reset(ids,upright);previous=np.zeros((104,6),np.float32);gravity_error=delta_error=peak_error=0.
    force_names=__import__('json').loads((A/'GEOMETRY_ACTUAL.json').read_bytes())['contact_names']
    wheel=[force_names.index(n) for n in ('left_wheel','right_wheel')]
    force_error=float(abs(p['all31_force'][:,:,wheel]-p['wheel_raw']).max());assert force_error<=.1
    assert np.array_equal(c['root13'],p['root13'][7::8])
    for i in range(steps):
        assert np.array_equal(previous,c['policy'][i,:,22:28]),('previous6',i)
        mode=np.zeros((104,7),np.float32);mode[np.arange(104),phase.mode().numpy()]=1
        assert np.array_equal(c['policy'][i,:,28:35],mode),('public_mode',i)
        phase.begin();root=torch.from_numpy(c['root13'][i].copy());x,y,z,w=root[:,3:7].unbind(-1)
        gravity=-(1-2*(x*x+y*y));gravity_error=max(gravity_error,float(abs(gravity.numpy()-c['gravity_z'][i]).max()));assert gravity_error<=1e-6
        phase.update(torch.from_numpy(c['gravity_z'][i].copy()),root[:,7:10].norm(dim=-1),root[:,10:13].norm(dim=-1))
        assert np.array_equal(c['age_after'][i],phase.age.numpy()) and np.array_equal(c['request'][i],phase.request.numpy()),('clock_request',i)
        assert np.array_equal(c['credited_before_reset'][i],phase.credited.numpy()) and np.array_equal(c['stable_units_before_reset'][i],phase.stable.numpy()),('stable_credit',i)
        delta_error=max(delta_error,float(abs(phase.delta.numpy()-c['event_delta'][i]).max()));peak_error=max(peak_error,float(abs(phase.peak.numpy()-c['peak'][i]).max()));assert delta_error<=1e-6 and peak_error<=1e-6
        previous=c['executed6'][i].copy();reset=np.flatnonzero(c['done'][i]);previous[reset]=0;rid=torch.from_numpy(reset);phase.reset(rid,upright[rid])
    return dict(passed=True,controls=steps,all104_previous_actual6_and_mode_and_10ms_counter_increment2_and_selected_resets_exact=True,all104_source_stable_counter_and_credit_before_reset_literal_exact=True,event_maxabs=delta_error,upright_peak_maxabs=peak_error,independent_gravity_from_actual_quaternion_maxabs=gravity_error,full31_vs_wheel_contact_force_maxabs_N=force_error,control_root_vs_last_physical_callback_literal_exact=True,no_new_physical_or_skill_threshold=True)
