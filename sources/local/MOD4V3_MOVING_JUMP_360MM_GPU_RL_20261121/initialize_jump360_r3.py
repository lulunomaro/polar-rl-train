"""Initialize the neural mode head from R2 proprioception and measured first support."""
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from calibrate_jump360_r3 import PARENT_R2, R2_SHA
from jump360_r3_policy import MODEL_TYPE, R3ActorCritic
from jump360_scene import json_save, sha


def augment(dataset):
    for i in range(len(dataset.files)//4):
        obs, action, relative, contact = (dataset[f"{name}_{i}"] for name in ("obs", "act", "relative", "contact"))
        jump = (relative >= 0) & (relative < int(contact.item()))
        target_exists = jump & (obs[:, 30] > .5)
        samples = np.flatnonzero(jump | ((relative >= -32) & (relative <= contact+52) & (relative % 2 == 0)))
        past = (samples[:, None] - np.arange(11, -1, -1)).clip(min=0)
        for hold in (10, 15, 20, 30, 40, 46, 50):
            augmented = obs.copy()
            augmented[:, 30] = (relative >= 0) & (relative < hold)
            yield augmented[samples], augmented[past].reshape(-1, 420), action[samples], jump[samples], target_exists[samples]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--demos", type=Path, required=True)
    args = parser.parse_args()
    if sha(PARENT_R2) != R2_SHA:
        raise ValueError("R2 checkpoint hash mismatch")
    torch.set_num_threads(3)
    torch.manual_seed(36003)
    args.out.mkdir(exist_ok=True, parents=True)
    model = R3ActorCritic.warm_from_r2(PARENT_R2)
    body = model.actor_body
    with np.load(args.demos) as raw:
        arrays = [torch.from_numpy(np.concatenate(values)) for values in zip(*augment(raw), strict=True)]
    obs, hist, action, jump_label, actor_label = arrays
    trainable = list(body.mode_head.parameters())
    expert = list(body.e_jump.encoder.parameters()) + list(body.e_jump.delta_head.parameters())
    optim = torch.optim.Adam((dict(params=trainable, lr=.0015), dict(params=expert, lr=.00005)))
    trace = []
    for epoch in range(10):
        stats = torch.zeros(4)
        for rows in torch.randperm(len(obs)).split(512):
            mask = actor_label[rows]
            phase, output, _ = body.components(obs[rows], hist[rows])
            phase_loss = F.binary_cross_entropy_with_logits(phase, jump_label[rows].float())
            imitation = F.smooth_l1_loss(output[mask].clamp(-6., 6.), action[rows][mask], beta=.15)
            loss = phase_loss + 1.5*imitation
            optim.zero_grad(set_to_none=True)
            loss.backward()
            optim.step()
            with torch.no_grad():
                stats += torch.tensor([phase_loss.item()*len(rows), imitation.item()*len(rows),
                                       ((phase>0.) == jump_label[rows]).sum().item(), len(rows)])
        row = dict(epoch=epoch+1, phase_bce=float(stats[0]/stats[3]), jump_action_loss=float(stats[1]/stats[3]),
                   phase_accuracy=float(stats[2]/stats[3]))
        print(row, flush=True)
        trace.append(row)
    path = args.out/"model_init.pt"
    metadata = dict(parent_sha256=R2_SHA, demos_sha256=sha(args.demos), frames=len(obs), ppo_updates=0,
                    imitation_epochs=trace, key_hold_augmentation=[10, 15, 20, 30, 40, 46, 50])
    torch.save(dict(model_type=MODEL_TYPE, obs_dim=35, hist_dim=420, action_dim=6,
                    state_dict=model.state_dict(), metadata=metadata), path)
    json_save(args.out/"INIT.json", dict(sha256=sha(path), **metadata))


if __name__ == "__main__":
    main()

