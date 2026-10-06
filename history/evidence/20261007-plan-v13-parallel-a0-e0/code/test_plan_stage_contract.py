import copy,unittest
from plan_stage_contract import validate,SOURCE_SHA
class Contract(unittest.TestCase):
 def setUp(self):
  self.a={'approved':True,'approval_basis':'explicit_human_message_in_current_chat','version':'1.3','approved_plan_sha256':'exact','allowed_stages':['S1','S1A'],'revision_basis':{'no_new_DR_task_interface_physics_hardware_reset_scope':True}}
  self.b={'authorized_training_seconds':828000,'remaining_training_seconds':500000,'charged_training_seconds':328000,'active_segment':None}
  self.s={'sha256':SOURCE_SHA,'iteration_stored':23509,'finite_tensors':68};self.c={'pass_':True}
 def test_allowed_without3060_verdict(self):self.assertTrue(validate(self.a,'exact',self.b,self.s,self.c))
 def test_plan_changed(self):
  with self.assertRaises(ValueError):validate(self.a,'different',self.b,self.s,self.c)
 def test_active(self):
  self.b['active_segment']={'pid':1}
  with self.assertRaises(ValueError):validate(self.a,'exact',self.b,self.s,self.c)
 def test_invalid_source(self):
  self.s['sha256']='other'
  with self.assertRaises(ValueError):validate(self.a,'exact',self.b,self.s,self.c)
 def test_not_authorized(self):
  self.a['approved']=False
  with self.assertRaises(ValueError):validate(self.a,'exact',self.b,self.s,self.c)
 def test_no_scope_revision(self):
  self.a['revision_basis']={}
  with self.assertRaises(ValueError):validate(self.a,'exact',self.b,self.s,self.c)
 def test_insufficient_budget(self):
  self.b['remaining_training_seconds']=120
  with self.assertRaises(ValueError):validate(self.a,'exact',self.b,self.s,self.c)
 def test_cpu_failed(self):
  with self.assertRaises(ValueError):validate(self.a,'exact',self.b,self.s,{'pass_':False})
if __name__=='__main__':unittest.main()
