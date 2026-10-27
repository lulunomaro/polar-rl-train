"""Final controller-folder checkpoint only; stop source work after this freeze."""
from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 index=HERE/'FINAL_FULL_CONTROLLER_SOURCE_INDEX_ACTUAL.json';assert not index.exists()
 handoff=HERE/'FINAL_E0_CONTROLLER_SOURCE_HANDOFF.md'
 handoff.write_text('''# E0 controller source handoff, current source work stopped

Root reports actual234 launched and returned in5.3s with one original72 owner and one E0 node. Run id E0_PPO50_GAS400_SINGLE72_1793099855286966300. Owner PID542939/create1793099859.6; node PID542948/create1793099859.94. Fresh selectedc27 had zero compute rows, original private/shared locks and loopback were admitted, and Task source54f/workerV4 8774/currentsourceCPU5509 were installed and typed READY passed. These are root-owned actual receipts, not a new observation by this subagent. Root is performing one finite first-metadata snapshot. This handoff does not claim a seen GO, actual CUDA restore, first PPO update, final checkpoint, settled fee or skill qualification.

The frozen executable package is V2_LR/E0_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json SHA cfee5558e2a4311c1caf159f47c1213fe146a67c718e82f8220f1a0b0a7cceb0. V2_LR frozen source index SHA eb6365b1f5be3500256d9c84e2b609ffbfc3a27b11045ef0a90406975e33cf74. Current worker is the additive E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py SHA87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19. It changes only the CLI constructor LR literal to the original.00038443359375000017, preserving the frozen V3 bytes under inverse replacement. Actual233 source-only migration SHA5509f4a793be9d9e5e858bc75bfa326440267f1caeff040979935b2bed6f3c8e embeds the entire actual89C fullstate CPU witness d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c unchanged. No repeated PT/normalizer load was performed for LR migration/controller preparation.

Owner/common/node/authority/resource/launcher preserve the original accounting and finite lifecycle. The sole originalC72 writer owns GO→load/train/save/SDKclose/childwait/terminal-receipt sum-once, unchanged two canonical locks, strict remaining>86412.86069250107,3900/3600save/300exit and original reserves/history. No second or fake slot, budget copy, refund, rounding, clamp, idle fee, clear-active, hotpatch, cleanup or other process intervention occurred here. The runtime HMAC token is generated in launcher memory and passed only through stdin; it is absent from cfg/TASK/reports/argv/Git.

Known source/fixture failures remain with sources and reports: V1 added16GiB disk and22000MiB/5percent worker thresholds were rejected before GO and minimally repaired through V2/V3; CPU readerV1 attempted CUDA16byte→CPU5056byte RNG restore and failed before GPU/GO; V2 honest structural-only admission passed actual89C. Original CUDA bytes stayed unchanged and real worker CUDA restore remains necessary. Later root identified PPO internal learning_rate was not synchronized by optimizer load; V3 was rejected before GO and V4 fixes the constructor literal. Controller fixture spy/locator/import and shell-quote errors are preserved, including the explicitly acknowledged overwritten temporary diagnostic file; they are not robot/PPO failures. Whole old night_frozen_experts directory was frozen with512-file checkpoint and root reports Git81fea08/full capture. This controller tree is an ordinary supplement of the existing89 trial, never another record/tag.

Actual job root is /home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c/e0; controller roots are sibling owner and node_e0. First-metadata observer is V2_LR/E0_first_metadata_observer_readonly_v1.py. Progress files: adaptation/SOURCE_FULLRESTORE_ZERO_VERIFIED.json, CLOCK_GAS400_NATIVE24_ACTUAL.json, PPO_POSITIVE_CURRENT.json, latest_complete.json. Close files: adaptation/FINAL.json and APP_CLOSED.json; node_e0/NODE_TERMINAL_ACTUAL.json and NODE_EXIT_ACTUAL.json; owner/COHORT_FINAL.json and OWNER_EXIT_ACTUAL.json. Only root's original owner and actual canonical closure read settle cost. Do not relaunch, clear canonical, or hotpatch because a status is pending.

No WM transition tap runs in this worker. A PPO checkpoint is not a WM transition dataset. Planned read-only collection must separately preserve state-before, actual clipped ingress and physics-applied queues, real xi/DR/domain, terminal-before-autoreset, episode/done and50Hz clocks. W35 resetV2 candidate remains separately frozen/pending; its original nearest.25 selection is pose34/rootheight.252 with original all30q/full collider points, not the flat74 assumption. W35 and remaining experts are not adapted or qualified by E0 preparation.

All controller sources, failed fixtures, reports and handoffs in the complete index are now immutable. This subagent holds no remote lease, has launched no GPU job itself, and stops current source work. No new GPU task is authorized to this subagent at this point. Root owns actual launch, first update, final validation and ordinary Git supplementation.
''',encoding='utf8')
 files=[]
 for path in sorted(ROOT.rglob('*')):
  if not path.is_file() or path==index:continue
  assert path.suffix.lower() not in ('.pt','.onnx','.npz','.npy','.usd','.usda','.usdc','.zip'),'no model/binary read allowed in this metadata freeze'
  files.append(dict(path=str(path),relative=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,SHA=H(path),immutable=True))
 value=dict(schema='mod4.E0.single72.controller.final_full_source_index.v1',epoch=time.time(),frozen_all_current_files=True,
  files=files,source_work_stopped=True,source_model_normalizer_binary_not_read=True,
  parent_actual234_launch=dict(run_id='E0_PPO50_GAS400_SINGLE72_1793099855286966300',owner_pid=542939,owner_creation=1793099859.6,node_pid=542948,node_creation=1793099859.94),
  actual_first_GO_CUDA_PPO_or_final_seen_by_this_subagent=False,subagent_remote_lease_held=False,
  root_owns_actual_start_firstupdate_close_and_Git=True,Git_status='ordinary_supplement_existing89trial_no_record_or_new_tag')
 index.write_text(json.dumps(value,indent=2),encoding='utf8')
 print(json.dumps(dict(index=str(index),SHA=H(index),files=len(files),source_work_stopped=True)))
if __name__=='__main__':main()
