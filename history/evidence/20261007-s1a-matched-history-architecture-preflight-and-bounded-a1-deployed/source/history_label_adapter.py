"""History teacher lifecycle: reset-frame SDK body-velocity cache is not a training target."""
from history_observation_adapter import HistoryObservationAdapter,tensor

class LabelHistoryAdapter(HistoryObservationAdapter):
    def augment(self,clean):
        # At a reset SDK write updates root world buffers within the current physics timestamp;
        # derived body-frame velocities may still contain the pre-reset cached value.
        valid=(~self.history.pending).clone()
        result=super().augment(clean)
        result['body_velocity_valid']=valid[:,None].to(result['body_velocity_label'].dtype)
        result['body_velocity_label'][~valid]=0.
        return result
