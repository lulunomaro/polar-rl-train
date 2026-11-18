"""Only E1 follows the authorized zeroDR -> clean coverage -> fullDR mixture course."""
import torch
from .continuous_stair_env import ContinuousStairEnv
from .e1_dr_mixture import E1DRMixture

class DRCurriculumEnv(ContinuousStairEnv):
    def __init__(self,cfg,meta,bank):
        self._mixture_ready=False;self._skip_course_finish=False
        super().__init__(cfg,meta,bank)
        self.dr_course=E1DRMixture(self);self._mixture_ready=True
    def _finish_course_episodes(self,ids):
        if self._skip_course_finish:return
        if self._mixture_ready:self.dr_course.finish(ids)
        super()._finish_course_episodes(ids)
    def _reset_idx(self,ids):
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        ready=getattr(self,'_mixture_ready',False)
        if ready:
            self._finish_course_episodes(ids)
            self.dr_course.prepare(ids)
            self._skip_course_finish=True
        try:super()._reset_idx(ids)
        finally:self._skip_course_finish=False
        if ready:
            selected=ids[self.continuous_stair_mask[ids]&(self.dr_course.stage[ids]==0)]
            self.stair_speed[selected]=.47
            from .reset_sensor_refresh import refresh_reset_sensors
            e1=ids[self.continuous_stair_mask[ids]]
            if len(e1):refresh_reset_sensors(self,e1)
            self._course_commands()
    def terrain_checkpoint_state(self):
        state=super().terrain_checkpoint_state()
        if self._mixture_ready:state['E1_DR_mixture']=self.dr_course.checkpoint()
        return state
