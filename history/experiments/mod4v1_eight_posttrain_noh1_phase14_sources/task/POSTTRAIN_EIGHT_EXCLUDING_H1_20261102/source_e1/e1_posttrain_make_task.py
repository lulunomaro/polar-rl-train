"""Pure taskassemblerforparent use; consumesACTUALparentadmission/GO objects.
ItdoesNOTproduceadmission/GO/ledger,readmodels/canonical,acquirelocksorlaunchSDK.
ParentW35originalownerstructure/account=charge_values remainssoleauthority.
"""
import copy
from e1_posttrain_contract import require_source_admission,REQUIRED_TASK_KEYS

PARENT_INJECT_KEYS=('run_id','role_key','GPU_UUID','canonical_path','owner_parent_pid','inherited_lock_fds','root_admission_file','root_admission_SHA','go_file','rescue_stop_file','asset_dir','source_read_purpose')
SOURCE_PIN_KEYS=('path','SHA','bytes','iteration','Adam17','LR','original_source_SHA')


def make_task(descriptor,parent_fields,actual_admission,actual_go,*,source_pin=None,now,environ,fd_check):
    """ReturnsnewTaskdict onlyafterparentactualobjectsareconsistent.
    Noactualauthorityiscreatedbycallingthisfunction; parentmustcreateitsROOT/GO
    underoriginalbudget+EX/SHfirstandprovidefd_check=os.fstat. SourceMOCKmustlabel
    itsfixturesandpassastubchecker; thatisNOTactualadmission.
    """
    assert all(k in parent_fields for k in PARENT_INJECT_KEYS)
    result=copy.deepcopy(descriptor)
    result.update({k:copy.deepcopy(parent_fields[k]) for k in PARENT_INJECT_KEYS})
    for k in ('additional_updates','save_interval','seed','exit_headroom_seconds','max_parent_seconds'):
        if k in parent_fields:result[k]=parent_fields[k]
    if source_pin is not None:
        assert all(k in source_pin for k in SOURCE_PIN_KEYS)
        result.update(selected_typed_source_path=source_pin['path'],model_path=source_pin['path'],source_SHA=source_pin['SHA'],source_bytes=source_pin['bytes'],source_iteration=source_pin['iteration'],source_Adam_step=source_pin['Adam17'],source_Adam17=source_pin['Adam17'],source_LR=source_pin['LR'],original_source_SHA=source_pin['original_source_SHA'])
    assert not [k for k in REQUIRED_TASK_KEYS if k not in result]
    require_source_admission(result,actual_admission,actual_go,now=now,environ=environ,fd_check=fd_check)
    result['sourceonly_NOT_READY']=False
    result.pop('no_actual_admission_or_GO_created',None)
    result['taskassembler_created_no_admission_or_GO']=True
    result['actual_admission_and_GO_created_by_original_parent_only']=True
    return result
