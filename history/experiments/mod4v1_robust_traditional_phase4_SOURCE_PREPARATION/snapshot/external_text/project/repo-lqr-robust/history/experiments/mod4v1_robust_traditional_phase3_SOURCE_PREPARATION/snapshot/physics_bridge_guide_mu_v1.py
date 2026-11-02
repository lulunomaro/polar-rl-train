"""EXPLICITalternativematerialsemantics, notretroactiveoldresultsfix.
Originalguidegeom.02+world.9 at equalpriority yielded effective.9 (audited).
Thisbranchgivesguideauthoredfrictionpriority; tireDRstillraisesaboveallothers.
No claimexactPhysXcombineorhardwarecalibration; robustnessmustreportbothbranches.
"""
import numpy as np
from physics_bridge_v4_grade import BufferedImuPlant


class GuideMaterialPlant(BufferedImuPlant):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        guide = [i for i in range(self.m.ngeom) if self.m.geom(i).name.startswith('guide_wheel_')]
        assert len(guide) == 8
        old = self.m.geom_priority[guide].copy()
        self.m.geom_priority[guide] = int(np.max(self.m.geom_priority)) + 1
        self.material_variant = dict(
            kind='EXPLICIT_GUIDE_AUTHORED_PRIORITY_ALTERNATIVE_NOT_PHYSX_EQUIVALENCE',
            guide_ids=guide, before=old.tolist(), after=self.m.geom_priority[guide].tolist(),
            guide_authored_friction3=self.m.geom_friction[guide].tolist(),
            old_results_unchanged=True, tire_DR_rules_unchanged=True)
