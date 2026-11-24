"""Export the measured experimental stair actor without optimizer/critic baggage."""
import hashlib
import json
from argparse import ArgumentParser
from pathlib import Path
import torch
from fsm_paths import HERE,E0_SHA,E0_BASE_SHA,JUMP_PATH
from fsm_io import put,sha256
from manual_fsm_model import make_stair


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--round',required=True)
    parser.add_argument('--name')
    args=parser.parse_args()
    source=args.source.resolve()
    payload=torch.load(source,map_location='cpu',weights_only=False)
    path=HERE/'weights'/(args.name or f'E_stair_stage2_{args.round}_{source.stem}_selected.pt')
    data=dict(format='mod4v3_manual_fsm_stair_v1',architecture='cnn12_z2',stair=payload['stair'],
        source_checkpoint=str(source.relative_to(HERE)),source_sha256=sha256(source),
        ppo_updates=payload['ppo_updates'],optimizer_steps=payload['optimizer_steps'],
        export_optimizer_updates=0,e0_sha256=E0_SHA,e0_base_sha256=E0_BASE_SHA,
        detector=json.loads((HERE/'DETECTOR.json').read_text(encoding='utf-8'))['config'],
        status='experimental_not_graduated')
    torch.save(data,path)
    original=make_stair(payload).state_dict()
    exported=make_stair(torch.load(path,map_location='cpu',weights_only=False)).state_dict()
    assert original.keys()==exported.keys() and all(torch.equal(original[k],exported[k]) for k in original)
    identity=hashlib.sha256()
    for name,value in sorted(exported.items()):
        identity.update(name.encode());identity.update(value.contiguous().numpy().tobytes())
    proof=dict(source_sha256=sha256(source),export_sha256=sha256(path),
        inference_weight_identity_sha256=identity.hexdigest(),all_tensors_bitwise_equal=True,
        removed='critic, optimizer and rollout state',optimizer_updates_in_export=0)
    put(HERE/'evidence/SELECTED_ACTOR_IDENTITY.json',proof)
    put(HERE/'CANDIDATE.json',dict(checkpoint=str(path.relative_to(HERE)),sha256=sha256(path),
        status='experimental_not_graduated',strict_stair_acceptance_passed=False,
        source_round=args.round,source_checkpoint=str(source.relative_to(HERE)),source_sha256=sha256(source),
        selected_round_ppo_updates=payload['ppo_updates'],selected_round_optimizer_steps=payload['optimizer_steps'],
        selected_snapshot_target_dr=payload.get('target_dr'),e0_sha256=E0_SHA,e0_base_sha256=E0_BASE_SHA,
        e0_height_blend_m=[.32,.40],calibration_sha256=sha256(HERE/'E0_CALIBRATION.json'),
        detector_config=json.loads((HERE/'DETECTOR.json').read_text(encoding='utf-8'))['config'],
        jump_sha256=sha256(JUMP_PATH),
        note='Selected through fixed closed-loop checkpoint comparison; final acceptance status is assigned from complete independent results.'))
    print(proof)


if __name__=='__main__':main()
