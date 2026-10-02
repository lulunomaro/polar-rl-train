#!/usr/bin/env python3
"""Export a MOD4 checkpoint to ONNX WITHOUT building the Isaac env (v2 item 5).

Why standalone
--------------
The obvious exporter would rebuild the runner (`OnPolicyRunner(vec_env, ...)`), which needs Isaac
Sim and a GPU -- and the GPU is busy with the training chain for hours at a time.  Everything the
export needs is already in the checkpoint: the actor's `state_dict` fixes every dimension, and the
model classes are plain `nn.Module`s (`rsl_rl.models.MLPModel`, or our `LatentEncoderModel`).

This also keeps the export identical to what the deployment gate checks:
  * ONE input, named `obs_history` when the encoder is on, `obs` otherwise;
  * output = the action MEAN (the distribution's deterministic output module), 6 wide;
  * the training contract is written into the ONNX `metadata_props`, so the MuJoCo harness can
    refuse to drift from it (the harness already reads `wheel_no_load_rad_s` etc. from there).

Usage
-----
    PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python     # has torch + onnx
    $PY sim2sim_mod4/export_mod4_onnx.py \
        --checkpoint logs/isaac_mod4/<run>/model_<N>.pt \
        --out train/deploy/mod4_model_<N>.onnx

    # history variant (only for a checkpoint that was TRAINED with RM_SEQ_ENCODER=1):
    $PY sim2sim_mod4/export_mod4_onnx.py --checkpoint ... --out ... --encoder-history 5

Exit codes: 0 = exported, 2 = refused (dimension/architecture mismatch), 3 = missing dependency.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "isaac" / "mod4"))

CONTRACT_JSON = ROOT / "train" / "deploy" / "contract_rm2025_later.json"
DIST_CFG = {"class_name": "GaussianDistribution", "init_std": 0.15, "std_type": "scalar"}
GROUPS = {"actor": ["policy"], "critic": ["critic"]}


def build_actor(frame_dim: int, history: int, hidden: tuple, latent: int, enc_hidden: tuple):
    """Build the actor the checkpoint was trained with (history 0 -> plain MLPModel)."""
    import torch
    from rsl_rl.models import MLPModel
    obs_dim = frame_dim * (history if history > 0 else 1)
    obs = {"policy": torch.zeros(1, obs_dim)}
    if history > 0:
        from mod4_sequence_model import LatentEncoderModel
        return LatentEncoderModel(obs, GROUPS, "actor", 6, hidden, "elu", False, dict(DIST_CFG),
                                  frame_dim=frame_dim, latent_dim=latent,
                                  encoder_hidden_dims=tuple(enc_hidden))
    return MLPModel(obs, GROUPS, "actor", 6, hidden, "elu", False, dict(DIST_CFG))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frame-dim", type=int, default=35, help="the 35-D deployment contract")
    ap.add_argument("--encoder-history", type=int, default=0,
                    help="0 = plain 35-D actor; 5 = the checkpoint must have been trained with it")
    ap.add_argument("--latent", type=int, default=3)
    ap.add_argument("--hidden", default="256,128,64")
    ap.add_argument("--encoder-hidden", default="128,64")
    ap.add_argument("--opset", type=int, default=17)
    args = ap.parse_args(argv)

    try:
        import torch
        import onnx
        from rsl_rl.models import MLPModel  # noqa: F401
    except Exception as exc:
        print("RESULT: EXPORT FAIL -- missing dependency (%s)" % exc)
        return 3

    ck_path = pathlib.Path(args.checkpoint)
    if not ck_path.is_file():
        print("RESULT: EXPORT FAIL -- checkpoint not found: %s" % ck_path)
        return 2
    ck = torch.load(ck_path, map_location="cpu", weights_only=False)
    sd = ck.get("actor_state_dict")
    if not sd:
        print("RESULT: EXPORT FAIL -- no actor_state_dict in %s" % ck_path)
        return 2

    hidden = tuple(int(v) for v in args.hidden.split(","))
    enc_hidden = tuple(int(v) for v in args.encoder_hidden.split(","))
    model = build_actor(args.frame_dim, args.encoder_history, hidden, args.latent, enc_hidden)
    want, have = set(model.state_dict()), set(sd)
    missing = sorted(want - have)
    unexpected = sorted(have - want)
    # `encoder.*` is the only kind of key a fresh model may lack; anything else is a real mismatch
    bad_missing = [k for k in missing if not k.startswith("encoder.")]
    if bad_missing or unexpected:
        print("RESULT: EXPORT FAIL -- the checkpoint was not trained with this layout")
        print("   checkpoint lacks (non-encoder): %s" % bad_missing)
        print("   checkpoint has, model does not:  %s" % unexpected)
        print("   (a checkpoint trained WITHOUT the encoder must be exported with "
              "--encoder-history 0)")
        return 2
    if missing:
        print("   note: %d fresh parameter(s) (%s...) -- exporting an untrained encoder"
              % (len(missing), ", ".join(missing[:2])))
    model.load_state_dict(sd, strict=False)
    model.eval()

    wrapper = model.as_onnx(verbose=False)
    wrapper.eval()
    dummy = wrapper.get_dummy_inputs()
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        wrapper, dummy, str(out_path), opset_version=args.opset, verbose=False,
        input_names=list(wrapper.input_names), output_names=list(wrapper.output_names),
        dynamic_axes={wrapper.input_names[0]: {0: "batch"}}, dynamo=False,
    )

    # --- contract metadata: the MuJoCo harness reads this and refuses to drift -------------
    contract = json.loads(CONTRACT_JSON.read_text(encoding="utf8")) if CONTRACT_JSON.is_file() else {}
    proto = onnx.load(str(out_path))
    meta = {
        "frame_dim": str(args.frame_dim),
        "encoder_history": str(args.encoder_history),
        "latent_dim": str(args.latent) if args.encoder_history > 0 else "0",
        "obs_layout": ("history:%d newest-frame-last" % args.encoder_history
                       if args.encoder_history > 0 else "single-frame-35"),
        "obs_width": str(args.frame_dim * (args.encoder_history or 1)),
        "action_width": "6",
    }
    for key in ("leg_kp", "leg_kd", "wheel_kd", "leg_action_scale", "wheel_action_scale",
                "wheel_radius", "leg_effort", "wheel_effort", "physics_dt", "policy_hz",
                "wheel_no_load", "yaw_rate_at_unit_action"):
        if key in contract:
            meta[key] = str(contract[key])
    if "export_action_permutation" in contract:
        meta["export_action_permutation"] = ",".join(str(v) for v in contract["export_action_permutation"])
    meta["checkpoint"] = ck_path.name
    have_keys = {e.key for e in proto.metadata_props}
    for k, v in sorted(meta.items()):
        if k in have_keys:
            for e in proto.metadata_props:
                if e.key == k:
                    e.value = v
        else:
            proto.metadata_props.append(onnx.StringStringEntryProto(key=k, value=v))
    onnx.save(proto, str(out_path))

    print("exported %s" % out_path)
    print("   input : %s %s (width %s)" % (wrapper.input_names[0], tuple(dummy[0].shape),
                                           meta["obs_width"]))
    print("   output: %s" % wrapper.output_names[0])
    print("   contract metadata: %s" % ", ".join(sorted(k for k in meta if k in contract)))
    print("RESULT: EXPORT OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
