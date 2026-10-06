"""Pure approved-scope and learning-accounting contract; no filesystem mutation."""
import math
LEARNING_KINDS=frozenset({'ppo_preflight','expert_ppo','gate_ppo','gate_supervised','encoder_auxiliary','matched_baseline_ppo'})
def validate_approval(approval,document_sha,stage):
 if not approval.get('approved') or approval.get('approval_basis')!='explicit_human_message_in_current_chat':raise ValueError('Missing direct human approval')
 if approval['approved_plan_sha256']!=document_sha:raise ValueError('Approved document changed')
 if stage not in approval['allowed_stages']:raise ValueError('Stage not approved')
 return True
def authorized_total(b):
 seen=set();total=36000
 for e in b.get('budget_extensions',[]):
  i=e['extension_id']
  if i in seen or e.get('state')!='applied' or e.get('authorization_basis')!='explicit_user_request':raise ValueError('Invalid or duplicate authorization')
  n=e['additional_training_seconds']
  if type(n)!=int or n<=0:raise ValueError('Invalid addition')
  seen.add(i);total+=n
 if total!=b['authorized_training_seconds']:raise ValueError('Unregistered budget total')
 charged=float(b['charged_training_seconds'])
 if not math.isfinite(charged) or charged<0:raise ValueError('Invalid charged time')
 return total
def register_extension(b,approval,now):
 import copy
 authorized_total(b)
 if b.get('active_segment'):raise ValueError('Active segment must be reconciled by its owner')
 records=[e for e in b.get('budget_extensions',[]) if e['extension_id']==approval['pending_extension_id']]
 if records:
  if len(records)!=1 or records[0]['additional_training_seconds']!=approval['pending_extension_seconds']:raise ValueError('Existing addition does not match approval')
  return copy.deepcopy(b),False
 after=copy.deepcopy(b);amount=approval['pending_extension_seconds'];before=b['authorized_training_seconds']
 if before!=468000 or amount!=360000 or before+amount!=approval['authorized_budget_ceiling_seconds']:raise ValueError('Unexpected authorization boundary')
 after.setdefault('budget_extensions',[]).append({'extension_id':approval['pending_extension_id'],'additional_training_seconds':amount,
  'authorization_basis':'explicit_user_request','authorization':'Human explicitly authorized100h and approved MOD4-MOE-PLAN-001 v1.2 execution in this chat',
  'requested_epoch':approval['recorded_epoch'],'applied_epoch':now,'authorized_seconds_before':before,'authorized_seconds_after':before+amount,'state':'applied',
  'approved_plan_sha256':approval['approved_plan_sha256']})
 after['authorized_training_seconds']=before+amount
 after['remaining_training_seconds']=before+amount-float(b['charged_training_seconds'])
 authorized_total(after)
 return after,True
def learning_delta(kind,started,ended):
 if kind not in LEARNING_KINDS:raise ValueError('Not an approved charged-learning kind')
 if not all(math.isfinite(x) for x in [started,ended]) or ended<started:raise ValueError('Invalid interval')
 return ended-started
