"""Staticproposalrefinement: avoidpretendingarangebeamcanpassrobotbody.
Preserveattempt002source; newmount+robotselfocclusiontest, stillnotBSPbinding.
"""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent;D=R/'revisions/attempt002';D.mkdir(parents=True,exist_ok=False)
p=R/'range_sensor_sim.py';raw=p.read_bytes();(D/p.name).write_bytes(raw);s=raw.decode('utf-8').replace("origin_B=(.15, 0., .05)","origin_B=(.30, 0., .10)");needle="        value = distance + self.rng.uniform(-self.noise, self.noise) if 0 <= distance <= self.max_range else None";assert needle in s
new="""        robot_group = np.array([0, 0, 0, 1, 0, 0], dtype=np.uint8)
        robot_id = np.array([-1], dtype=np.int32)
        self_distance = float(mujoco.mj_ray(self.model, self.scratch, point, direction,
                                          robot_group, 1, -1, robot_id))
        occluded = self_distance >= 0 and (distance < 0 or self_distance < distance)
        value = distance + self.rng.uniform(-self.noise, self.noise) if not occluded and 0 <= distance <= self.max_range else None"""
s=s.replace(needle,new);ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
s=(R/'static_qa_v2.py').read_text(encoding='utf-8').replace("D=HERE/'attempts/002'","D=HERE/'attempts/003'");needle="delayed=ProposedToF(plant.m,noise_half_m=.005,delay_samples=1);";assert needle in s;s=s.replace(needle,"blocked=ProposedToF(plant.m,origin_B=(0.,0.,0.),noise_half_m=0.,delay_samples=0);check(not blocked.sample(plant.d,0.).valid,'insidebodybeamnotseeThroughRobot');"+needle);ast.parse(s);p=R/'static_qa_v3.py';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n');print('NEW_MOUNT_SELF_OCCLUSION_STATIC_CHECK_READY_0STEPS')
