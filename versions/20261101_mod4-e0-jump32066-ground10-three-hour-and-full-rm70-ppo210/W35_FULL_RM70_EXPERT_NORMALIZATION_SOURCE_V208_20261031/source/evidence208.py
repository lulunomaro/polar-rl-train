"""Preserve actual terrain reset, add only expected-q audit bookkeeping."""
from base_learning208 import E1TerrainLearningEnv
from e1_reset_evidence import bind_expected_reset_q

class E1ResetEvidenceLearningEnv(E1TerrainLearningEnv):
    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        if hasattr(self,'_rough_probe_expected_q'):
            bind_expected_reset_q(self,ids)
