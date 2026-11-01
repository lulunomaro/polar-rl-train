from pathlib import Path
import ast,json,shutil,time
O=Path(__file__).resolve().parent;N=O.parent/'REFERENCE_TRACKING_BPTT_V296_20261101';N.mkdir(exist_ok=False);(N/'reports').mkdir()
for name in('tracking_reference295.py','tracking_learner295.py','tracking_wm295.py','prepare295_source.py'):
    text=(O/name).read_text('utf8').replace('295','296')
    if name.startswith('tracking_reference'):
        text=text.replace("float(r['support_wheels']==2)","float(r['support_wheels'])/2.")
        text=text.replace("    assert all(r['support_wheels']in(0,2)for r in selected),'Actual two-wheel support labels required; no inferred asymmetric support'", "    assert all(r['support_wheels']in(0,1,2)for r in selected)")
        text=text.replace("support_label='actual support_wheels=0or2 in retained source; both supported flags; top-vsground via planned wheel location'", "support_label='actual supported-wheel count/2 in repeated scalar goal slots; partial support is aggregate, no individual identity inferred'")
        text=text.replace("errors['support']=(supported-label['support']).square().mean(-1)","errors['support']=((supported.sum(-1)-label['support'].sum(-1))/2.).square()")
    if name.startswith('tracking_learner'):
        text=text.replace("context[:,31:]/context.new_tensor(DEPTH_SCALE)","b.data['xi'][rows,envs,31:]/context.new_tensor(DEPTH_SCALE)")
    p=N/name.replace('295','296');p.write_bytes(text.encode());ast.parse(text)
with (N/'reports/SOURCE296_ORIGINAL295_SUPPORT_FALSE_AND_REPAIR.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),original295='Saved teacher includes valid one-wheel support; premature0or2-onlyassert rejected before referencepack/SDK/model.',repair='Use exact measured aggregate supportcount; do not infer missing perwheel identity. Compare predicted total support. Actual start actor depth uses current raw packet, remembered support only WM context.',oldsource=str(O),modelreads=0,SDK=0,GO=0),f,indent=2)
print(json.dumps(dict(passed=True,newroot=str(N))))
