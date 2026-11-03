# R60 fresh TRAIN4605/4606 contact audit（offline only）

四raw路径与方法/小源SHA先锁；各trace/physics仅stream一遍，producerSHA沿用。没有D1/D2 q积分/控制/拟合/physics/Git/新agent/H5/heldout/mesh/rawhash。

## r60_tall0_fresh_RM_DR_4605
原gate=False; guide/hard ticks=4/0; endstable=4.659999999999945; firstflightmainrear=2.445999999999984（非整机器人净跨）。
|event|stage/control s|rootPREz m|pitch deg|main L/R, guide, hard N|
|---|---:|---:|---:|---|
|decision|1.99|—|—|100Hz loggedphase/flags; not2kpose|
|push|2|—|—|100Hz loggedphase/flags; not2kpose|
|capture|2.39|—|—|100Hz loggedphase/flags; not2kpose|
|Kffref_weight>0|2.4|—|—|100Hz loggedphase/flags; not2kpose|
|observer_reenable|2.64|—|—|100Hz loggedphase/flags; not2kpose|
|anybar>1|2.497|0.260676492|-11.9569342|[316.64808144912905, 751.0743094532581], 6330.00255, 0|
|air_onset|2.1225|0.362168195|0.497099791|[0.0, 0.0], 0, 0|
|air_confirm|2.142|0.396264828|0.0768760836|[0.0, 0.0], 0, 0|
|landing|2.4765|0.293669156|-13.0451087|[7286.788993200169, 0.0], 0, 0|
|guide_first|2.497|0.260676492|-11.9569342|[316.64808144912905, 751.0743094532581], 6330.00255, 0|
|guide_peak|2.497|0.260676492|-11.9569342|[316.64808144912905, 751.0743094532581], 6330.00255, 0|
|guide_last|2.499|0.258412601|-11.3910012|[0.0, 697.4969838528604], 114.602941, 0|
guide/hard segment first/peak/last/force/contactsurface和邻近100Hz实际landing_ref4/weight/observer详EVENTS；legacytarget不冒currentref，2k单腿q未知。

## r60_tall0_fresh_RM_DR_4606
原gate=False; guide/hard ticks=5/5; endstable=4.239999999999954; firstflightmainrear=2.217999999999908（非整机器人净跨）。
|event|stage/control s|rootPREz m|pitch deg|main L/R, guide, hard N|
|---|---:|---:|---:|---|
|decision|1.85|—|—|100Hz loggedphase/flags; not2kpose|
|push|1.86|—|—|100Hz loggedphase/flags; not2kpose|
|capture|2.26|—|—|100Hz loggedphase/flags; not2kpose|
|Kffref_weight>0|2.27|—|—|100Hz loggedphase/flags; not2kpose|
|observer_reenable|2.5|—|—|100Hz loggedphase/flags; not2kpose|
|anybar>1|2.3385|0.337597667|-49.4990914|[0.0, 0.0], 0, 17782.7814|
|air_onset|1.9915|0.383969391|-2.44791845|[0.0, 0.7219586810985837], 0, 0|
|air_confirm|2.011|0.418796243|-5.89324537|[0.0, 0.0], 0, 0|
|landing|2.3385|0.337597667|-49.4990914|[0.0, 0.0], 0, 17782.7814|
|guide_first|2.3885|0.288170622|-39.0036649|[0.0, 0.0], 10659.6927, 0|
|guide_peak|2.3885|0.288170622|-39.0036649|[0.0, 0.0], 10659.6927, 0|
|guide_last|2.391|0.286489624|-38.1890595|[813.207496536447, 0.0], 2.56015664, 0|
|hard_first|2.3385|0.337597667|-49.4990914|[0.0, 0.0], 0, 17782.7814|
|hard_peak|2.3385|0.337597667|-49.4990914|[0.0, 0.0], 0, 17782.7814|
|hard_last|2.3405|0.3360716|-49.0148451|[0.0, 0.0], 0, 3.30623988|
guide/hard segment first/peak/last/force/contactsurface和邻近100Hz实际landing_ref4/weight/observer详EVENTS；legacytarget不冒currentref，2k单腿q未知。

两案分别报告，不从单一时序推独一机制；bar/top/front-edge按实存normal/point区分，guide不冒main支持，positive force点数与>1N物理row不同。完整源前后SHA/原计数核对见RECEIPT；仅PH7pending诊断，原失败不改。
