"""Contact confirmation on the physics clock, independent of policy sampling.
A raw contact may be floor, riser or top support. It must never be substituted
for rolling odometry, which separately rejects wall contacts and flight.
"""
import numpy as np

class WheelContactLatch:
    def __init__(self, count=2):
        self.confirmed=np.zeros(count,dtype=bool)
        self.present_s=np.zeros(count)
        self.absent_s=np.zeros(count)
        self.scale=np.zeros(count)

    def update(self, contacts, dt):
        contacts=np.asarray(contacts,dtype=bool)
        self.present_s=np.where(contacts,self.present_s+dt,0.)
        self.absent_s=np.where(contacts,0.,self.absent_s+dt)
        self.confirmed=np.where(self.present_s>=.004,True,self.confirmed)
        self.confirmed=np.where(self.absent_s>=.006,False,self.confirmed)
        self.scale=np.where(self.confirmed,np.minimum(1.,self.scale+dt/.012),0.)
        return self.snapshot()

    def snapshot(self):
        return dict(wheel_contact_confirmed=self.confirmed.tolist(),
                    wheel_contact_present_s=self.present_s.tolist(),
                    wheel_contact_absent_s=self.absent_s.tolist(),
                    wheel_torque_scale_physics=self.scale.tolist())
