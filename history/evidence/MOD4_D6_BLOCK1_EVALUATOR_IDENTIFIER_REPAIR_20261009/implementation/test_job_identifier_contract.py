"""CPU checks: reject unsafe names without starving unrelated valid evaluation jobs."""
from pathlib import Path
import ast,json,sys
from job_identifier_contract import accepted,partition

def main():
    here=Path(__file__).resolve().parent
    bridge=Path(sys.argv[1]) if len(sys.argv)>1 else here.parent/'MOD4_MOE_PLAN_EXECUTION_20261007/artifact_service.py'
    module=ast.parse(bridge.read_text(encoding='utf8'))
    key=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='key')
    assert any(isinstance(n,ast.Constant) and n.value==r'[a-z0-9][a-z0-9-]{5,95}' for n in ast.walk(key))
    namespace={'re':__import__('re')};exec(compile(ast.Module(body=[key],type_ignores=[]),'actual_bridge_key','exec'),namespace)
    values=['clk2500-closure-episode-d3-97-d5-retention-20261002-white2-flat','clk2500-closure-episode-d3-95-d5-retention-20261002-white_v2-flat','abcde','abcdef','a'*96,'a'*97,'../escape','ABCDEF','white 2',None,4]
    for value in values:
        try:namespace['key'](value);expected=True
        except ValueError:expected=False
        assert accepted(value)==expected,repr(value)
    valid,invalid=partition(values)
    assert len(valid)==3 and len(invalid)==8
    ordered=['clk2500-closure-episode-d3-95-d5-retention-20261002-white_v2-flat','clk2500-closure-episode-d3-84-d5-nominal-sdk-review','clk2500-closure-episode-d3-86-d6-gas-b1-world']
    valid,invalid=partition(ordered)
    assert valid==ordered[1:] and invalid==ordered[:1]
    print(json.dumps(dict(CPU_cases=12,actual_restricted_bridge_key_equivalent=True,invalid_queue_names_do_not_block_valid_jobs=True,no_GPU_PPO_or_bridge_mutation=True)))

if __name__=='__main__':main()
