"""Fullstate save/identity utilities. Torch injected onlyafterparentactualadmission.
No trainingalgo/DR/physics/authority implementation, no PT I/O atmoduleimport.
"""
from pathlib import Path
import copy,hashlib,json,time

def preserve_unknown(original,current):
    # Currentknownleaf wins. Preservecontainerandallmissingoriginaldictkeys.
    if isinstance(original,dict) and isinstance(current,dict):
        result=copy.copy(current)
        for k,old in original.items():
            result[k]=preserve_unknown(old,current[k]) if k in current else copy.deepcopy(old)
        return result
    if isinstance(original,(list,tuple)) and type(original)==type(current) and len(original)==len(current):
        values=[preserve_unknown(a,b) for a,b in zip(original,current)]
        return tuple(values) if isinstance(current,tuple) else values
    return current


def exact_tree(t,a,b):
    if a is b:return True
    if t.is_tensor(a):return t.is_tensor(b) and a.dtype==b.dtype and tuple(a.shape)==tuple(b.shape) and t.equal(a.detach().cpu(),b.detach().cpu())
    if isinstance(a,dict):return isinstance(b,dict) and list(a)==list(b) and all(exact_tree(t,a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a)==type(b) and len(a)==len(b) and all(exact_tree(t,x,y) for x,y in zip(a,b))
    if hasattr(a,'dtype') and hasattr(a,'shape'):
        import numpy as np
        return type(a)==type(b) and a.dtype==b.dtype and a.shape==b.shape and np.array_equal(a,b)
    return type(a)==type(b) and a==b


def keys_preserved(old,new,path=''):
    if not isinstance(old,dict):return []
    if not isinstance(new,dict):return [path+' TYPE_CHANGED']
    missing=[]
    for k,v in old.items():
        p=path+'/'+str(k)
        if k not in new:missing.append(p)
        elif isinstance(v,dict):missing+=keys_preserved(v,new[k],p)
    return missing


def live_core(t,runner):
    state=runner.alg.optimizer.state_dict();assert len(state['state'])==17
    steps=[int(v['step'].detach().cpu().item()) if t.is_tensor(v['step']) else int(v['step']) for v in state['state'].values()]
    return dict(iteration=int(runner.current_learning_iteration),actual_alg_LR=float(runner.alg.learning_rate),optimizer_LRs=[float(g['lr']) for g in state['param_groups']],Adam17_steps=steps,STD6=runner.alg.actor.state_dict()['distribution.std_param'].detach().cpu().tolist(),actor_tensors=len(runner.alg.actor.state_dict()),critic_tensors=len(runner.alg.critic.state_dict()))


def validate_save_core(t,ck,runner,source):
    assert not keys_preserved(source,ck),'Missingoriginalroot/nestedkeys'
    assert exact_tree(t,ck['actor_state_dict'],runner.alg.actor.state_dict())
    assert exact_tree(t,ck['critic_state_dict'],runner.alg.critic.state_dict())
    assert exact_tree(t,ck['optimizer_state_dict'],runner.alg.optimizer.state_dict())
    assert int(ck['iter'])==int(runner.current_learning_iteration)
    assert len(ck['optimizer_state_dict']['state'])==17
    assert ck['independent_terrain_expert'] in ('E1_CURB','E1_SLOPE')
    assert ck['spring_pressure_state']['n']==20000 and ck['physical_action_delay_state']['n']==20000
    assert ck['physical_action_delay_state']['physics_us']==2500 and ck['physical_action_delay_state']['control_us']==20000
    assert ck['spring_pressure_recipe']['nominal_stiffness_N_m']==2000
    assert ck['feedback_delay_recipe']['control_period_us']==10000
    return True


def install_complete_unknown_merge(runner,env,cache,t,output_root):
    """InstallAFTERownD0-D7/E1savecontract,BEFOREoriginalatomicrescue wrapper."""
    old=runner.save;out=Path(output_root).resolve();records=[]
    def save(path,*a,**kw):
        p=Path(path).resolve();assert not cache.owns(p) and p.is_relative_to(out)
        old(str(p),*a,**kw)
        ck=cache.load(str(p),map_location='cpu',weights_only=False,purpose='posttrain.OWN_COMPLETE_FULL_D0_D7_SAVE_BEFORE_UNKNOWN_MERGE')
        merged=preserve_unknown(cache.state,ck);validate_save_core(t,merged,runner,cache.state)
        t.save(merged,str(p));real=cache.load(str(p),map_location='cpu',weights_only=False,purpose='posttrain.OWN_COMPLETE_SAVE_ACTUAL_ROUNDTRIP')
        assert exact_tree(t,real,merged);validate_save_core(t,real,runner,cache.state)
        records.append(dict(epoch=time.time(),physical_write_path=str(p),fully_validated_before_atomic_publication=True,original_key_count=len(cache.state),new_key_count=len(real),no_missing_original_keys=True,all_original_D0_D7_E1_saveowners_retained=True,live_core=live_core(t,runner),selected_source_not_overwritten=True))
    runner.save=save
    return records


def install_published_save_receipts(runner,env,cache,t,out,records,SavedStop,put,completed):
    """InstallAFTERrescue_training.install; recordsfinalfileafteratomicrename.
    Snapshotrecord isnotGO/canonical orskillqualification.
    """
    atomic=runner.save;published=[];folder=Path(out)
    def save(path,*a,**kw):
        stopped=None;before=len(records)
        try:value=atomic(path,*a,**kw)
        except SavedStop as e:stopped=e;value=None
        assert len(records)==before+1
        p=Path(path).resolve();assert not cache.owns(p) and p.is_relative_to(folder.resolve())
        with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        receipt=dict(records[-1],checkpoint=str(p),SHA=digest,bytes=p.stat().st_size,completed_actual_updates=completed[0],atomic_final_published=True,iteration=int(runner.current_learning_iteration),source_SHA=cache.SHA,source_new_20k_history_saved=True,source_slicing_or_retyping=False,selected_source_byte_reads=cache.physical_byte_reads,selected_source_SHA_calculations=cache.source_SHA_calculations,selected_source_decodes=cache.source_decodes,original_fullhelper_receipts=[x.name for x in folder.glob('*STARTUP_VERIFIED.json')],skill_evaluation_required_before_best_selection=True,skill_graduation=False,canonical_accounting='OriginalparentonlythroughfullsaveSDKclosechildwaitterminal')
        published.append(receipt);put('COMPLETE_CHECKPOINT_RECEIPT_'+str(len(published)).zfill(4)+'.json',receipt)
        if stopped is not None:raise stopped
        return value
    runner.save=save
    return published
