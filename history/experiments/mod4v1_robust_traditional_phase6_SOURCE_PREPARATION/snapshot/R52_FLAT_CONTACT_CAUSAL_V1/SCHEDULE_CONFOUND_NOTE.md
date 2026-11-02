# 同时发生的命令变化与因果边界

R52配置brake_at_s=2.5：原runner在control2.50将forward命令.9→0；V3 K/nominalff/ref插值同在control2.50首次weight>0。因此2.537guide既在landing2.464之后，也在capture2.49/首weight2.50之后，但不能由这个singleTRAINcase把作用唯一分给K、ff、ref或刹车。

firstguide是guide06→GROUND、7059.476610N，而main=[0,0]；此时captureweight.104，observer仍disabled直到2.64。实际stage pitch14.667222deg/rootPREz.213525586m，100Hz encoder只bracket，actual单腿2kq未重建。capture中的legacytarget不是当前V3ref。

此补注只基于已分析配置/原runner语义与现有DETAILS，不再次读raw、不选择R53参数、不改任何源/门槛/分数。报告+receipt+本注<70行，PH6pending。
