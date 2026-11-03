# 两案不是相同接触类型（只对既存TRAIN事实）

4605：1.99decision→2.00push，air onset2.1225/confirmedPOST2.1425；2.4765左轮落GROUND（7286.789N），2.497guide05首次碰bar011顶面（合6330.002554N，n向robot=[0,0,1]）；随后guide07同bar顶面。guide两段各2ticks、hard0，首guide pitch−11.956934deg/rootPREz.260676492m。
4606：1.85decision→1.86push，air onset1.9915/confirmedPOST2.0115；2.3385首次ANYbar和operationalfirstlanding是chassis_front→bar011斜侧/上棱（17782.781376N，point[1.8369943,.1377360,.0599669]、n向robot=[.6484461,0,.7612606]），并非主轮landing。main=[0,0]、pitch−49.499091deg/rootPREz.337597667m，hard连续5ticks；2.3885 guide07再撞GROUND（10659.692721N，pitch−39.003665deg/rootPREz.288170622m），guide分3+2ticks。
两案mainfirstflightrear=2.446/2.218均非空，但随后分别guide/bar顶与body/bar棱+guide/地接触，不能升级整机器人净跨。两案不同DRseed，不是单变量干预；不解释为同一故障或已证某K/ref唯一原因。
初事件均在capture开始后、observer恢复和2.50刹车之前（实际capture4605/4606=2.39/2.26，restore=2.64/2.50）；故后来observer恢复/刹车不是这些初事件的前因。真实landing_ref/weight见EVENTS，legacytarget不冒当前ref。正文air_confirm行是该确认row的stage，本注与EVENTS给confirmedPOST，二者差.0005s。
原localFalse、guide/hard4/0与5/5、endstable原值不改；0新physics/编译/Git/agent/rawhash/H5/mesh，D1/D2 q未积分，2k单腿q未知。四raw各一次，后续只读已派生EVENTS，PH7pending。
