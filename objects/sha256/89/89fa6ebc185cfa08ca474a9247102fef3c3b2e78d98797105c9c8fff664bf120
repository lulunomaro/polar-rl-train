import sys, json
from tensorboard.backend.event_processing import event_accumulator
path = sys.argv[1]
wanted = sys.argv[2].split(',') if len(sys.argv) > 2 else None
ea = event_accumulator.EventAccumulator(path, size_guidance={'scalars': 100000})
ea.Reload()
tags = ea.Tags()['scalars']
print('TAGS:', json.dumps(sorted(tags), ensure_ascii=False))
for t in sorted(tags):
    if wanted and not any(w in t for w in wanted):
        continue
    ev = ea.Scalars(t)
    pts = [(e.step, e.value) for e in ev]
    print('---', t, 'n=%d' % len(pts))
    step = max(1, len(pts)//25)
    print('  ', ' '.join('%d:%.5g' % p for p in pts[::step]))
    print('   last:', '%.6g @ %d' % (pts[-1][1], pts[-1][0]))
