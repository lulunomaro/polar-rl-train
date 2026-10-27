from pathlib import Path
import ast,json,hashlib,shutil
HERE=Path(__file__).resolve().parent;L=HERE.parent
old=L/'root_augmented_world_model_candidate/v4/supermimic_wheel_leg_v3'
new=L/'root_augmented_world_model_candidate/v5/supermimic_wheel_leg_v3'
report=L/'reports/FINAL_NATIVE_VENDOR5_AND_MDP4_SOURCE_DERIVATION_ACTUAL.json'
assert not new.exists() and not report.exists()
new.parent.mkdir()
shutil.copytree(old,new)
p=new/'augmented_wheel_leg_world_model_v1.py';text=p.read_text('utf8')
a='self.in_dim = 13+2*num_joints+auxiliary_dim+action_dim+context_dim+2'
b='self.in_dim = 13+2*num_joints+auxiliary_dim+action_dim+context_dim+3'
assert text.count(a)==1;text=text.replace(a,b,1)
a='return torch.stack((self.edge_x_m-p[...,0],\n                            self.platform_top_z_m-p[...,2]), -1)'
b='return torch.stack((self.edge_x_m-p[...,0], -p[...,1],\n                            self.platform_top_z_m-p[...,2]), -1)'
assert text.count(a)==1;text=text.replace(a,b,1);ast.parse(text);p.write_text(text,'utf8')
p=HERE/'converted_MOD4_jump_mdp_v3.py';mdp=p.read_text('utf8')
mdp=mdp.replace('def __init__(self,provider):','def __init__(self,provider,leg_encoder_joint_names=None):',1)
mdp=mdp.replace('        self.provider=provider\n    def to(self,device):return ConvertedMOD4JumpMdp(self.provider.to(device))',
'        self.provider=provider\n        self.leg_encoder_joint_names=tuple(leg_encoder_joint_names or provider.metadata["actuator_leg_joint_names"])\n        require(len(self.leg_encoder_joint_names)==4,"four actual leg encoder names required")\n        self.leg_ids=[provider.names.index(n) for n in self.leg_encoder_joint_names]\n    def to(self,device):return ConvertedMOD4JumpMdp(self.provider.to(device),self.leg_encoder_joint_names)',1)
mdp=mdp.replace('q[...,self.provider.leg_ids]+=context[...,27:31]','q[...,self.leg_ids]+=context[...,27:31]',1)
mdp=mdp.replace('            physical_joints=30,packed_state=127,dynamic_aux=54,static_xi=31,','            physical_joints=30,packed_state=127,dynamic_aux=54,static_xi=31,\n            actual_leg_encoder_joint_names=self.leg_encoder_joint_names,world_model_terrain_features=3,',1)
dest=HERE/'converted_MOD4_jump_mdp_v4.py';assert not dest.exists();ast.parse(mdp);dest.write_text(mdp,'utf8')
result={'passed':True,'source_only':True,'vendor_package':str(new),'MDP':str(dest),'changes':['WM adds lane-relativeY to edgeX/topZ; fixed finite platform is not horizontally invariant','Encoder bias maps actual runtime actuator group names, not an assumed source joint permutation'],'original_vendor_learning_loop_changed':False,'actual_SDK':False,'Task_GO':False}
report.write_text(json.dumps(result,indent=2),'utf8')
print(json.dumps(result))

