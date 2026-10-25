# Prospective no-go decisions and empty result templates

These are **new research-stage** decisions only. They do not stop current H1/E3 training, alter the existing approved physical success criterion or impose extra FP64/bitwise/1µm health gates. Existing2.5ms/TGS32/4, H1×4/E3×8, per-environment2mm closure reset and original finite/integrity/hardware/save protections retain their approved scope.

## Stage decisions

| Check | No-go / valid interpretation | Next permitted preparation action |
|---|---|---|
| current H1 not complete / process still owns GPU | no T2-z train/collection launch | root can finish source/protocol/archive preparation; actual process/save receipt governs release |
| real native RGB absent | `DATASET_MISSING`, no visual task fine-tuning | retain rejection; prepare collector/manifest without pretending existing reconstructed clips are training data |
| applied-target/time/reset/group receipts absent | `DATA_NOT_CERTIFIED`; no claim of lossless actual-action training | preserve original data/reader error, fix exporter against retained evidence; approximate dataset gets a new schema and explicit label |
| no independent held-out physical groups or disjoint source episodes | `IDENTIFICATION_NOT_EVALUABLE` | keep descriptive fit results; do not randomly split frames or relabel same trajectory independent |
| query/factor labels reach adaptation | `INVALID_LEAKAGE` | preserve contaminated attempt; correct interface and use an untouched test set under a new version, not quietly reuse compromised test scores |
| candidate uses future hidden apply receipt | `PRIVILEGED_ACTION_INPUT` | label offline conditional prediction; redesign command-conditioned candidates before deployment claims |
| new H1 action loader/checkpoint/Wan alignment not checked | `INTEGRATION_PENDING` | complete engineering smoke audit under separately approved compute; CPU module tests are insufficient |
| model cannot fit declared per-device VRAM / time cap | `RESOURCE_NO_GO` or `TIMEOUT` | log exact attempted config and costs; a new reduced/offloaded design is a new explicitly approved comparison version, not silent unlimited retries |
| no validated visual physical observer | `PHYSICAL_METRIC_NOT_EVALUABLE` | report only valid visual endpoints, observer failures and limits; no actual-contact benefit claim |
| query error fails prospective benefit criterion | `NO_EVIDENCE_FOR_NEXT_STAGE` | retain all seeds/failures; state/identifiability diagnostics can explain, not rescue primary success posthoc |
| contact benefit only in generated frames | `NO_PHYSICAL_SUCCESS_EVIDENCE` | actual candidate execution remains unrun; no graduation or sim-to-real claim |
| model nonfinite / timeout / native unknown termination | model or evaluation failure, counted and retained | follow original stage protections; do not hide failed candidates/groups in an “effective” denominator |

Proposed next-stage research criterion, to be frozen before test access: primary group-averaged query trajectory error decreases by at least10% relative to the matched standard visual model, the paired95% group-CI supports positive improvement, and all three seed effects have the same direction. If a contact proxy observer is valid, its false-positive rate must not worsen under the preregistered comparison; publish its uncertainty rather than treating a small sample's zero events as proof. These are proposed research utility criteria, not human-approved mechanics/training health thresholds. A failure can still be reported faithfully and does not authorize changing the criterion or extending budget.

The10% criterion is undefined if standard-model error is effectively zero; in that case report absolute differences and declare the planned relative utility decision not evaluable. Thresholds/observer missingness tolerances, exact GPU-hour caps and per-device memory cap remain pending actual root approval. Do not infer unlimited compute because this document gives no number. H1 graduation still requires actual double-wheel270mm contact/recovery regardless of this criterion.

## Tables to fill only after actual runs

Every blank measurement is `NA/NOT_RUN`, never zero. Record actual denominator, exclusions and failed attempts. `result_template.json` contains null-valued machine-readable rows. Keep old failed rows immutable; append repaired attempts with distinct IDs and source/checkpoint hashes.

| Method | Train groups/episodes | Test groups/query episodes | K/S | Physical trajectory error | Contact proxy FP/miss | Actual H1 success | GPU-h / peak VRAM | Status |
|---|---|---|---|---|---|---|---|---|
| VIS_STANDARD_H1 | NA | NA | 0/0 | NA | NA | NA | NA | NOT_RUN |
| VIS_T2Z_H1 | NA | NA | 1/40 | NA | NA | NA | NA | NOT_RUN |
| VIS_T2Z_H1_S0 | NA | NA | 0/0 | NA | NA | NA | NA | NOT_RUN |
| VIS_HISTORY_H1 | NA | NA | 1/0 | NA | NA | NA | NA | NOT_RUN |
| VIS_LORA_TTA_H1 | NA | NA | 1/pending-val | NA | NA | NA | NA | NOT_RUN_OPTIONAL |
| STATE_LATENT_INSPIRED | NA | NA | 1/40 | NA state-only | NA state-only | NA | NA | NOT_RUN_SEPARATE_MODALITY |

Detailed per-query long table columns:

```text
trial_id,protocol_sha,code_sha,model_checkpoint_sha,data_index_sha,split_sha,method,model_seed,physical_group_id,source_support_episode_ids,source_query_episode_id,K,S,z_init_seed,z_before_sha,z_after_sha,shared_weights_before_sha,shared_weights_after_sha,query_initial_tick,query_horizon_s,prediction_status,observer_status,wheel_edge_error,contact_proxy_fp,contact_proxy_miss,native_actual_success,native_termination,adapt_s,query_s,load_s,decode_s,vae_s,peak_allocated_bytes,peak_reserved_bytes,exclusion_reason,evidence_paths
```

Resource/failure table columns:

```text
attempt_id,method,source_sha,config_sha,parent_attempt_id,actual_host,actual_gpu_model,devices,per_device_vram_bytes,precision,T,H,W,action_adapter_sha,parallelism,offload,checkpointing,optimizer,trainable_params,update_count,data_exposure,elapsed_s,gpu_hours,peak_cpu_ram_bytes,peak_disk_bytes,status,raw_error_path,resolution_attempt_id
```

Paper claim checklist after results: direct visual transfer versus state-inspired model named correctly; own contribution distinguished from T2-z; true target data source documented; hidden-factor/test-query leakage ruled out in actual loader; all model/data/compute counts given; physical success comes from execution evidence; negative results/failures included; simulator-only limitations explicit; no unmeasured4090/H200 speed extrapolation; no PPO throughput or graduation claim from video similarity.
