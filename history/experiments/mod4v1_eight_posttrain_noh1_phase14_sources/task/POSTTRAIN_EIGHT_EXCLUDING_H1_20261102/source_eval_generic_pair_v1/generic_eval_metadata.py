"""Purestdlib eight-role/two-member frozen-eval metadata producer.
ConsumesactualtrainingFINALobjects; nofiles/model/SDK/resources/C/GO/Ready.
NoSTDpre-readforE0/E2/E3/W35: originaloneCPUcacheloadsactualsavedSTDstrict.
"""
import copy,math,re
ROLES=('E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50')
E1_ROLES=ROLES[4:]
# ExactV8actualprotocolcounts fromSINGLE_GPU_NINE_FINAL_SUMMARY_V1.json.
CONTROLS=dict(E0=1000,E2=1200,E3=160,W35=1600,CURB_PROTECTED878=750,CURB_INDEPENDENT113=750,SLOPE135=750,SLOPE_INDEPENDENT50=1000)
E1_WORKERS=dict(CURB_PROTECTED878='worker_curb878_n80.py',CURB_INDEPENDENT113='worker_curb113_n80.py',SLOPE135='worker_slope135_n80.py',SLOPE_INDEPENDENT50='worker_slope50_n80.py')
KIND='N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_NOT_FULL20K_RESUME'


def validate_roles(roles):
    assert isinstance(roles,(list,tuple)) and len(roles)==2 and len(set(roles))==2
    assert set(roles)<=set(ROLES),'ExactlytwooftheeightnonH1rolesrequired'
    return list(roles)


def _one_unique(steps):
    assert isinstance(steps,(list,tuple)) and steps
    assert all(type(x)in(int,float) and math.isfinite(x) and int(x)==x for x in steps)
    unique=sorted(set(int(x)for x in steps))
    if len(unique)!=1:raise ValueError('Originalfreshcacheexpectsuniform17Adam; donotflattennonuniformactualmetadata')
    return unique


def pin_from_training_final(role,final):
    """Exactknownproducer schemas, notoldsourcecounters orPPOarithmetic."""
    assert role in ROLES
    if role in E1_ROLES:
        r=final['new_fullstate_checkpoint'];m=r['live_core']
        assert r['atomic_final_published']is True and r['completed_actual_updates']==final['completed_actual_updates']
        assert len(m['Adam17_steps'])==17 and len(m['optimizer_LRs'])>=1 and m['iteration']==r['iteration']
        unique=_one_unique(m['Adam17_steps']);std=list(m['STD6']);assert len(std)==6 and all(type(x)in(int,float)and math.isfinite(x)for x in std)
        pin=dict(path=r['checkpoint'],bytes=r['bytes'],SHA=r['SHA'],iteration=m['iteration'],LR=m['optimizer_LRs'][0],Adam17_unique=unique,Adam17_steps=copy.deepcopy(m['Adam17_steps']),STD6=std,metadata_schema='E1_FINAL.new_fullstate_checkpoint.live_core',STD_metadata_available=True)
    else:
        r=final['final']
        if role=='W35':
            assert r['full_core_STD_optimizer_and_targetDR_saved']is True and r['Adam_min']==r['Adam_max']
            unique=_one_unique([r['Adam_min'],r['Adam_max']]);schema='W35_FINAL.final.Adam_min_max'
        else:
            # saved_17AdamisproducerUNIQUEsetlist,not17copies; donotclaimafull
            # 17elementlistfromit. OriginalCPUcachechecksactualoptimizerlen17.
            assert r['full_live_core_STD_optimizer_DR_history_RNG_queue_verified']is True
            unique=_one_unique(r['saved_17Adam']);schema='FORMAL_FINAL.final.saved_17Adam_unique'
        pin=dict(path=r['path'],bytes=r['bytes'],SHA=r['SHA'],iteration=r['saved_iteration'],LR=r['actual_saved_LR'],Adam17_unique=unique,metadata_schema=schema,STD_metadata_available=False,STD_source='OnlyoriginaladmittedwholeCPUcacheactualactorstate,nostandalonePTread')
    assert isinstance(pin['path'],str)and pin['path'] and type(pin['bytes'])is int and pin['bytes']>0
    assert re.fullmatch('[0-9a-f]{64}',pin['SHA']) and type(pin['iteration'])is int and pin['iteration']>=0
    assert type(pin['LR'])in(int,float) and math.isfinite(pin['LR'])
    return pin


def roster_row(role):
    assert role in ROLES
    steps=CONTROLS[role]
    return dict(role=role,family='e1'if role in E1_ROLES else'parent',worker=('worker_sources/e1/'+E1_WORKERS[role])if role in E1_ROLES else'worker_sources/parent/worker_five_original_n80.py',num_envs=80,seed=20260928,controls=steps,seconds=steps*.02,physics_callbacks=steps*8,feedback_samples=steps*2,policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],source20k_history_scope='WHOLE_CPU_CACHED_NOT_APPLIED_OR_SLICED',skill_scope='S50_DESCRIPTIVE_ACCEPTED_METRIC_GAP'if role=='SLOPE_INDEPENDENT50'else'ORIGINAL_OWN_PROTOCOL_UNCHANGED')


def build_eval_metadata(roles,actualtrainingfinalbyrole,baseline_contracts,*,baseline_roster=None,provenance=None):
    """Metadata/planpatchesonly; noactualTask/ROOT/Ready/GO/orresourcewait.
    Parentinjectsactualcase/runtime/asset/GPU/fds/deadline/admissionafterfresh
    originalresourcegate. NeverreuseoldtrainingGOoroldfiniteSH/waitonce.
    """
    members=validate_roles(roles);assert all(r in actualtrainingfinalbyrole for r in members)
    contracts=copy.deepcopy(baseline_contracts);pins={r:pin_from_training_final(r,actualtrainingfinalbyrole[r])for r in members};patches={};rows=[]
    for role in members:
        p=pins[role]
        patch=dict(role=role,source_path=p['path'],source_SHA=p['SHA'],source_bytes=p['bytes'],source_iteration=p['iteration'],source_Adam17=p['Adam17_unique'][0],source_LR=p['LR'],eval_members=members[:],kind=KIND,purpose=KIND,optimizer_updates=0,saved20k_DR_physically_applied=False,state_projection_or_slicing=False,whole20k_savedrestore_claim=False)
        if role in E1_ROLES:
            assert role in contracts,'OwnrolebaselineROLE_CONTRACTrequired'
            c=contracts[role];baseline=dict(source=copy.deepcopy(c['source']),core=copy.deepcopy(c['core']))
            c['source']={k:p[k]for k in('path','bytes','SHA')}
            c['core']=dict(original_iteration=p['iteration'],original_17Adam_step=p['Adam17_unique'][0],original_LR=p['LR'],original_STD6=copy.deepcopy(p['STD6']))
            c['historical_baseline_source_contract']=baseline;c['candidate_metadata_provenance']=copy.deepcopy(provenance);patch['source_STD6']=copy.deepcopy(p['STD6'])
        # FormalfamilieshaveNOpretendedSTD6field. Actorstrictloadsfromsamewholecache.
        patches[role]=patch
        row=copy.deepcopy(baseline_roster[role])if baseline_roster is not None else{}
        if role not in E1_ROLES:
            stale={k:row.pop(k)for k in ('source_STD6','original_STD6','expected_STD6','STD6')if k in row}
            if stale:row['historical_baseline_STD_metadata_not_candidate']=stale
            if 'core'in row:row['historical_baseline_core_metadata_not_candidate']=row.pop('core')
        row.update(roster_row(role));row.update(patch);rows.append(row)
    return dict(kind='TWO_MEMBER_FROZEN_EVAL_SOURCE_METADATA_ONLY_NOT_READY',eval_members=members,roles=rows,source_pins=pins,task_source_patches=patches,ROLE_CONTRACTS=contracts,baseline_original_protocols={r:roster_row(r)for r in members},actualTask_Ready_GO_or_resources_created=False,old_sources_changed=False,model_byte_stat_hash_read_SDK_SSH_GPU_C_Git=0,eval_updates=0,no_new_physical_or_skill_predicates=True,all20k_unknown_root_histories_cached_whole_no_slice_apply=True)
