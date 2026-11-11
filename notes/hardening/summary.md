| method | status | R* | success_rate | axis_error_deg | pivot_error | rotation_error_deg | translation_error | psnr | part_miou | depth_mae | cd_static | cd_mobile | cd_whole |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ablation_no2a | ok | +2.684 | 0.6538 | 1.335 | 0.005298 | 4.271 | 0.01387 | 32.31 | 0.6191 | 0.3578 | 0.1105 | 0.1294 | 0.104 |
| search_more | ok | +2.171 | 0.6538 | 1.891 | 0.001952 | 3.639 | 0.02927 | 31.38 | 0.5735 | 0.3622 | 0.1149 | 0.1474 | 0.1074 |
| better_color_geom | ok | +0.999 | 0.5 | 2.019 | 0.01372 | 4.632 | 0.03615 | 26.59 | 0.4485 | 0.5112 | 0.1324 | 0.1462 | 0.1272 |
| splart_seed2 | ok | +0.749 | 0.4615 | 2.202 | 0.008339 | 4.734 | 0.03568 | 25.51 | 0.4159 | 0.5487 | 0.1378 | 0.1528 | 0.1326 |
| splart_seed1 | ok | +0.501 | 0.4615 | 2.705 | 0.01284 | 5.803 | 0.03446 | 25.15 | 0.4098 | 0.5488 | 0.1378 | 0.1562 | 0.1326 |
| duplicate_files | ok | +0.000 | 0.3846 | 2.631 | 0.00994 | 6.037 | 0.03668 | 22.29 | 0.3473 | 0.6252 | 0.1488 | 0.162 | 0.1446 |
| splart | ok | +0.000 | 0.3846 | 2.631 | 0.00994 | 6.037 | 0.03668 | 22.29 | 0.3473 | 0.6252 | 0.1488 | 0.162 | 0.1446 |
| ablation_no2b | ok | -0.181 | 0.3462 | 2.739 | 0.009177 | 5.807 | 0.03617 | 21.44 | 0.3198 | 0.6613 | 0.1526 | 0.1596 | 0.1491 |
| all_static_masks | ok | -0.611 | 0.3846 | 2.631 | 0.00994 | 6.037 | 0.03668 | 16.88 | 0.2047 | 0.6859 | 0.1705 | 0.2 | 0.1446 |
| faint_gaussian_grid | ok | -0.717 | 0.3846 | 2.631 | 0.00994 | 6.037 | 0.03668 | 13 | 0.2036 | 0.8115 | 0.1855 | 0.162 | 0.1731 |
| ablation_no3b | ok | -1.056 | 0.3462 | 3.756 | 0.0292 | 7.225 | 0.04446 | 17.01 | 0.2765 | 0.6816 | 0.1516 | 0.1646 | 0.1503 |
| weaker_short | ok | -1.278 | 0.2692 | 3.312 | 0.03337 | 8.34 | 0.03857 | 18.03 | 0.2393 | 0.7392 | 0.1594 | 0.1723 | 0.1572 |
| missing_half_scenes | incomplete: 13 scenes missing | -2.288 | 0.1538 | 4.02 | 0.03947 | 8.711 | 0.03933 | 14.78 | 0.1362 | 0.85 | 0.1799 | 0.1853 | 0.1779 |
| icp_baseline | ok | -3.347 | 0.03846 | 4.747 | 0.03374 | 8.859 | 0.04941 | 10.59 | 0.02856 | 0.9672 | 0.1954 | 0.1963 | 0.1941 |
| icp_bruteforce | ok | -3.647 | 0 | 4.831 | 0.03722 | 9.399 | 0.04941 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| forged_score_files | ok | -3.708 | 0 | 4.815 | 0.03892 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| static_baseline | ok | -3.708 | 0 | 4.815 | 0.03892 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| ablation_no3a | ok | -3.805 | 0 | 4.829 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| empty_method_dir | failed: no predictions for this slice | -3.846 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| impossible_opacity_one_scene | failed: test_000: static_opacities: non-finite values | -3.846 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| lightweight_splart | failed: no predictions for this slice | -3.846 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| nan_axis_one_scene | failed: test_000: axis: non-finite values | -3.846 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| pickled_payload | failed: test_000: unreadable prediction file: ValueError | -3.846 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| too_many_gaussians | failed: test_000: 20809 Gaussians > limit 20000 | -3.846 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |

## Train slice

| method | success_rate | axis_error_deg | pivot_error | rotation_error_deg | translation_error | psnr | part_miou | depth_mae | cd_static | cd_mobile | cd_whole |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ablation_no2a | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| ablation_no2b | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| ablation_no3a | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| ablation_no3b | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| better_color_geom | 0.3889 | 2.702 | 0.02122 | 5.59 | 0.03612 | 22.68 | 0.3384 | 0.6207 | 0.1458 | 0.1633 | 0.1429 |
| icp_baseline | 0.1667 | 4.636 | 0.02874 | 7.269 | 0.05 | 12.62 | 0.1203 | 0.8677 | 0.1772 | 0.1786 | 0.1734 |
| icp_bruteforce | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| lightweight_splart | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| search_more | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| splart | 0.3889 | 2.766 | 0.02547 | 6.409 | 0.02876 | 22.67 | 0.3312 | 0.6206 | 0.1453 | 0.1636 | 0.1427 |
| splart_seed1 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| splart_seed2 | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| static_baseline | 0 | 4.832 | 0.03168 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |
| weaker_short | 0 | 5 | 0.05 | 10 | 0.05 | 10 | 0 | 1 | 0.2 | 0.2 | 0.2 |

## Seed spread (max - min over seeds 0,1,2)

```
{
 "articulation_estimation.success_rate": 0.07692307692307693,
 "articulation_estimation.axis_error_deg": 0.5026460687612286,
 "articulation_estimation.pivot_error": 0.004498608936692249,
 "articulation_estimation.rotation_error_deg": 1.3029911259307543,
 "articulation_estimation.translation_error": 0.0022237082042837406,
 "part_reconstruction.psnr": 3.216103742284716,
 "part_reconstruction.part_miou": 0.06861708034617608,
 "part_reconstruction.depth_mae": 0.0765426069904962,
 "part_reconstruction.cd_static": 0.010961150889111315,
 "part_reconstruction.cd_mobile": 0.009223013260551055,
 "part_reconstruction.cd_whole": 0.012087791408273985,
 "rank": 0.7486223528537709
}
```

## Paired vs reference (test scenes)

```
{
 "icp_baseline": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 9
 },
 "static_baseline": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 10
 },
 "ablation_no2a": {
  "n": 26,
  "success_gained": 7,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": 2.4055469651374466,
   "se": 0.7002568336936736,
   "n": 10
  },
  "raw_depth_mae": {
   "mean_diff": -0.008349042167717095,
   "se": 0.00180439172071676,
   "n": 10
  },
  "raw_part_miou": {
   "mean_diff": 0.046875871639924724,
   "se": 0.016858601737714623,
   "n": 10
  },
  "raw_cd_whole": {
   "mean_diff": -0.0015878940600790883,
   "se": 0.0005262811028390398,
   "n": 10
  },
  "axis_error_deg": {
   "mean_diff": -0.1653228758314769,
   "se": 0.10084985781710824,
   "n": 10
  }
 },
 "ablation_no2b": {
  "n": 26,
  "success_gained": 1,
  "success_lost": 2,
  "raw_psnr": {
   "mean_diff": 0.6373308260721728,
   "se": 0.5066977814413118,
   "n": 8
  },
  "raw_depth_mae": {
   "mean_diff": -0.0010324660452060614,
   "se": 0.002467576858669126,
   "n": 8
  },
  "raw_part_miou": {
   "mean_diff": 0.005747751619940511,
   "se": 0.005346425599724282,
   "n": 8
  },
  "raw_cd_whole": {
   "mean_diff": -0.0017445226991294263,
   "se": 0.00034195680762506093,
   "n": 8
  },
  "axis_error_deg": {
   "mean_diff": -0.041155010555789795,
   "se": 0.08536236438308036,
   "n": 8
  }
 },
 "ablation_no3a": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 10
 },
 "ablation_no3b": {
  "n": 26,
  "success_gained": 1,
  "success_lost": 2,
  "raw_psnr": {
   "mean_diff": -12.322082050702683,
   "se": 0.6843829047252975,
   "n": 8
  },
  "raw_depth_mae": {
   "mean_diff": 0.05809913827125977,
   "se": 0.008153179345419105,
   "n": 8
  },
  "raw_part_miou": {
   "mean_diff": -0.13266445560094625,
   "se": 0.01777280153995799,
   "n": 8
  },
  "raw_cd_whole": {
   "mean_diff": 0.0021410007577925376,
   "se": 0.001860536965340558,
   "n": 8
  },
  "axis_error_deg": {
   "mean_diff": 2.3582144988215714,
   "se": 0.4413274322274458,
   "n": 8
  }
 },
 "better_color_geom": {
  "n": 26,
  "success_gained": 4,
  "success_lost": 1,
  "raw_psnr": {
   "mean_diff": 0.20528835254505473,
   "se": 0.581873021335515,
   "n": 9
  },
  "raw_depth_mae": {
   "mean_diff": -0.00010825603281682994,
   "se": 0.0012221041448482093,
   "n": 9
  },
  "raw_part_miou": {
   "mean_diff": -0.01036351554514725,
   "se": 0.00966229366791851,
   "n": 9
  },
  "raw_cd_whole": {
   "mean_diff": -3.2822647538718885e-06,
   "se": 0.0003822193485597851,
   "n": 9
  },
  "axis_error_deg": {
   "mean_diff": -0.07588071963815773,
   "se": 0.05487047223932045,
   "n": 9
  }
 },
 "icp_bruteforce": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 10
 },
 "search_more": {
  "n": 26,
  "success_gained": 8,
  "success_lost": 1,
  "raw_psnr": {
   "mean_diff": 0.671441647789973,
   "se": 0.5962769697516926,
   "n": 9
  },
  "raw_depth_mae": {
   "mean_diff": -0.0010499462763563171,
   "se": 0.0010269763722378829,
   "n": 9
  },
  "raw_part_miou": {
   "mean_diff": 0.009396033758982063,
   "se": 0.005699920249291499,
   "n": 9
  },
  "raw_cd_whole": {
   "mean_diff": 0.0017253809859471827,
   "se": 0.0003274843804125463,
   "n": 9
  },
  "axis_error_deg": {
   "mean_diff": 0.25242199257171954,
   "se": 0.2674707217779127,
   "n": 9
  }
 },
 "splart_seed1": {
  "n": 26,
  "success_gained": 3,
  "success_lost": 1,
  "raw_psnr": {
   "mean_diff": -0.030378677280876017,
   "se": 0.6330663641504527,
   "n": 9
  },
  "raw_depth_mae": {
   "mean_diff": -0.0011552056729624205,
   "se": 0.0017350579358933525,
   "n": 9
  },
  "raw_part_miou": {
   "mean_diff": 0.001304638530914917,
   "se": 0.007042021798675465,
   "n": 9
  },
  "raw_cd_whole": {
   "mean_diff": -0.0002939516266764814,
   "se": 0.0005903323407921302,
   "n": 9
  },
  "axis_error_deg": {
   "mean_diff": 0.4928728296660228,
   "se": 0.4248081524578202,
   "n": 9
  }
 },
 "splart_seed2": {
  "n": 26,
  "success_gained": 3,
  "success_lost": 1,
  "raw_psnr": {
   "mean_diff": 0.5296422662428495,
   "se": 0.48033119540337094,
   "n": 9
  },
  "raw_depth_mae": {
   "mean_diff": -0.0007493744104855439,
   "se": 0.0012163282144887447,
   "n": 9
  },
  "raw_part_miou": {
   "mean_diff": 0.007550829492446047,
   "se": 0.006264865459636864,
   "n": 9
  },
  "raw_cd_whole": {
   "mean_diff": -0.00031275019635060606,
   "se": 0.00046289261913808906,
   "n": 9
  },
  "axis_error_deg": {
   "mean_diff": -0.11230987450088532,
   "se": 0.09934900897729099,
   "n": 9
  }
 },
 "weaker_short": {
  "n": 26,
  "success_gained": 1,
  "success_lost": 4,
  "raw_psnr": {
   "mean_diff": -1.688096186498677,
   "se": 0.4073689741434922,
   "n": 6
  },
  "raw_depth_mae": {
   "mean_diff": 0.006361064346094216,
   "se": 0.0031332253713705423,
   "n": 6
  },
  "raw_part_miou": {
   "mean_diff": -0.00242615257337205,
   "se": 0.008204418348036117,
   "n": 6
  },
  "raw_cd_whole": {
   "mean_diff": -0.0142550347522472,
   "se": 0.0026466230261879874,
   "n": 6
  },
  "axis_error_deg": {
   "mean_diff": 0.4960957268717658,
   "se": 0.5161257170929316,
   "n": 6
  }
 },
 "all_static_masks": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": -14.062898714771695,
   "se": 1.4053535048289918,
   "n": 10
  },
  "raw_depth_mae": {
   "mean_diff": 0.1579381977111561,
   "se": 0.023698994311334327,
   "n": 10
  },
  "raw_part_miou": {
   "mean_diff": -0.37072134635637577,
   "se": 0.03791199146587628,
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
 },
 "duplicate_files": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 0,
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
 },
 "faint_gaussian_grid": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 0,
  "raw_psnr": {
   "mean_diff": -24.164374656360792,
   "se": 0.8244870017640646,
   "n": 10
  },
  "raw_depth_mae": {
   "mean_diff": 0.48447403085291646,
   "se": 0.04333603780709329,
   "n": 10
  },
  "raw_part_miou": {
   "mean_diff": -0.37353887157303645,
   "se": 0.04896549118841273,
   "n": 10
  },
  "raw_cd_whole": {
   "mean_diff": 0.07388654703271032,
   "se": 0.011686677980342283,
   "n": 10
  },
  "axis_error_deg": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 10
  }
 },
 "forged_score_files": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 10
 },
 "missing_half_scenes": {
  "n": 26,
  "success_gained": 0,
  "success_lost": 6,
  "raw_psnr": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 4
  },
  "raw_depth_mae": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 4
  },
  "raw_part_miou": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 4
  },
  "raw_cd_whole": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 4
  },
  "axis_error_deg": {
   "mean_diff": 0.0,
   "se": 0.0,
   "n": 4
  }
 }
}
```
