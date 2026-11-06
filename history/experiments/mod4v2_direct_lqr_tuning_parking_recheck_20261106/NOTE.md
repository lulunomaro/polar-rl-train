# Direct human-requested LQR tuning, parking improvement and actual +/-2m/s benchmark

2026-11-06 14:18 human explicitly complained of excessive audit loops and requested actual tuning. This stage changed REAL DARe-solved gains/legparameters and ran6new fullCAD DRclosedloops plus2nominal28sfullrobotflatbenchmarks. NoobserverE1retuning/newaudits/replay/rootteacher/newagents/GPU/SSH/PPO/deps/hardwareflash. OriginalP0c19asset/300N60mm/k2000d3unmeasured/cylinder.0625/.01guides.015/.9/6connect4mimic/31robotbody+world/100Hz-.5msNewton100/PD-targetD4-currentPD-signedDC-gain-sameDC/gatesunchanged. Newconfig results retained,old3FFfailures/E1data not erased.

Fixednew530300training:baseline vs Qpitchrate4/Qvelocity2.25 actualKmaxdiff16.0651 vs sameLQRwithdifferentialKP90KD6;bothworsenedfixedscore/pitchRMS,notadopted. ThirdandFINALchangedgaincandidate R4(oldQ/leg120-4)predeclaredafterthosefailures;same trainingepisode/newdistinctgaincase,notbaseline replay. R4score2.67693vs2.80886=4.697%better but BELOWold5%selectionrule;old not-selected conclusion preserved. It did restoreoriginalstopgate.053773->.045809m/s,thereforea separatelydeclarednew530301DIAGNOSTIC parkingrecheck—notretroactivewinner—heldR4fixed. RechecksameDR/initialqpos:stop.065334->.054786(16.145%better),score2.98760->2.69147;pitch/rollbetter,velocitytracking slightlyworse. Stilloriginalstop>.05/wholepositive-lowpoints/strictCADscreensfalse,no scope widening. Trainingwhole2->5,recheck24->17. Source scope recheck bothtrue,trainingbothfalse retained. Noautomaticformaldefault/reliability/T01qualification.

ActualcompleteP0nominal EXTRA longflatfixture baseline/R4each28s2800controls56000physics:command+2,brake,-2,brake;baselineactualmeans+2.05033/-2.05044,R4+2.06345/-2.06365. StopRMSbase.012271/.012024,R4.012393/.012127. Allcomplete/noreset/fall. Originalbetterinnominalspeedfixture,soR4isparkingprioritytrialnotuniversalreplacement. Explicitnot latestCAD/T02acceptance/DRproof. Existingflatmodelbranchpurpose relabelledinbenchmarkmeta,notpretendinglinearizationorwholearena. CSVactualqpos37recorded100Hz,nocontinuous-sweep/hardwareproof.

Exported parking trial recipe actualKreference plusoptincontroller factory with EXACTtestedbaseP25settings(defaultposition25 etc),R4re-solvedonnewv2dynamics,shareddefaultruntimeunchanged. NoMPCchangeclaimed. New8closedloop256000physics. OldunarchivedR31threecompletecase receipts/source also includedwithoutreplay:nominalE1standpass/520211D3=10msnewpairrollimprovesbutwhole4->14worse,bothstrictfail/scopeTrue,E1notdefault. OldR31once/newrawbudgetsretained;not pretending R31 was previouslycommitted.

Goalgetat14:19revision30paused/disarmed31/40;resumeinterface requiresuser,notclaimedactive/noalternateGoal. Currentdirecthumanrequestexecuted. Allcase failures/unchanged originalgates persist. Large27CADraw+2flatCSV/sourceassetspathsize/existingproducerSHAorunknownONLY,NOarchivalpayloadhash/read. Snapshotnotstandaloneassets;olderpendingstatesretain. Actualsmall summary:

{
  "training_score_ratio": 0.9530300265488022,
  "training_fixed5percent_selection_met": false,
  "independent_recheck_score_ratio": 0.9008775877215028,
  "parking_relative_reductions": [
    0.14811417488297562,
    0.16144698642389743
  ],
  "additional_DR_parameter_settings": 2,
  "full_CAD_simulations": 6,
  "full_CAD_controls": 7200,
  "full_CAD_physics": 144000,
  "flat_simulations": 2,
  "flat_physics": 112000,
  "adopted_as_formal_default": false,
  "parking_priority_trial": {
    "effort_weight": 4.0
  },
  "all_original_failures_retained": true,
  "note": "R4 parking improvement reproduced on second setting,butstrictCADscreen not complete;initial5percenttrainingrule stillUNMET. Flat2m/s is extra fixture notCADqualification.",
  "raw_reads": 0,
  "extra_model_or_physics_or_old_QA": 0
}