"""SOURCE-ONLY thin compatibility shim; keep every V4 installer/resume API.

Place beside the unchanged V4/V3/V2 dependencies in a future manifest-owned
worker_sources directory. Importing this module imports no SDK/Torch and opens
no checkpoint. V5 only overrides close witness/gate and bounds pose receipts.
"""
from resume_runtime_install_hook_v4 import (
    FINAL_KIND, LIFECYCLE_KIND, BASELINE_ACTOR_VIEW, RAW35_ACTOR_VIEW,
    validate_worker_variant, PinnedOwnFullCheckpoint,
    load_decoded_full_checkpoint_once, resolve_future_bridge_adapter,
    preserve_worker_error, require, bind_future_task_extensions,
    validate_pose_cache_installer_descriptor, install_optional_pose_cache_runtime_adapter,
)
from app_close_semantics_v5 import (
    close_original_resources, evaluate_waited_worker,
    BoundedPoseCacheEventsV5, force_pose_cache_event_receipt_v5,
)
