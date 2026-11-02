# Continue independent MOD4v1 robust LQR/MPC — active goal, not complete

## Goal and scope

Goal `goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d` last queried revision4/active/armed, max12rounds. Direct human last said继续任务. Workroot F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102; sessioncwd F:/RMPOLAR-RL. Keepgoalactive; nohardwareflashing/otherexpertjobs. Skills catalog onlyOffice/ACL, nonefitrobotcontrol; filesystem/CLI/tools used.

## Authoritative model and clocks

Primary [MJCF](<MODEL_AUDIT/mod4v1_usd_source_aligned.xml>) SHA`0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324`, actualUSD`2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3`; mass14.294140288606286kg, robot31body/nq37/nv36/nu6,6connect+4mimic,311robotgeom/279meshes. [Audit](<MODEL_AUDIT/MODEL_ALIGNMENT.md>) and [receipt](<MODEL_AUDIT/USD_SOURCE_DERIVATION_RECEIPT.json>) preserveallengine/contractconflicts. Not oldthreeMCI/preliminarycylinder. Newtireactual48point/92triangle convexhulls,24radialfacets, circumradius~.0637 isnotallorientation verticalsupportheight; initializationuses[exactmeshhelper](<MODEL_AUDIT/mesh_support_helper_v1/mesh_support.py>). Physics.0005s implicitfast/Newton100; control100Hz; latestsensorbridge2kHzwindowing→D1noise→100Hz sharedD3. NotPhysX2.5ms/TGS/RL50Hz.

Motors DM8009P×4, DM3519+replacementtotal15.8:1×2, notSPR3508. MJCFgear1 meanswheel-end torquealreadyreflected. Hardwarewheelrnom.0625 vsCADmesh.0637 separated. DJI Cboard OR Damiaoboard stillunbound; SPRreferenceisDM02/H723chassis+C/F407gimbal, notselectedtarget.

## Actual completed physical work

ThroughR04 [62casefacts](<reports/through_r04_62_case_facts.json>):976000physicssteps/48800controls,62complete,36fullDRcases,4explicittruthdiagnostics,0holdout. R05adds27newfullDRconfigablationcases, allcompleted: total89cases/1408000physicssteps/70400controls,63fullDR/26nominal; do notcombineheterogeneousprofilesintoacceptancerate.

- R00 sensor-onlynominalstand6s complete, drift.0649m. FullDR101/102bothD3=10ms complete6s. Firstforward2.613m/sbadtracking; firstspin.613rad/s/3.18mdriftfailed. Originals retained.
- R01 highrateIMUwindow/exactinit/yawdecouple improvedforward butold14statelegcontrolsplitstronglyduringyaw, hipsatlimits. R02 fixedlegposePID allowed~10rad/s butbadinitialaccelerometerpriorcaused~.17radbias. All failures retained.
- R03 explicitSUPPORTEDUPRIGHTarmingprior (not arbitraryinitattitudepass), innovation-gatedattitude, fixedleg120/4, longitudinalwheelLQR, yawPI(.8/.5,Ilimit15, rateFF.052), gyro/encodercoherentwindow. Nominalforward2.004531m/s/RMSE.0170; spin_gated12.592855rad/s/11.7577turnsin8s/xy.1755m, spin_gyro12.555009/xy.0430m. No worldtruthcontrol inthese; 4truthdiagnosticsnevercountreleasequalification. FullDR101forward1.9865/RMSE.0211.
- R04TRAIN201..20832cases: all32complete; stand8/8screen,forward5/8,spin_gated2/8,spin_gyro3/8. D3strata7delay10ms+1zero persubgroup. Mainspin failurexy>.3m(.4.. .8m), althoughyawrate~4pi, notfalls. Forwardbias/steadystateerrorsstillneedwork. [Results](<batches/r04_train_32/BATCH_RESULT.json>).
- R05 pairedTRAINfailseeds203/205/208, changedQpos/leash only: p25+leash1normalstand3/3 andforward3/3, p10/p10v4forward2/3. ALL9spinvariantsfailed, strongerpositiongainworsenedspin. Do notjustkeepincreasingQposforgyro. [Results](<batches/r05_position_27/BATCH_RESULT.json>).
- No independentholdout yet;10000..10063reserved andunused. No newmodelRMrough/270stepphysicalqualification, noARM/board/HIL, no newmodelMPCclosedloopqualificationyet.

## Current source and diagnostics

Current [runner](<run_ground_case_v5.py>) imports [sensorV4](<sensor_core_v4.py>),[controllerV4](<ground_controller_v4.py>),[bridgeV3](<physics_bridge_v3.py>) +base [bridge](<physics_bridge.py>); uses [nominalgain](<nominal_gain_v1.json>) (14state, nominalDAREonly), and legacyread-only sources underF:/RMPOLAR-RL/traditional_control_20261101. R04/R05sources/configsfrozeninthebatches. V5streamsrawtraceSHAwhileproducingdata; do notreadrawmerelytohashforarchive.

[IndependentR00diagnosis](<DATA_DIAGNOSTIC/R00_DATA_DIAGNOSTIC.md>): norm-onlyaccfusionturneddynamicproperforceintogravity; forwardpitchRMSE.150vs.0052gyro-onlywithcorrectreset, notprincipallymissinggyrointegral. MuJoCoIMUframecheckpassed(noinertial-axisbugthisround). Gyro-onlynotuniversallybetterforoldspin. WheelKFupdatedevencontactproxy0andwaswildlyoverconfident. .5msstage-mixingconfirmedseparatelyfrom10msrowmetricmisalignment; fixallfieldtimestampsbeforefinalholdout. Latestmeanratewindowreducesaliasbutdoesnotmakecontact/slipobservable.

[Yawbias](<DATA_DIAGNOSTIC/YAW_NOMINAL_BIAS_NOTES.md>): oddwheelFF[-.0515228,+.0515228]*yawrateconsistentauthored.015wheelviscousdamping. Evenw²coefficientsfromoldfixedoriginchartareNOTexactpureCOMspinbalance; 4piresidualmax16.7Nm/lateralslip.43m/s, do notblindlyfeedassteady-stateoracle.

## Highest-value next work

1. Spinworlddrift: data-onlyinspectR04gyro203/205/208vs202. Comparetruebodyvywithencoder/gyrokinematicnoslipvy=−(omega×wheelmid_B)_y; integrate2Dworldodomfromestimatedyaw,vx,vy andcompareloggedrootxy. Currentonlyscalarforwarddistancecontrolcannotcenter2Dspinaxis. If2Dodomobservabledrift, addwheel-centeredworldpositionouterloopprojectedintobodyforwardcommand. Ifnot, implementlateralIMUKF/slip/contactadaptation; avoidtruthfeedbackandfakecovariance. RejectR05high-Qposspinregression.
2. Normaldrivingcandidatep25/leash1: remainingtrainseeds201,202,204,206,207notyettestedwithp25; reuseexisting3pairedfactswithoutreplaying. ExportACTUALderivedcontrollerK/weights beforeCport; nominalgainK isnotp25K.
3. BuildsmallgroundMPC: fixedlegPIDinAcl=A14+B14L_leg; symmetric8stateprojection[x,pitch,hipavg,deltaavg,v,pitchdot,hipdotavg,deltadotavg], commonwheelinputB=(BwheelL+BwheelR), ZOH. Option1-stepfractionalactuatorlagaugstate9, N15 scalarinputboxQP. Source old [linear_mpc.py](<../traditional_control_20261101/linear_mpc.py>) is14state/6inputN15anddoesnotmodelqueue; nofakeMPCflightclaims. Supervisor oninfeasible/deadline/KKTinvalid→independentLQR, countfallbackusage. Highspinoutsidefixedzero-yawmodelneedsLPVorLQRswitchclearlyreported.
4. Contact/flight/anomaly/FSM/power: onlygroundcontrollercurrentlybuilt. UseIMUproperforce+motorfeedback/nominalgas/J residual, notMuJoCocontacttruth. Contactproxyaloneisnotqualified. Addfull7modules andgoalstates, thenRMrough/270jumplandinit/launch/flight/footprintclearance/endhold withsameepisodeandoriginal0.5smetric+newend2sreported.
5. FreezeafterTRAINqualifies; runindependent≥64seeds/familywithD3/D4strata/Wilsonintervalsandfailures. Neverfitonholdout. Separate2m/sand4piskills; combined2+4pineedsouterwheel4.75m/sabove3.46..3.53noloadenvelope.
6. BoardBSP/IMUextrinsics/motorCANID/sign/unit/thermal/elecpowerremainunbound; do notflashorclaimBIN/HILdone. MechanicalpowerΣτwNOTbus/I²Rpower.

## C work and children (reuse, no proliferation)

- Agent`abf2088f-af10-479a-9108-202785031447`: sealed [portablecoreV1](<SPR_AUDIT/portable_core_v1/README.md>)18152hostchecks/0fail; sealed [kinematicsV2](<SPR_AUDIT/portable_core_v2_kinematics/README.md>)2761/0. GCC C:/MinGW/bin/gcc.exe GCC6.3mingw32. FixedsizeC99float32/noheap, notARMWCET. V1observatormathisFROZENR00, notcurrentV4physicalversion. State4/6arecrank-minus-hipNOTpassiveknee; parent[append-onlyschemaerratum](<reports/STATE14_SCHEMA_ERRATUM.md>)correctsREADMElabelwithoutrewritingsealedbytes. CkinematicsfiniteDifferenceepsf32~1e-3..2e-3muchbetterthan1e-5in52fixtures; keepconfigurableoranalyticallater.
- Sameagentcurrentlybuildingpure [boxQPdirectory](<SPR_AUDIT/portable_mpc_qp_v1/>)n<=16, SPDcheck/coordinateclip/KKT/fixedworkspace/deadlinecallback, independenthostunitonly. NotrobotHessianorMPCskillqualification. Collectcompletionandreview; reusefornextportoncePythonfrozen.
- Agent`e4e6c8f2-f08d-4df1-9150-945c804e8c2a`: model/helper/dataauditcompleted, currentlyPHASE1GitarchiveonindependentworktreeF:/RMPOLAR-RL/repo-lqr-robust, branchmod4v1-lqr-mpc-robust. Nevermodifyoriginalrepo-lqrbranchmod4v1-experts-fulldr-rm70/index/checkout/main. New--no-checkout+sparsegaveemptyindexstagedD307122; childfixedNEWindexviaread-treeHEADandmaterialized19policies/tools; originalsharedindexstatSHAchangesunattributed/otherlivework, donotrestoreit.
- Phase1archivecutoffR03plussealedCkinematicsV2andapprovedschemaerratum; allR04/R05/newreports/MPCactivephase2pending. Childauthorizedrecord_experimentidmod4v1-robust-traditional-phase1andpushOWNbranch+annotatedtagonly, verifyremoteownbranch/tag/peeled/mainunchanged. mainpre938b9ee8458f09a47e369995c8bfb1064b052a1f. Waitreceipt; noduplicateonce/recordifpushfails. Pendingallreportsmustbesupplementedlater, noforeveromission.

## Jobs and status at write

R00unit9/10failurepreservedthen10/10fixed; allphysicalR00..R05jobsfinishedandcollected. summarize_through_r04jobpwsh-aa0c57cc213b4c7cfinished/collected. Noactiveparentpwshjob. Twoabovechildrenstillworkingindependently. Goalnotcomplete/notblocked; continueworkandpreserveallrawfailures/report/sourceSHA. Userquestion15.8ratioansweredwithcurrentcontract/MJCFlineevidence; noidentity/preference/memorywriteback.
