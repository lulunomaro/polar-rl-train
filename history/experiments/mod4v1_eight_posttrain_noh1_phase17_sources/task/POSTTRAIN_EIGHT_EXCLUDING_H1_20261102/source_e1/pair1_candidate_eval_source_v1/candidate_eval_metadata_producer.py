"""Puremetadata formatterforNEWunusedpair1eval, neverreads/stat/hashesPT.
Consumesactualfullsaveproducer pins suppliedbyparentafterfullsave/close/wait.
NoGO/admission/SDK/physical/skillpredicate creation. OriginalV8sourcesunchanged.
"""
import copy,math,re
MEMBERS=['E0','CURB_PROTECTED878']
KIND='N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_NOT_FULL20K_RESUME'
PIN_KEYS=('path','bytes','SHA','iteration','LR','Adam17_steps','STD6')


def normalize_actual_pin(pin):
    assert all(k in pin for k in PIN_KEYS),'Parentactualfullsaveproducerpinrequired'
    assert isinstance(pin['path'],str) and pin['path']
    assert type(pin['bytes']) is int and pin['bytes']>0
    assert re.fullmatch('[0-9a-f]{64}',pin['SHA'])
    assert type(pin['iteration']) is int and pin['iteration']>=0
    assert isinstance(pin['LR'],(int,float)) and math.isfinite(pin['LR'])
    steps=pin['Adam17_steps'];assert len(steps)==17 and all(isinstance(x,(int,float)) and math.isfinite(x) and int(x)==x for x in steps)
    if len(set(steps))!=1:raise ValueError('ExistingV8cacheexpectsuniform17Adam; neverflattenactualnonuniformstepsormakethisaskillfailure')
    std=pin['STD6'];assert len(std)==6 and all(isinstance(x,(int,float)) and math.isfinite(x) for x in std)
    # Exactsavedoptimizerfirst-groupLR, notalgLRheuristic; no +20n extrapolation.
    return copy.deepcopy(dict(path=pin['path'],bytes=pin['bytes'],SHA=pin['SHA'],iteration=pin['iteration'],LR=float(pin['LR']),Adam17_steps=[int(x)for x in steps],STD6=list(std)))


def actual_pin_from_e1_final(final):
    """ForourE1fullstateFINALschemaonly; E0parentformatsitsactualproducerpin.
    Thisfunctiononlyconsumesdecodedmetadata,itdoesnotopenafinalorcheckpoint.
    """
    r=final['new_fullstate_checkpoint'];m=r['live_core']
    assert r['atomic_final_published'] is True
    assert final['completed_actual_updates']==r['completed_actual_updates']
    assert m['iteration']==r['iteration'] and len(m['optimizer_LRs'])>=1
    return normalize_actual_pin(dict(path=r['checkpoint'],bytes=r['bytes'],SHA=r['SHA'],iteration=m['iteration'],LR=m['optimizer_LRs'][0],Adam17_steps=m['Adam17_steps'],STD6=m['STD6']))


def candidate_role_contracts(old_contracts,curb_actual_pin,*,provenance):
    pin=normalize_actual_pin(curb_actual_pin);contracts=copy.deepcopy(old_contracts);c=contracts['CURB_PROTECTED878'];baseline=dict(source=copy.deepcopy(c['source']),core=copy.deepcopy(c['core']))
    c['source']={k:pin[k]for k in ('path','bytes','SHA')}
    # Onlythese4areactualexpectedmetadatausedbyV8cache. OldRNGbytehash/rootkeys
    # remainhistoricalprovenance, neverclaimtheydescribeupdatedcandidatehistory.
    c['core']=dict(original_iteration=pin['iteration'],original_LR=pin['LR'],original_17Adam_step=pin['Adam17_steps'][0],original_STD6=pin['STD6'])
    c['historical_baseline_source_contract']=baseline
    c['candidate_metadata_provenance']=copy.deepcopy(provenance)
    c['source_scope']='NEW_FULL20K_PPO_CANDIDATE_WHOLE_CPU_CACHE_ACTORONLY_FRESH80_EVAL_NOT20KRESTORE'
    return contracts


def candidate_task_source_patch(role,pin):
    assert role in MEMBERS
    pin=normalize_actual_pin(pin)
    return dict(source_path=pin['path'],source_SHA=pin['SHA'],source_bytes=pin['bytes'],source_iteration=pin['iteration'],source_Adam17=pin['Adam17_steps'][0],source_LR=pin['LR'],source_STD6=pin['STD6'],eval_members=MEMBERS[:],kind=KIND,purpose=KIND,saved20k_DR_physically_applied=False,state_projection_or_slicing=False,whole20k_savedrestore_claim=False,optimizer_updates=0)


def make_pair1_metadata(old_contracts,actual_pins,*,provenance):
    """Returnscontract+sourcepatchesNOTwholeTasks/GO/Ready.
    ParentmustkeepV8factory/seed/cohort/clocksandinjectfreshresources/deadline/
    case/runtime/actual_group_admission; neverreusetheoldV8leasesortrainingGO.
    """
    assert set(actual_pins)==set(MEMBERS)
    pins={role:normalize_actual_pin(actual_pins[role])for role in MEMBERS}
    return dict(kind='PAIR1_CANDIDATE_EVAL_METADATA_ONLY_NOT_READY',members=MEMBERS[:],ROLE_CONTRACTS=candidate_role_contracts(old_contracts,pins['CURB_PROTECTED878'],provenance=provenance),task_source_patches={role:candidate_task_source_patch(role,pins[role])for role in MEMBERS},unchanged_protocol={'CURB_PROTECTED878':dict(seed=20260928,num_envs=80,controls=750,seconds=15.,physics_callbacks=6000,feedback_samples=1500),'E0':dict(seed=20260928,num_envs=80,controls=1000,seconds=20.,physics_callbacks=8000,feedback_samples=2000)},actual_admission_or_GO_or_Ready_created=False,no_source_PT_open_stat_hash=True,new_unused_copy_required=True)
