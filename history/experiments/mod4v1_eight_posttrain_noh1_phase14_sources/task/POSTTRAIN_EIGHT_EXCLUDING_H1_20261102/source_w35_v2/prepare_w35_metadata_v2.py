"""Create child-local SOURCE metadata only; no Task/GO/Ready or actual execution."""
from pathlib import Path
import ast,hashlib,json,sys
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B))
import w35_posttrain_source_builder_v2 as s

def put(name,value):
    with (B/name).open('x',encoding='utf-8')as f:json.dump(value,f,indent=2,ensure_ascii=False)
def main():
    s.create_derivation_from_installed_source(B)
    protocol=ast.parse((B/s.PROTOCOL).read_text(encoding='utf-8-sig'))
    worker=ast.parse((B/s.WORKER).read_text(encoding='utf-8-sig'))
    def fields(tree,var):
        return sorted({n.slice.value for n in ast.walk(tree) if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name)
            and n.value.id==var and isinstance(n.slice,ast.Constant) and isinstance(n.slice.value,str)})
    required=dict(status='SOURCE_ONLY_FIELDS_NOT_ADMISSION_OR_LIVE_READY',
        Task_required=sorted(set(fields(protocol,'task'))|set(fields(worker,'task'))),
        GO_required=sorted(set(fields(protocol,'go'))|set(fields(worker,'go'))),
        canonical_binding_required=['path','generation','owner_run_id','owner_parent_pid','one_original_writer'],
        parent_actual_populates=['run_id','role_key','GPU_UUID','owner_parent_pid','inherited_lock_fds','original_owner_pid',
            'root_admission_file','root_admission_SHA','manifest_file','manifest_SHA','canonical_binding','stop_file',
            'learning_started_epoch','save_deadline','nominal_end_epoch','source_CPU_SHA from parent-produced historical-Ready convention'],
        parent_stager_manifest=dict(kind=s.INSTALL_KIND,source_model_metadata_SHA=s.SHA,
            derivation_binding='manifest.files[] row for '+s.DERIVATION_FILE+' and Task.derivation_index_SHA; no nonexistent manifest.derivation_index_SHA'),
        exact_task_kind=s.KIND,exact_derivation_kind=s.DERIVATION_KIND,
        expected_new_Ready_kind=s.KIND,Ready_actual_writer='Original parent w35 branch only; no child Ready is emitted',
        source_read_purpose_parent_string='NEW_W35_FULL20K_POSTTRAIN20_<run_id>',
        independent_source_read_plan=dict(physical_byte_opens=1,decodes=1,source_bytes=s.BYTES),
        raw_iteration='No assignment to live runner iteration or saved iter; exact original saved value recorded independently of completed updates',
        actual_currenttraining_fullrestore_required=True,H1_excluded=True)
    put('W35_REQUIRED_PARENT_FIELDS_V2.json',required)
    task,go=s.build_source_templates(job_root=B,run_id='SOURCE_DRAFT_ONLY',role_key='w35_DRAFT_ONLY',manifest_SHA='0'*64)
    assert task['owner_parent_pid']==0 and go['learning_started_epoch']==0 and not task['inherited_lock_fds']
    put('W35_SOURCE_TASK_GO_DRAFT_EXAMPLE_V2.json',dict(status='MOCK_SOURCE_DRAFT_NOT_TASK_OR_GO_NOT_ADMISSION',
        actual_budget_owner_admitted=False,actual_new_live_SDK_restore=False,Task_file_published=False,GO_Ready_file_published=False,
        task_template=task,go_template=go))
    descriptor=dict(status='SOURCE_ONLY_NOT_ACTUAL_GO_OR_TRAINING_PASS',role='W35',H1_excluded=True,kind=s.KIND,
        source_model_metadata=s.SOURCE_METADATA,source_GPU_fullrestore_proof_SHA=s.GPU_CERT_SHA,
        install_kind=s.INSTALL_KIND,derivation_kind=s.DERIVATION_KIND,derivation_file=s.DERIVATION_FILE,
        runtime_root_base_remote='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000',
        required_runtime_uploads=[s.WORKER,s.PROTOCOL,'w35_posttrain_source_builder_v2.py',s.GPU_CERT_FILE,s.DESCRIPTOR],
        original_IDX_kept='MOD4V1_DERIVATION_INDEX.json',new_dedicated_IDX=s.DERIVATION_FILE,
        source_runtime_files=[s.source_row(B,n) for n in(s.WORKER,s.PROTOCOL,'w35_posttrain_source_builder_v2.py',s.GPU_CERT_FILE)],
        source_family='w35',parent_entry_fields=s.PARENT_ENTRY_FIELDS,
        final_receipt='production/FINAL.json',final_checkpoint='production/model_final_complete.pt',
        parent_builder_interface=['create_derivation_from_installed_source(dst)',
            'build_source_templates(*, job_root, run_id, role_key, manifest_SHA) -> (task_template, go_template)'],
        seed=20260928,steps_per_env=24,num_envs=20000,max_additional_updates=20,
        raw_original_iteration_not_synthesized=True,Adam20_steps_per_actual_update_assertion_only=True,
        original_save_knownlive_before_union=True,unknown_roots_preserved=True,whole_source_RAM_truth_checked=True,
        prior_window=82,prior_cumulative=162,source_declared_LR=s.LR,SDK_Torch_PPO_PT_C_GO_Git_operations=0,
        source_review_file='SOURCE_REVIEW_ERRORS_AND_FIXES_V2.json',test_report='W35_SOURCE_AST_MOCK_REVIEW_V2_FINAL.json')
    put(s.DESCRIPTOR,descriptor)
    print(json.dumps(dict(status='SOURCE_METADATA_PREPARED_NO_ACTUAL_READY',root=str(B),Task_GO_Ready_files=0),indent=2))
if __name__=='__main__':main()
