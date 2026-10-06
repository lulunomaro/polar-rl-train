"""Pure authority contract for the human-approved parallel A0 branch."""
import math
SOURCE_SHA='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'
def validate(a,document_sha,b,source,cpu):
 if not a.get('approved') or a.get('approval_basis')!='explicit_human_message_in_current_chat':raise ValueError('Missing human approval')
 if a.get('version')!='1.3' or a['approved_plan_sha256']!=document_sha:raise ValueError('Plan revision mismatch')
 if not all(s in a['allowed_stages'] for s in ['S1','S1A']):raise ValueError('Stages not authorized')
 if not a.get('revision_basis',{}).get('no_new_DR_task_interface_physics_hardware_reset_scope'):raise ValueError('Missing parallel correction')
 if b.get('active_segment'):raise ValueError('Previous active segment must be reconciled by its owner')
 if b['authorized_training_seconds']!=828000 or b['remaining_training_seconds']<=120:raise ValueError('Budget unavailable')
 if not math.isfinite(b['charged_training_seconds']):raise ValueError('Nonfinite ledger')
 if source.get('sha256')!=SOURCE_SHA or source.get('iteration_stored')!=23509 or source.get('finite_tensors')!=68:raise ValueError('Unvalidated source')
 if not cpu.get('pass_'):raise ValueError('Missing expert isolation/interface contract')
 return True
