"""Materialize isolated, undeployed source candidates; original source stays exact."""
from pathlib import Path
import ast
import hashlib
import json
import time
import traceback

D = Path(__file__).resolve().parent
W = D.parent
O = D / 'isolated'
R = D / 'reports'
S = W / 'MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
MOD = S / 'runtime/isaac/mod4'
IMPORT = 'from nominal_d0_source_audit_v1 import mild_dr_present_or_nominal, capture_nominal_d0_reference, parameter_audit as s5_parameter_audit\n'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def wrap_slice(source, start, end, guard):
    block = source[start:end]
    return source[:start] + guard + ''.join('    ' + line if line.strip() else line for line in block.splitlines(True)) + source[end:]


def main():
    R.mkdir(exist_ok=True)
    out = R / 'NOMINAL_ISOLATED_SOURCE_CANDIDATES_MATERIALIZED_ACTUAL.json'
    assert not out.exists()
    rows = []
    for name in ('spring_pressure_audit_runtime.py', 'gas_damping_sdk_adapter.py',
                 'chassis_com_pose_roundtrip_sdk_adapter.py', 'explicit_pd_sdk_adapter.py',
                 'chassis_pd_training_env.py', 'nominal_parameter_audit.py',
                 'factor_runtime_3060_reference17b_v1.py'):
        original = S / name if name.startswith('factor_runtime') else MOD / name
        raw = original.read_bytes()
        source = raw.decode('utf8')
        before = source
        if name == 'spring_pressure_audit_runtime.py':
            start = source.index('        mild=self.env._mild_dr;')
            end = source.index('        mild.audit=types.MethodType(audit,mild)') + len('        mild.audit=types.MethodType(audit,mild)\n')
            source = wrap_slice(source, start, end, '        if mild_dr_present_or_nominal(self.env):\n')
            source += '\n        else:\n            capture_nominal_d0_reference(self.env)\n'
        elif name == 'gas_damping_sdk_adapter.py':
            start = source.index('        mild=self.env._mild_dr;')
            end = source.index('        pressure=self.env._spring_pressure;')
            source = wrap_slice(source, start, end, '        adapter=self  # Explicitly retained for the nominal gas-to-spring audit overlay.\n        if mild_dr_present_or_nominal(self.env):\n')
        elif name in ('chassis_com_pose_roundtrip_sdk_adapter.py', 'explicit_pd_sdk_adapter.py'):
            start = source.index('        mild=self.env._mild_dr;')
            source = source[:start] + '        if not mild_dr_present_or_nominal(self.env):\n            return\n' + source[start:]
        elif name == 'chassis_pd_training_env.py':
            assert source.count('parameter_auditor=self._mild_dr.audit()') == 1
            source = source.replace('parameter_auditor=self._mild_dr.audit()', 'parameter_auditor=s5_parameter_audit(self)')
        elif name == 'nominal_parameter_audit.py':
            assert source.count('def parameter_audit(env):') == 1
            source = source.replace('def parameter_audit(env):', 'def legacy_nominal_parameter_audit(env):')
            source += '\n\ndef parameter_audit(env):\n    return s5_parameter_audit(env)\n'
        else:
            old = 'mild_factor=js(e._mild_dr.factor),mild_nominal=js(e._mild_dr.nominal),mild_mu=js(e._mild_dr.mu),mild_outputs={k:js(v) for k,v in e._mild_dr.output.items()},'
            new = 'mild_factor=js(e._mild_dr.factor) if mild_dr_present_or_nominal(e) else None,mild_nominal=js(e._mild_dr.nominal) if mild_dr_present_or_nominal(e) else None,mild_mu=js(e._mild_dr.mu) if mild_dr_present_or_nominal(e) else None,mild_outputs={k:js(v) for k,v in e._mild_dr.output.items()} if mild_dr_present_or_nominal(e) else None,'
            assert source.count(old) == 1
            source = source.replace(old, new)
            old_loop = '  walk(getattr(e,k),k,8)'
            assert source.count(old_loop) == 1
            source = source.replace(old_loop, '  if k==\'_mild_dr\' and not mild_dr_present_or_nominal(e):continue\n' + old_loop)
        source = IMPORT + source
        ast.parse(source)
        target = O / name
        with target.open('x', encoding='utf8', newline='\n') as f:
            f.write(source)
        rows.append(dict(original=str(original), original_SHA=hashlib.sha256(raw).hexdigest(),
                         candidate=str(target), candidate_SHA=H(target), original_source_unmodified=H(original) == hashlib.sha256(raw).hexdigest()))
    with out.open('x', encoding='utf8') as f:
        json.dump(dict(epoch=time.time(), candidates=rows, helper=dict(path=str(O/'nominal_d0_source_audit_v1.py'), sha256=H(O/'nominal_d0_source_audit_v1.py')),
                       parsed_only_not_CPU_admitted_or_deployed=True, no_GPU_network_learning_budget=True,
                       old_rejections_and_CPU_verification_to_follow=True), f, indent=2)
    print(json.dumps(dict(materialized=len(rows), isolated_only=True, not_CPU_or_GPU_pass=True)))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        R.mkdir(exist_ok=True)
        with (R/('NOMINAL_MATERIALIZER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(), no_GPU_network_learning_budget=True),f,indent=2)
        raise
