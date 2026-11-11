| method | status | R* | success_rate | axis_error_deg | pivot_error | rotation_error_deg | translation_error | psnr | part_miou | depth_mae | cd_static | cd_mobile | cd_whole |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| better_color_geom | ok | +0.500 | 0.8846 | 0.9695 | 0.0004539 | 1.837 | 0.003697 | 36.05 | 0.7683 | 0.1383 | 0.07926 | 0.1139 | 0.07105 |
| ablation_no2a | ok | +0.442 | 0.8846 | 0.8976 | 0.0005036 | 1.314 | 0.006931 | 34.73 | 0.75 | 0.14 | 0.08212 | 0.1188 | 0.07193 |
| repeat_run_check | ok | +0.236 | 0.8462 | 0.9454 | 0.0005175 | 2.366 | 0.007416 | 33.38 | 0.7193 | 0.1775 | 0.08683 | 0.1206 | 0.07669 |
| splart_seed2 | ok | +0.058 | 0.8077 | 0.9699 | 0.0004466 | 2.451 | 0.0104 | 32.34 | 0.6916 | 0.2144 | 0.09247 | 0.124 | 0.08254 |
| duplicate_files | ok | +0.000 | 0.8077 | 1.259 | 0.0005046 | 2.297 | 0.01078 | 31.94 | 0.6902 | 0.2156 | 0.09229 | 0.1239 | 0.08297 |
| splart | ok | +0.000 | 0.8077 | 1.259 | 0.0005046 | 2.297 | 0.01078 | 31.94 | 0.6902 | 0.2156 | 0.09229 | 0.1239 | 0.08297 |
| splart_seed1 | ok | -0.002 | 0.8077 | 1.274 | 0.0004416 | 3.087 | 0.00669 | 32.04 | 0.6903 | 0.2151 | 0.09198 | 0.1245 | 0.08244 |
| scaled_lambda_geom | ok | -0.191 | 0.7692 | 1.425 | 0.000563 | 3.291 | 0.007269 | 31 | 0.6544 | 0.2524 | 0.09689 | 0.1273 | 0.08846 |
| search_more | ok | -0.375 | 0.7308 | 1.558 | 0.0003812 | 2.45 | 0.01396 | 29.96 | 0.6263 | 0.2911 | 0.1043 | 0.1286 | 0.09499 |
| all_static_masks | ok | -0.693 | 0.8077 | 1.259 | 0.0005046 | 2.297 | 0.01078 | 24.08 | 0.4419 | 0.3236 | 0.1222 | 0.2 | 0.08297 |
| weaker_short | ok | -0.917 | 0.6154 | 1.741 | 0.003408 | 3.882 | 0.01796 | 27.72 | 0.532 | 0.4024 | 0.1076 | 0.1404 | 0.1022 |
| faint_gaussian_grid | ok | -0.954 | 0.8077 | 1.259 | 0.0005046 | 2.297 | 0.01078 | 16.42 | 0.4063 | 0.6459 | 0.1785 | 0.1239 | 0.156 |
| ablation_no3b | ok | -1.129 | 0.6538 | 2.26 | 0.01231 | 5.147 | 0.02112 | 25.57 | 0.5484 | 0.3763 | 0.1115 | 0.1395 | 0.1052 |
| ablation_no2b | ok | -1.757 | 0.5 | 2.603 | 0.01255 | 5.226 | 0.02532 | 23.84 | 0.4291 | 0.5147 | 0.1346 | 0.1527 | 0.1279 |
| missing_half_scenes | incomplete: 13 scenes missing | -2.602 | 0.3846 | 3.093 | 0.03934 | 8.312 | 0.01862 | 19.9 | 0.3146 | 0.6269 | 0.1492 | 0.1665 | 0.144 |
| ablation_no3a | ok | -4.291 | 0.07692 | 4.711 | 0.03773 | 9.143 | 0.04601 | 12.12 | 0.05975 | 0.9279 | 0.1891 | 0.1912 | 0.189 |
| icp_baseline | ok | -4.451 | 0.03846 | 4.747 | 0.03374 | 8.859 | 0.04941 | 10.59 | 0.02856 | 0.9672 | 0.1954 | 0.1963 | 0.1941 |
| icp_bruteforce | ok | -4.648 | 0 | 4.831 | 0.03722 | 9.399 | 0.04941 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| forged_score_files | ok | -4.688 | 0 | 4.815 | 0.03892 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| static_baseline | ok | -4.688 | 0 | 4.815 | 0.03892 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| empty_method_dir | failed: no predictions for this slice | -4.800 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| impossible_opacity_one_scene | failed: test_000: static_opacities: non-finite values | -4.800 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| nan_axis_one_scene | failed: test_000: axis: non-finite values | -4.800 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| pickled_payload | failed: test_000: unreadable prediction file: ValueError | -4.800 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| too_many_gaussians | failed: test_000: 20817 Gaussians > limit 20000 | -4.800 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |

## Train slice

| method | success_rate | axis_error_deg | pivot_error | rotation_error_deg | translation_error | psnr | part_miou | depth_mae | cd_static | cd_mobile | cd_whole |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ablation_no2a | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| ablation_no2b | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| ablation_no3a | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| ablation_no3b | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| better_color_geom | 0.8889 | 0.9345 | 0.001772 | 2.753 | 0.00133 | 36.11 | 0.747 | 0.136 | 0.07673 | 0.1135 | 0.06931 |
| icp_baseline | 0.1667 | 4.636 | 0.02874 | 7.269 | 0.05 | 12.62 | 0.1203 | 0.8677 | 0.1772 | 0.1786 | 0.1734 |
| icp_bruteforce | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| repeat_run_check | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| scaled_lambda_geom | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| search_more | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| splart | 0.8889 | 0.7988 | 0.001483 | 2.374 | 0.00201 | 34.4 | 0.7337 | 0.1372 | 0.07742 | 0.1163 | 0.0695 |
| splart_seed1 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| splart_seed2 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| static_baseline | 0 | 4.832 | 0.03168 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| weaker_short | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |

## Seed spread (max - min over seeds 0,1,2)

```
{
 "articulation_estimation.success_rate": 0.0,
 "articulation_estimation.axis_error_deg": 0.3039883062038622,
 "articulation_estimation.pivot_error": 6.297848724417225e-05,
 "articulation_estimation.rotation_error_deg": 0.7902657415862038,
 "articulation_estimation.translation_error": 0.004087859902679525,
 "part_reconstruction.psnr": 0.4021150145436323,
 "part_reconstruction.part_miou": 0.0014293038901278532,
 "part_reconstruction.depth_mae": 0.0011982160913232287,
 "part_reconstruction.cd_static": 0.000496250114033342,
 "part_reconstruction.cd_mobile": 0.0005799570422174161,
 "part_reconstruction.cd_whole": 0.0005236625444205723,
 "rank": 0.05990513276824087
}
```

## Paired vs reference (test scenes)

```
{
 "icp_baseline": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 20
 },
 "static_baseline": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 21
 },
 "ablation_no2a": {
  "n": 26,
  "success_gained": 3,
  "success_lost": 1,
  "raw_psnr": {
   "mean_diff": 0.3620301904172999,
   "se": 0.31730970641412526,
   "n": 20
  },
  "raw_depth_mae": {
   "mean_diff": -2.631067643447168e-05,
   "se": 0.0006661966629502244,
   "n": 20
  },
  "raw_part_miou": {
   "mean_diff": 0.0006195439322771556,
   "se": 0.006963439299022925,
   "n": 20
  },
  "raw_cd_whole": {
   "mean_diff": 0.00046617830923083547,
   "se": 0.00017748843596267403,
   "n": 20
  },
  "axis_error_deg": {
   "mean_diff": -0.09469571552441428,
   "se": 0.06563080567071411,
   "n": 20
  }
 },
 "ablation_no2b": {
  "n": 26,
  "success_gained": 2,
  "success_lost": 10,
  "raw_psnr": {
   "mean_diff": 0.1940974768364505,
   "se": 0.4591485243763213,
   "n": 11
  },
  "raw_depth_mae": {
   "mean_diff": 0.0001767795153638586,
   "se": 0.0010329252144276554,
   "n": 11
  },
  "raw_part_miou": {
   "mean_diff": 0.007518401754022751,
   "se": 0.0036106420808390757,
   "n": 11
  },
  "raw_cd_whole": {
   "mean_diff": -0.0001256227814472574,
   "se": 0.0003787788736779374,
   "n": 11
  },
  "axis_error_deg": {
   "mean_diff": -0.13848326359259044,
   "se": 0.10504737431481906,
   "n": 11
  }
 },
 "ablation_no3a": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 19,
  "raw_psnr": {
   "mean_diff": 0.21739689971236587,
   "se": 0.907365687198446,
   "n": 2
  },
  "raw_depth_mae": {
   "mean_diff": 0.03310258597826798,
   "se": 0.017960452935180275,
   "n": 2
  },
  "raw_part_miou": {
   "mean_diff": -0.009092269178969159,
   "se": 0.00558125654737046,
   "n": 2
  },
  "raw_cd_whole": {
   "mean_diff": 0.002729400678179405,
   "se": 0.0006608105607410242,
   "n": 2
  },
  "axis_error_deg": {
   "mean_diff": 1.204348132247883,
   "se": 1.119324874691622,
   "n": 2
  }
 },
 "ablation_no3b": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 4,
  "raw_psnr": {
   "mean_diff": -3.392271091835824,
   "se": 0.6487500920356315,
   "n": 17
  },
  "raw_depth_mae": {
   "mean_diff": 0.017070613750210697,
   "se": 0.0022853324237661777,
   "n": 17
  },
  "raw_part_miou": {
   "mean_diff": -0.01993086492081763,
   "se": 0.006172253172925653,
   "n": 17
  },
  "raw_cd_whole": {
   "mean_diff": -0.0007332792576787449,
   "se": 0.0005046699776742326,
   "n": 17
  },
  "axis_error_deg": {
   "mean_diff": 1.043065394190381,
   "se": 0.15425391195589963,
   "n": 17
  }
 },
 "better_color_geom": {
  "n": 26,
  "success_gained": 4,
  "success_lost": 2,
  "raw_psnr": {
   "mean_diff": 2.077087155994572,
   "se": 0.5003842225549231,
   "n": 19
  },
  "raw_depth_mae": {
   "mean_diff": -0.0021101357950443593,
   "se": 0.0009893037737867228,
   "n": 19
  },
  "raw_part_miou": {
   "mean_diff": 0.017810256889840323,
   "se": 0.008092535741348631,
   "n": 19
  },
  "raw_cd_whole": {
   "mean_diff": -0.00027275279451541106,
   "se": 0.00015000074029513478,
   "n": 19
  },
  "axis_error_deg": {
   "mean_diff": -0.09588480798782802,
   "se": 0.08945541717975415,
   "n": 19
  }
 },
 "icp_bruteforce": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 21
 },
 "repeat_run_check": {
  "n": 26,
  "success_gained": 3,
  "success_lost": 2,
  "raw_psnr": {
   "mean_diff": -0.04693418479409392,
   "se": 0.27499659049463676,
   "n": 19
  },
  "raw_depth_mae": {
   "mean_diff": 0.00048059667278946993,
   "se": 0.0007963099034103514,
   "n": 19
  },
  "raw_part_miou": {
   "mean_diff": 0.004934496424644426,
   "se": 0.006624981129532305,
   "n": 19
  },
  "raw_cd_whole": {
   "mean_diff": 0.00011302859888236442,
   "se": 0.00018417616477922128,
   "n": 19
  },
  "axis_error_deg": {
   "mean_diff": -0.06393127230239624,
   "se": 0.07107267380509871,
   "n": 19
  }
 },
 "scaled_lambda_geom": {
  "n": 26,
  "success_gained": 1,
  "success_lost": 2,
  "raw_psnr": {
   "mean_diff": 0.036584630743213234,
   "se": 0.31212588591613555,
   "n": 19
  },
  "raw_depth_mae": {
   "mean_diff": 9.539487143020058e-05,
   "se": 0.0006041237948003062,
   "n": 19
  },
  "raw_part_miou": {
   "mean_diff": -0.0005344193500938013,
   "se": 0.006184538541333144,
   "n": 19
  },
  "raw_cd_whole": {
   "mean_diff": 0.0005791586260528936,
   "se": 0.00017194098025034575,
   "n": 19
  },
  "axis_error_deg": {
   "mean_diff": -0.0015591393400573926,
   "se": 0.02947836696301925,
   "n": 19
  }
 },
 "search_more": {
  "n": 26,
  "success_gained": 1,
  "success_lost": 3,
  "raw_psnr": {
   "mean_diff": -0.2239581215234906,
   "se": 0.3054691653499644,
   "n": 18
  },
  "raw_depth_mae": {
   "mean_diff": 0.0016881946358636465,
   "se": 0.0008389961905936936,
   "n": 18
  },
  "raw_part_miou": {
   "mean_diff": -0.0041466182873183205,
   "se": 0.005196893566579731,
   "n": 18
  },
  "raw_cd_whole": {
   "mean_diff": 0.0013828572134041255,
   "se": 0.00029354363696999466,
   "n": 18
  },
  "axis_error_deg": {
   "mean_diff": 0.0072331763522182945,
   "se": 0.06500706926072326,
   "n": 18
  }
 },
 "splart_seed1": {
  "n": 26,
  "success_gained": 3,
  "success_lost": 3,
  "raw_psnr": {
   "mean_diff": 0.07099009332518709,
   "se": 0.3119846461275586,
   "n": 18
  },
  "raw_depth_mae": {
   "mean_diff": 9.847373227969614e-05,
   "se": 0.000567860009538522,
   "n": 18
  },
  "raw_part_miou": {
   "mean_diff": 0.00016489094795824673,
   "se": 0.007559974653716959,
   "n": 18
  },
  "raw_cd_whole": {
   "mean_diff": 0.00013807335657608708,
   "se": 0.00018689859801549594,
   "n": 18
  },
  "axis_error_deg": {
   "mean_diff": 0.041605576978217526,
   "se": 0.059668817683960686,
   "n": 18
  }
 },
 "splart_seed2": {
  "n": 26,
  "success_gained": 3,
  "success_lost": 3,
  "raw_psnr": {
   "mean_diff": -0.18320830193914026,
   "se": 0.33716911341839817,
   "n": 18
  },
  "raw_depth_mae": {
   "mean_diff": -2.9592138898534618e-06,
   "se": 0.0007209776509399703,
   "n": 18
  },
  "raw_part_miou": {
   "mean_diff": 0.006554748306433569,
   "se": 0.005725749441589698,
   "n": 18
  },
  "raw_cd_whole": {
   "mean_diff": 9.342190539419228e-05,
   "se": 0.00021603290691777868,
   "n": 18
  },
  "axis_error_deg": {
   "mean_diff": 0.0396027889148787,
   "se": 0.04706198756604177,
   "n": 18
  }
 },
 "weaker_short": {
  "n": 26,
  "success_gained": 1,
  "success_lost": 6,
  "raw_psnr": {
   "mean_diff": 1.5902951424526175,
   "se": 0.7863002601175177,
   "n": 15
  },
  "raw_depth_mae": {
   "mean_diff": -0.0003259152613743636,
   "se": 0.0022024604719364962,
   "n": 15
  },
  "raw_part_miou": {
   "mean_diff": 0.02382276955471403,
   "se": 0.009497127917162772,
   "n": 15
  },
  "raw_cd_whole": {
   "mean_diff": -0.015284405797430612,
   "se": 0.001059630102278625,
   "n": 15
  },
  "axis_error_deg": {
   "mean_diff": 0.041287732515407315,
   "se": 0.09440687703211327,
   "n": 15
  }
 },
 "all_static_masks": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": -9.73021156618508,
   "se": 1.0384256989580982,
   "n": 21
  },
  "raw_depth_mae": {
   "mean_diff": 0.13381720175709888,
   "se": 0.01862860219292993,
   "n": 21
  },
  "raw_part_miou": {
   "mean_diff": -0.30739394417965266,
   "se": 0.028683283630939596,
   "n": 21
  },
  "raw_cd_whole": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 21
  },
  "axis_error_deg": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 21
  }
 },
 "duplicate_files": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 21
  },
  "raw_depth_mae": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 21
  },
  "raw_part_miou": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 21
  },
  "raw_cd_whole": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 21
  },
  "axis_error_deg": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 21
  }
 },
 "faint_gaussian_grid": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": -19.209737733138095,
   "se": 0.8283627958134752,
   "n": 21
  },
  "raw_depth_mae": {
   "mean_diff": 0.5327977657526317,
   "se": 0.026529603987112495,
   "n": 21
  },
  "raw_part_miou": {
   "mean_diff": -0.35149378841073575,
   "se": 0.029767081657472536,
   "n": 21
  },
  "raw_cd_whole": {
   "mean_diff": 0.09040360409554203,
   "se": 0.008381296569733741,
   "n": 21
  },
  "axis_error_deg": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 21
  }
 },
 "forged_score_files": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 21
 },
 "missing_half_scenes": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 11,
  "raw_psnr": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 10
  },
  "raw_depth_mae": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 10
  },
  "raw_part_miou": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 10
  },
  "raw_cd_whole": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 10
  },
  "axis_error_deg": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 10
  }
 }
}
```
