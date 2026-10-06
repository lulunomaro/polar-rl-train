"""Meaningful refusal/idempotency tests for the approved budget boundary."""
import copy,json,unittest
from pathlib import Path
from plan_budget_contract import register_extension,validate_approval,learning_delta,authorized_total
class BudgetContract(unittest.TestCase):
 def setUp(self):
  r=Path(__file__).parent/'reports'
  self.b=json.loads((r/'STAGE_S0_ACTUAL_BEFORE.json').read_text(encoding='utf8'))['budget']
  self.a=json.loads((r/'PLAN_APPROVAL.json').read_text(encoding='utf8'))
 def test_add_once_preserves_all_old_evidence(self):
  after,added=register_extension(self.b,self.a,1.)
  self.assertTrue(added);self.assertEqual(after['authorized_training_seconds'],828000)
  self.assertEqual(after['charged_training_seconds'],self.b['charged_training_seconds'])
  for key in set(self.b)-{'authorized_training_seconds','remaining_training_seconds','budget_extensions'}:self.assertEqual(after[key],self.b[key])
  again,added=register_extension(after,self.a,2.);self.assertFalse(added);self.assertEqual(after,again)
 def test_active_refused(self):
  b=copy.deepcopy(self.b);b['active_segment']={'pid':1}
  with self.assertRaises(ValueError):register_extension(b,self.a,1.)
 def test_duplicate_refused(self):
  b=copy.deepcopy(self.b);b['budget_extensions'].append(copy.deepcopy(b['budget_extensions'][0]))
  with self.assertRaises(ValueError):authorized_total(b)
 def test_unregistered_total_refused(self):
  b=copy.deepcopy(self.b);b['authorized_training_seconds']+=1
  with self.assertRaises(ValueError):authorized_total(b)
 def test_changed_doc_or_unapproved_stage_refused(self):
  with self.assertRaises(ValueError):validate_approval(self.a,'wrong','S0')
  with self.assertRaises(ValueError):validate_approval(self.a,self.a['approved_plan_sha256'],'S8')
 def test_supervised_and_encoder_are_charged(self):
  for kind in ['expert_ppo','gate_supervised','encoder_auxiliary']:self.assertEqual(learning_delta(kind,2.,12.),10.)
  with self.assertRaises(ValueError):learning_delta('frozen_evaluation',2.,12.)
  with self.assertRaises(ValueError):learning_delta('gate_supervised',12.,2.)
if __name__=='__main__':unittest.main()
