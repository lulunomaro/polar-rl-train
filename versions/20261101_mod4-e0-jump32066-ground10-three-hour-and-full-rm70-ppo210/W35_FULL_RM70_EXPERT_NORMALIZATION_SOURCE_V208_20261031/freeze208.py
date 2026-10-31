"""Freeze one new LOCAL purpose before executing it; never calls old entries."""
from pathlib import Path
import argparse, hashlib, json, time

HERE = Path(__file__).resolve().parent


def row(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('stage', choices=('preparation','cpu'))
    stage = parser.parse_args().stage
    if stage == 'preparation':
        value = dict(ID='NEW208_SOURCE_DERIVATION_V1', epoch=time.time(),
            purpose='Derive a new independent full original-CAD RM70 training source and full-world skill caller from immutable allowlisted source/text',
            source_rows=[row(HERE/'prepare208.py')], source_derivation_calls=1,
            model_NPZ_USD_raw_SDK_remote_reads=0, optimizer_updates=0, external_mutations=0)
        output = HERE / 'reports/PREPARATION208_PURPOSE_FROZEN.json'
    else:
        value = dict(ID='NEW208_CPU_COMPLETE_CYCLE_CAD_LAYOUT_DATA_ABI_V1', epoch=time.time(),
            purpose='New complete-cycle fields, original CAD reference/layout/course bounds and native measured data ABI; synthetic source contracts only',
            source_rows=[row(p) for p in sorted((HERE/'source').glob('*.py'))]+[row(HERE/'test208_once.py')],
            envs=8, control_steps=360, population_control_pairs=2880,
            expected_contract_groups=4, expected_negative_refusals=7,
            model_NPZ_USD_raw_SDK_remote_reads=0, neural_optimizer_updates=0,
            no_repeat_189_190_teacher_or_WM_CPU=True, no_repeat_consumed_W35_JSONL=True)
        output = HERE / 'reports/CPU208_PURPOSE_FROZEN.json'
    with output.open('x', encoding='utf8') as f:json.dump(value,f,indent=2)
    print(json.dumps(dict(purpose_frozen=str(output),ID=value['ID'],source_count=len(value['source_rows']))))


if __name__=='__main__':main()
