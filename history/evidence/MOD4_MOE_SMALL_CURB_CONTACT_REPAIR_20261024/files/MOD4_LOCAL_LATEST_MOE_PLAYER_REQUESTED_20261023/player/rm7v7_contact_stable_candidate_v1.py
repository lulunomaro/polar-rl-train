from rm7v7_moe_sim import RM7V7MoESim, ROUTES
import mujoco

class ContactStableRM7V7MoESim(RM7V7MoESim):
    """Versioned player candidate: same terrain and actors, single-contact native CCD."""
    def __init__(self):
        super().__init__()
        self.model.opt.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_MULTICCD)
        self.reset_route('flat_run')
    def parameter_readback(self):
        result=super().parameter_readback()
        disabled=int(self.model.opt.disableflags)
        assert disabled & int(mujoco.mjtDisableBit.mjDSBL_MULTICCD)
        result.update(mujoco_version=mujoco.__version__,collision_candidate='nativeCCD with multiCCD disabled',actual_disableflags=disabled,actual_enableflags=int(self.model.opt.enableflags),validated_scope='Only finite flat-route small-contact comparisons, not jump/recovery/all terrain qualification')
        return result
