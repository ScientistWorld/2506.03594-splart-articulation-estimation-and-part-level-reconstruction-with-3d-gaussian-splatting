| method | status | R* | success_rate | axis_error_deg | pivot_error | rotation_error_deg | translation_error | psnr | part_miou | depth_mae | cd_static | cd_mobile | cd_whole |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| better_color_geom | ok | +0.678 | 0.8846 | 1.084 | 0.0003812 | 1.848 | 0.003108 | 36.24 | 0.7712 | 0.1377 | 0.07994 | 0.1156 | 0.07141 |
| ablation_no2a | ok | +0.638 | 0.8846 | 0.8976 | 0.0005036 | 1.314 | 0.006931 | 34.73 | 0.75 | 0.14 | 0.08212 | 0.1188 | 0.07193 |
| paper_lambda_geom | ok | +0.431 | 0.8462 | 0.9454 | 0.0005175 | 2.366 | 0.007416 | 33.38 | 0.7193 | 0.1775 | 0.08683 | 0.1206 | 0.07669 |
| search_more | ok | +0.197 | 0.8077 | 1.285 | 0.0004651 | 2.338 | 0.0069 | 31.85 | 0.6856 | 0.2151 | 0.09218 | 0.1286 | 0.08339 |
| duplicate_files | ok | +0.000 | 0.7692 | 1.425 | 0.000563 | 3.291 | 0.007269 | 31 | 0.6544 | 0.2524 | 0.09689 | 0.1273 | 0.08846 |
| splart | ok | +0.000 | 0.7692 | 1.425 | 0.000563 | 3.291 | 0.007269 | 31 | 0.6544 | 0.2524 | 0.09689 | 0.1273 | 0.08846 |
| splart_seed1 | ok | -0.148 | 0.7308 | 1.321 | 0.0005958 | 3.325 | 0.009911 | 30.07 | 0.6268 | 0.2895 | 0.1022 | 0.1306 | 0.09397 |
| splart_seed2 | ok | -0.151 | 0.7308 | 1.12 | 0.004081 | 3.122 | 0.01008 | 30.31 | 0.621 | 0.2893 | 0.1024 | 0.1371 | 0.09421 |
| ablation_no2b | ok | -0.452 | 0.6923 | 1.857 | 0.0002825 | 2.559 | 0.02131 | 29.12 | 0.5932 | 0.3278 | 0.1088 | 0.1364 | 0.1001 |
| all_static_masks | ok | -0.657 | 0.7692 | 1.425 | 0.000563 | 3.291 | 0.007269 | 23.77 | 0.4201 | 0.3513 | 0.1246 | 0.2 | 0.08846 |
| weaker_short | ok | -0.699 | 0.6154 | 1.53 | 0.007896 | 4.28 | 0.01464 | 27.57 | 0.5352 | 0.4025 | 0.1073 | 0.1361 | 0.1019 |
| ablation_no3b | ok | -0.827 | 0.6923 | 2.699 | 0.01466 | 4.06 | 0.02149 | 26.6 | 0.5815 | 0.339 | 0.1055 | 0.1339 | 0.09954 |
| faint_gaussian_grid | ok | -0.913 | 0.7692 | 1.425 | 0.000563 | 3.291 | 0.007269 | 16.12 | 0.3857 | 0.6564 | 0.1794 | 0.1273 | 0.1588 |
| missing_half_scenes | incomplete: 13 scenes missing | -2.266 | 0.4231 | 3.123 | 0.03931 | 8.408 | 0.01519 | 21.1 | 0.3426 | 0.5888 | 0.1435 | 0.1671 | 0.1385 |
| ablation_no3a | ok | -4.108 | 0.07692 | 4.726 | 0.03722 | 9.119 | 0.04603 | 12.12 | 0.06016 | 0.927 | 0.189 | 0.1914 | 0.189 |
| icp_baseline | ok | -4.269 | 0.03846 | 4.747 | 0.03374 | 8.859 | 0.04941 | 10.59 | 0.02856 | 0.9672 | 0.1954 | 0.1963 | 0.1941 |
| icp_bruteforce | ok | -4.468 | 0 | 4.831 | 0.03722 | 9.399 | 0.04941 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| forged_score_files | ok | -4.508 | 0 | 4.815 | 0.03892 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| static_baseline | ok | -4.508 | 0 | 4.815 | 0.03892 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| empty_method_dir | failed: no predictions for this slice | -4.620 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| impossible_opacity_one_scene | failed: test_000: static_opacities: non-finite values | -4.620 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| nan_axis_one_scene | failed: test_000: axis: non-finite values | -4.620 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| pickled_payload | failed: test_000: unreadable prediction file: ValueError | -4.620 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| too_many_gaussians | failed: test_000: 20818 Gaussians > limit 20000 | -4.620 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |

## Train slice

| method | success_rate | axis_error_deg | pivot_error | rotation_error_deg | translation_error | psnr | part_miou | depth_mae | cd_static | cd_mobile | cd_whole |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ablation_no2a | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| ablation_no2b | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| ablation_no3a | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| ablation_no3b | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| better_color_geom | 0.8889 | 0.7761 | 0.002499 | 2.24 | 0.0014 | 35.92 | 0.7482 | 0.136 | 0.07662 | 0.1152 | 0.06961 |
| icp_baseline | 0.1667 | 4.636 | 0.02874 | 7.269 | 0.05 | 12.62 | 0.1203 | 0.8677 | 0.1772 | 0.1786 | 0.1734 |
| icp_bruteforce | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| paper_lambda_geom | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| search_more | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| splart | 0.8889 | 0.7978 | 0.003194 | 2.355 | 0.001369 | 34.6 | 0.7297 | 0.1364 | 0.07714 | 0.1168 | 0.06945 |
| splart_seed1 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| splart_seed2 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| static_baseline | 0 | 4.832 | 0.03168 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| weaker_short | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |

## Seed spread (max - min over seeds 0,1,2)

```
{
 "articulation_estimation.success_rate": 0.03846153846153855,
 "articulation_estimation.axis_error_deg": 0.3042849498785345,
 "articulation_estimation.pivot_error": 0.0035182438161145187,
 "articulation_estimation.rotation_error_deg": 0.20307076249104483,
 "articulation_estimation.translation_error": 0.002813342838885469,
 "part_reconstruction.psnr": 0.9350764585143629,
 "part_reconstruction.part_miou": 0.03341317443881697,
 "part_reconstruction.depth_mae": 0.03711512101323233,
 "part_reconstruction.cd_static": 0.005495071390342429,
 "part_reconstruction.cd_mobile": 0.009832561789437977,
 "part_reconstruction.cd_whole": 0.005751861821186879,
 "rank": 0.15094392149555275
}
```

## Paired vs reference (test scenes)

```
{
 "icp_baseline": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 19
 },
 "static_baseline": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 20
 },
 "ablation_no2a": {
  "n": 26,
  "success_gained": 3,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": 0.282388139945329,
   "se": 0.31219005531506955,
   "n": 20
  },
  "raw_depth_mae": {
   "mean_diff": -0.00011062596427796091,
   "se": 0.0006645266294841188,
   "n": 20
  },
  "raw_part_miou": {
   "mean_diff": 6.023636524982723e-05,
   "se": 0.005932058545146376,
   "n": 20
  },
  "raw_cd_whole": {
   "mean_diff": -0.00013523992958311241,
   "se": 0.00019969012363526124,
   "n": 20
  },
  "axis_error_deg": {
   "mean_diff": -0.08147053714824863,
   "se": 0.06544935774531492,
   "n": 20
  }
 },
 "ablation_no2b": {
  "n": 26,
  "success_gained": 2,
  "success_lost": 4,
  "raw_psnr": {
   "mean_diff": -0.15735060604739193,
   "se": 0.34532086227505177,
   "n": 16
  },
  "raw_depth_mae": {
   "mean_diff": 0.0008147234231297962,
   "se": 0.0007131522227583465,
   "n": 16
  },
  "raw_part_miou": {
   "mean_diff": -0.002622342168469058,
   "se": 0.004592931134005165,
   "n": 16
  },
  "raw_cd_whole": {
   "mean_diff": -0.0012202550938748575,
   "se": 0.0002865447821771671,
   "n": 16
  },
  "axis_error_deg": {
   "mean_diff": 0.02022687055578145,
   "se": 0.01871835843165603,
   "n": 16
  }
 },
 "ablation_no3a": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 18,
  "raw_psnr": {
   "mean_diff": 0.48401105011824797,
   "se": 0.8388284959038258,
   "n": 2
  },
  "raw_depth_mae": {
   "mean_diff": 0.02158609267017878,
   "se": 0.013460223131027564,
   "n": 2
  },
  "raw_part_miou": {
   "mean_diff": -0.0018279069191158848,
   "se": 0.006129916174890837,
   "n": 2
  },
  "raw_cd_whole": {
   "mean_diff": 0.0014016824049444994,
   "se": 0.0007533507616488307,
   "n": 2
  },
  "axis_error_deg": {
   "mean_diff": 1.4302396888462954,
   "se": 1.2352754347594903,
   "n": 2
  }
 },
 "ablation_no3b": {
  "n": 26,
  "success_gained": 1,
  "success_lost": 3,
  "raw_psnr": {
   "mean_diff": -3.598967661803669,
   "se": 0.6613613804870079,
   "n": 17
  },
  "raw_depth_mae": {
   "mean_diff": 0.01695694688595216,
   "se": 0.0018076166725893388,
   "n": 17
  },
  "raw_part_miou": {
   "mean_diff": -0.026288137261807905,
   "se": 0.004298968489942789,
   "n": 17
  },
  "raw_cd_whole": {
   "mean_diff": -0.0011261019414954786,
   "se": 0.00053504151248073,
   "n": 17
  },
  "axis_error_deg": {
   "mean_diff": 1.43687947114426,
   "se": 0.22092261541981317,
   "n": 17
  }
 },
 "better_color_geom": {
  "n": 26,
  "success_gained": 3,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": 2.1548257141327762,
   "se": 0.4592393727685557,
   "n": 20
  },
  "raw_depth_mae": {
   "mean_diff": -0.002839954374404585,
   "se": 0.0007904592557493251,
   "n": 20
  },
  "raw_part_miou": {
   "mean_diff": 0.02342423075503494,
   "se": 0.006131562231678807,
   "n": 20
  },
  "raw_cd_whole": {
   "mean_diff": -0.0004162198996102796,
   "se": 0.00015355316854012862,
   "n": 20
  },
  "axis_error_deg": {
   "mean_diff": -0.05927668501859977,
   "se": 0.06157457325783953,
   "n": 20
  }
 },
 "icp_bruteforce": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 20
 },
 "paper_lambda_geom": {
  "n": 26,
  "success_gained": 2,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": -0.10449881576145881,
   "se": 0.3020178554803526,
   "n": 20
  },
  "raw_depth_mae": {
   "mean_diff": 0.0003183824456587965,
   "se": 0.0007940725619971664,
   "n": 20
  },
  "raw_part_miou": {
   "mean_diff": 0.005980906772396777,
   "se": 0.004676955779500951,
   "n": 20
  },
  "raw_cd_whole": {
   "mean_diff": -0.0004473600740053811,
   "se": 0.00016546901025375586,
   "n": 20
  },
  "axis_error_deg": {
   "mean_diff": -0.041348933261910026,
   "se": 0.054410234480332186,
   "n": 20
  }
 },
 "search_more": {
  "n": 26,
  "success_gained": 2,
  "success_lost": 1,
  "raw_psnr": {
   "mean_diff": -0.06605772803045963,
   "se": 0.27819670569208343,
   "n": 19
  },
  "raw_depth_mae": {
   "mean_diff": -0.00014706418478426184,
   "se": 0.0007001613039550689,
   "n": 19
  },
  "raw_part_miou": {
   "mean_diff": -0.006723696781854501,
   "se": 0.0045821211126544515,
   "n": 19
  },
  "raw_cd_whole": {
   "mean_diff": 0.00019554223353552237,
   "se": 0.00021167009931945022,
   "n": 19
  },
  "axis_error_deg": {
   "mean_diff": -0.050932449260613404,
   "se": 0.0462765962506934,
   "n": 19
  }
 },
 "splart_seed1": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 1,
  "raw_psnr": {
   "mean_diff": 0.06659489115933924,
   "se": 0.2771829905718328,
   "n": 19
  },
  "raw_depth_mae": {
   "mean_diff": -0.00010340654271266407,
   "se": 0.0006130992982584795,
   "n": 19
  },
  "raw_part_miou": {
   "mean_diff": 0.0006365957592370359,
   "se": 0.004396221517824176,
   "n": 19
  },
  "raw_cd_whole": {
   "mean_diff": -0.0005019420407534398,
   "se": 0.00017664850846134072,
   "n": 19
  },
  "axis_error_deg": {
   "mean_diff": 0.090653814960031,
   "se": 0.07883895040644215,
   "n": 19
  }
 },
 "splart_seed2": {
  "n": 26,
  "success_gained": 1,
  "success_lost": 2,
  "raw_psnr": {
   "mean_diff": 0.2563611941531282,
   "se": 0.33505593455005056,
   "n": 18
  },
  "raw_depth_mae": {
   "mean_diff": -0.00028231058605399084,
   "se": 0.0007171137560485741,
   "n": 18
  },
  "raw_part_miou": {
   "mean_diff": 0.006513002218200799,
   "se": 0.004594799022988819,
   "n": 18
  },
  "raw_cd_whole": {
   "mean_diff": -0.0003216113797832471,
   "se": 0.00030495498995303596,
   "n": 18
  },
  "axis_error_deg": {
   "mean_diff": -0.07037482130832251,
   "se": 0.08825336829745825,
   "n": 18
  }
 },
 "weaker_short": {
  "n": 26,
  "success_gained": 1,
  "success_lost": 5,
  "raw_psnr": {
   "mean_diff": 1.7214993966486476,
   "se": 0.6760497393488305,
   "n": 15
  },
  "raw_depth_mae": {
   "mean_diff": 6.631306252704502e-05,
   "se": 0.0016942417929772006,
   "n": 15
  },
  "raw_part_miou": {
   "mean_diff": 0.021807612383338837,
   "se": 0.004981515519790329,
   "n": 15
  },
  "raw_cd_whole": {
   "mean_diff": -0.015129971694917702,
   "se": 0.0011466594942782145,
   "n": 15
  },
  "axis_error_deg": {
   "mean_diff": 0.0008550547115263678,
   "se": 0.09389172522534396,
   "n": 15
  }
 },
 "all_static_masks": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": -9.406514651093516,
   "se": 1.2209256101131603,
   "n": 20
  },
  "raw_depth_mae": {
   "mean_diff": 0.12852554305646502,
   "se": 0.020519679909731012,
   "n": 20
  },
  "raw_part_miou": {
   "mean_diff": -0.30457396985286916,
   "se": 0.031502446040639315,
   "n": 20
  },
  "raw_cd_whole": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 20
  },
  "axis_error_deg": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 20
  }
 },
 "duplicate_files": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 20
  },
  "raw_depth_mae": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 20
  },
  "raw_part_miou": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 20
  },
  "raw_cd_whole": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 20
  },
  "axis_error_deg": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 20
  }
 },
 "faint_gaussian_grid": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": -19.34445318768551,
   "se": 0.8261622574512817,
   "n": 20
  },
  "raw_depth_mae": {
   "mean_diff": 0.5252430305900487,
   "se": 0.025906802455197428,
   "n": 20
  },
  "raw_part_miou": {
   "mean_diff": -0.34922052003043635,
   "se": 0.029204457460759933,
   "n": 20
  },
  "raw_cd_whole": {
   "mean_diff": 0.09142766357296216,
   "se": 0.009160728049365477,
   "n": 20
  },
  "axis_error_deg": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 20
  }
 },
 "forged_score_files": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 20
 },
 "missing_half_scenes": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 9,
  "raw_psnr": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 11
  },
  "raw_depth_mae": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 11
  },
  "raw_part_miou": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 11
  },
  "raw_cd_whole": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 11
  },
  "axis_error_deg": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 11
  }
 }
}
```
