"""Named NumPy provider boundary for a non-rejected own reference proposal."""
import numpy as np

def to_named_tables(reference,joint_names):
    if reference is None:raise ValueError('Rejected conversion has no own step reference tables')
    names=tuple(joint_names)
    if len(names)!=30 or len(set(names))!=30:raise ValueError('30 unique actual own joint names required')
    ages=np.asarray(reference.ages);states=np.asarray(reference.states);mask=np.asarray(reference.masks)
    if ages.ndim!=1 or states.shape!=(len(ages),73) or mask.shape!=states.shape:raise ValueError('table layout mismatch')
    if not np.isfinite(states).all() or not np.array_equal(np.diff(ages),np.ones(len(ages)-1)):raise ValueError('finite contiguous control table required')
    metadata=dict(reference.metadata)
    metadata['phase_contract']=dict(control_dt_s=.01,public_request_age_start=100,public_request_age_end_exclusive=180,
        physical_command_vx_m_s=.8,own_target_reference_not_action=True,source_contacts_not_own_contacts=True,
        platform_height_m=.27,edge_x_m=.35,dynamic_feasibility='pending',actual_contact_and_success='not_tested')
    return dict(ages=ages.copy(),control_dt_s=.01,packed73=states.copy(),mask73=mask.astype(bool,copy=True),
                phase=np.asarray(reference.phases).copy(),joint_names=names,metadata=metadata)

def query_numpy(tables,ages,*,future=10):
    ages=np.asarray(ages)
    if not isinstance(future,int) or future<1:raise ValueError('positive integer future window required')
    wanted=ages[...,None]+np.arange(future)
    if not np.isfinite(wanted).all() or not np.equal(wanted,wanted.round()).all():raise ValueError('integer control ages required')
    index=wanted.astype(np.int64)-int(tables['ages'][0])
    if (index<0).any() or (index>=len(tables['ages'])).any():raise ValueError('future query outside explicit clip')
    state=tables['packed73'][index];mask=tables['mask73'][index]
    return dict(packed73=state,mask73=mask,goal=state*mask,phase=tables['phase'][index])
