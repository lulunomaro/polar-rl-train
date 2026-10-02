"""v2 item 1: 5-frame observation history + a small encoder (latent 3) for the actor.

Why this module exists
----------------------
The reference implementation (refs/fudan_src/fudan_rl_wheel_leg-main) gives its actor a 5-frame
history and a small encoder that produces a 3-D latent, while the critic keeps the privileged
observation set (asymmetric actor-critic).  Its `ActorCriticSequence` is written against an OLD
rsl_rl module API, so the code cannot be copied: our installed rsl_rl is the rewritten 4.x line
(`rsl_rl/models/{MLPModel,RNNModel,CNNModel}` + `rsl_rl/modules/{MLP,RNN,Distribution}`,
`resolve_callable`, and `RslRlPpoActorCriticCfg` is formally deprecated in favour of
`RslRlMLPModelCfg` -- see isaaclab_rl/rsl_rl/rl_cfg.py:356-360).

Two implementation facts made this a small subclass instead of a rewrite:
  * `MLPModel.get_latent(obs, masks, hidden_state)` is the single place where the model turns
    observation groups into its MLP input, so an encoder slots in there.
  * `MLPModel._get_latent_dim()` is consulted to size the MLP head, and it is called AFTER
    `self.obs_dim` is resolved, so overriding it is enough to make the head consume
    `frame + latent` dimensions.

History ordering (corrected against the installed ObservationManager)
----------------------------------------------------------------------
Isaac keeps history PER TERM, then concatenates terms. The 175 numbers are
[commands history, height history, ..., mode history]. Taking the last 35
does not give the current frame. latest_indices gathers each term's newest
sample. The encoder retains the term-major 175-D input; export uses the same
gather. Previously trained sequence checkpoints have different semantics and
must not be silently reused under this layout. A plain 35-D policy is the
controlled warm-start baseline. Shape equality alone is insufficient.

What is deliberately NOT copied
-------------------------------
The reference trains the encoder with its OWN optimizer and an auxiliary regression loss against
the privileged (scaled) base linear velocity, and detaches the latent on the actor path.  That
needs hooks inside the PPO update, which lives in site-packages here.  This module instead lets
PPO train the encoder jointly through the actor path -- the requirement as stated is "5-frame
history + a small encoder (latent 3)", which joint training satisfies.  If the joint version
underperforms, the separate-optimiser variant is the documented next step (see
docs/MOD4_V2_REDESIGN_AUDIT_20260912.md section 1).

Knobs (read by the patch that wires this in, not here):
    RM_SEQ_ENCODER=1            enable this model
    RM_SEQ_LATENT=3             latent width
    RM_SEQ_ENCODER_HIDDEN=128,64
"""

from __future__ import annotations
import os

import copy

import torch
import torch.nn as nn
from rsl_rl.models import MLPModel
from rsl_rl.modules import MLP
from repair_contracts import latest_term_indices

# v2 fix (2026-09-13): these were hard-coded, but the dimensions CANNOT travel through
# RslRlMLPModelCfg (it has no passthrough for custom kwargs -- passing frame_dim raised
# "TypeError: RslRlMLPModelCfg.__init__() got an unexpected keyword argument 'frame_dim'").
# The model therefore reads the same environment variables the launcher sets.
FRAME_DIM = int(os.environ.get("RM_FRAME_DIM", "35"))   # the MOD4 deployment contract
LATENT_DIM = int(os.environ.get("RM_SEQ_LATENT", "3"))  # reference: ">=3 for base lin vel"
ENCODER_HIDDEN = tuple(int(v) for v in
                       os.environ.get("RM_SEQ_ENCODER_HIDDEN", "128,64").split(",") if v.strip())
HISTORY_LEN = 5


class LatentEncoderModel(MLPModel):
    """Actor/critic MLP whose actor input is `[current frame | encoder(history)]`."""

    is_recurrent: bool = False

    def __init__(self, *args, **kwargs):
        # These must exist before MLPModel.__init__ calls _get_latent_dim().
        self.frame_dim = int(kwargs.pop("frame_dim", FRAME_DIM))
        self.latent_dim = int(kwargs.pop("latent_dim", LATENT_DIM))
        self.encoder_hidden_dims = tuple(kwargs.pop("encoder_hidden_dims", ENCODER_HIDDEN))
        self._activation = str(kwargs.get("activation", "elu"))
        # The encoder belongs to the ACTOR ONLY.  The critic keeps its full privileged set, which
        # is also wider than frame_dim -- gating on the dimension alone would silently give the
        # critic an encoder and throw away the privileged information it exists to consume.
        _obs_set = kwargs.get("obs_set", args[2] if len(args) > 2 else "")
        self._enable_encoder = str(_obs_set) == "actor"
        super().__init__(*args, **kwargs)
        if self._enable_encoder and self.obs_dim > self.frame_dim:
            self.encoder = MLP(self.obs_dim, self.latent_dim, self.encoder_hidden_dims,
                               self._activation)
            # Zero the NEW ACTOR INPUT COLUMNS during 35->38 warm start only.
            # Zeroing the encoder output as well makes both sides' gradients zero.
        else:
            # no history (or the critic set): degrade to a plain MLP rather than crash
            self.encoder = None
        if self.encoder is not None and self.obs_dim % self.frame_dim:
            raise ValueError("history width does not match frame contract")
        self.register_buffer("latest_indices", latest_term_indices(
            self.obs_dim // self.frame_dim if self.encoder is not None else 1,
            self.frame_dim), persistent=False)

    @property
    def has_encoder(self) -> bool:
        return self.encoder is not None

    def _get_latent_dim(self) -> int:
        """Size the MLP head: `frame + latent` for the actor when a history is present."""
        if getattr(self, "_enable_encoder", False) and getattr(self, "obs_dim", 0) > self.frame_dim:
            return self.frame_dim + self.latent_dim
        return self.obs_dim

    def get_latent(self, obs, masks=None, hidden_state=None):
        """Encoder over the full (history) input; the actor head sees the newest frame + latent."""
        x = super().get_latent(obs, masks, hidden_state)
        if self.encoder is None:
            return x
        current = x.index_select(-1, self.latest_indices)
        return torch.cat([current, self.encoder(x)], dim=-1)

    # --- export -------------------------------------------------------------------------
    def as_jit(self) -> nn.Module:
        return _TorchLatentModel(self)

    def as_onnx(self, verbose: bool) -> nn.Module:
        return _OnnxLatentModel(self, verbose)


class _TorchLatentModel(nn.Module):
    """TorchScript-friendly copy: 175 -> encoder -> [35 | 3] -> actor MLP -> action."""

    def __init__(self, model: LatentEncoderModel) -> None:
        super().__init__()
        self.frame_dim = model.frame_dim
        self.register_buffer("latest_indices", model.latest_indices.detach().clone(), persistent=False)
        self.obs_normalizer = copy.deepcopy(model.obs_normalizer)
        self.mlp = copy.deepcopy(model.mlp)
        self.encoder = copy.deepcopy(model.encoder) if model.encoder is not None else None
        if model.distribution is not None:
            self.deterministic_output = model.distribution.as_deterministic_output_module()
        else:
            self.deterministic_output = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.obs_normalizer(x)
        if self.encoder is None:
            return self.deterministic_output(self.mlp(x))
        latent = torch.cat([x.index_select(-1, self.latest_indices), self.encoder(x)], dim=-1)
        return self.deterministic_output(self.mlp(latent))

    @torch.jit.export
    def reset(self) -> None:
        pass


class _OnnxLatentModel(nn.Module):
    """ONNX wrapper: ONE input of `history_length * frame_dim` (newest frame last)."""

    is_recurrent: bool = False

    def __init__(self, model: LatentEncoderModel, verbose: bool) -> None:
        super().__init__()
        self.verbose = verbose
        self.frame_dim = model.frame_dim
        self.register_buffer("latest_indices", model.latest_indices.detach().clone(), persistent=False)
        self.obs_normalizer = copy.deepcopy(model.obs_normalizer)
        self.mlp = copy.deepcopy(model.mlp)
        self.encoder = copy.deepcopy(model.encoder) if model.encoder is not None else None
        if model.distribution is not None:
            self.deterministic_output = model.distribution.as_deterministic_output_module()
        else:
            self.deterministic_output = nn.Identity()
        self.input_size = model.obs_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.obs_normalizer(x)
        if self.encoder is None:
            return self.deterministic_output(self.mlp(x))
        latent = torch.cat([x.index_select(-1, self.latest_indices), self.encoder(x)], dim=-1)
        return self.deterministic_output(self.mlp(latent))

    def get_dummy_inputs(self) -> tuple[torch.Tensor]:
        return (torch.zeros(1, self.input_size),)

    @property
    def input_names(self) -> list[str]:
        # NOT "obs": the vector is a flattened 5-frame history, newest frame LAST.
        return ["obs_history"]

    @property
    def output_names(self) -> list[str]:
        return ["actions"]
