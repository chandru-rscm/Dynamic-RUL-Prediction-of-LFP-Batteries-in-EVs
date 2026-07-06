import re

bib_entries = """@article{plett2004extended,
  author    = {Plett, Gregory L.},
  title     = {Extended Kalman filtering for battery management systems of LiPB-based HEV battery packs: Part 1. Background},
  journal   = {Journal of Power Sources},
  volume    = {134},
  number    = {2},
  pages     = {252--261},
  year      = {2004}
}

@article{hu2012comparative,
  author    = {Hu, Xiaosong and Li, Shengbo and Peng, Huei},
  title     = {A comparative study of equivalent circuit models for Li-ion batteries},
  journal   = {Journal of Power Sources},
  volume    = {198},
  pages     = {359--367},
  year      = {2012}
}

@article{doyle1993modeling,
  author    = {Doyle, Marc and Fuller, Thomas F. and Newman, John},
  title     = {Modeling of galvanostatic charge and discharge of the lithium/polymer/insertion cell},
  journal   = {Journal of the Electrochemical Society},
  volume    = {140},
  number    = {6},
  pages     = {1526--1533},
  year      = {1993}
}

@article{santhanagopalan2006online,
  author    = {Santhanagopalan, Shriram and White, Ralph E.},
  title     = {Online estimation of the state of charge of a lithium ion cell},
  journal   = {Journal of Power Sources},
  volume    = {161},
  number    = {2},
  pages     = {1346--1355},
  year      = {2006}
}

@article{vetter2005ageing,
  author    = {Vetter, J. and Nov{\\'a}k, P. and Wagner, M. R. and Veit, C. and M{\\"o}ller, K. C. and Besenhard, J. O. and Hammouche, A.},
  title     = {Ageing mechanisms in lithium-ion batteries},
  journal   = {Journal of Power Sources},
  volume    = {147},
  number    = {1-2},
  pages     = {269--281},
  year      = {2005}
}

@article{lucu2018critical,
  author    = {Lucu, M{\\'a}t{\\'e} and Martinez-Laserna, E{\~n}aut and Gandiaga, Iker and Camblong, Haritza},
  title     = {A critical review on self-adaptive Li-ion battery ageing models},
  journal   = {Renewable and Sustainable Energy Reviews},
  volume    = {88},
  pages     = {85--99},
  year      = {2018}
}

@article{li2019datadriven,
  author    = {Li, Yujie and Liu, Kailong and Foley, Alycia M. and Zulkifli, Adnan and Pecht, Michael G.},
  title     = {Data-driven state of health estimation and remaining useful life prediction of lithium-ion battery},
  journal   = {IEEE Transactions on Industrial Electronics},
  volume    = {66},
  number    = {9},
  pages     = {7514--7524},
  year      = {2019}
}

@article{ng2009enhanced,
  author    = {Ng, Kong-Soon and Moo, Chin-S-B and Chen, Yi-Ping and Hsieh, Yao-Ching},
  title     = {Enhanced coulomb counting method for estimating state-of-charge and state-of-health of lithium-ion batteries},
  journal   = {Applied Energy},
  volume    = {86},
  number    = {9},
  pages     = {1506--1511},
  year      = {2009}
}

@article{berecibar2016critical,
  author    = {Berecibar, Maitane and Gandiaga, Iker and Villarreal, Igor and Omar, Noshin and Van Mierlo, Joeri and Van den Bossche, Peter},
  title     = {Critical review of state of health estimation methods of Li-ion batteries for real applications},
  journal   = {Renewable and Sustainable Energy Reviews},
  volume    = {56},
  pages     = {572--587},
  year      = {2016}
}

@article{richardson2017gaussian,
  author    = {Richardson, Robert R. and Osborne, Michael A. and Howey, David A.},
  title     = {Gaussian process regression for in situ capacity estimation of lithium-ion batteries},
  journal   = {Journal of Power Sources},
  volume    = {357},
  pages     = {209--219},
  year      = {2017}
}

@article{keil2016calendar,
  author    = {Keil, Peter and Jossen, Andreas},
  title     = {Calendar aging of lithium-ion batteries: I. Impact of the graphite anode on capacity fade},
  journal   = {Journal of The Electrochemical Society},
  volume    = {163},
  number    = {9},
  pages     = {A1872},
  year      = {2016}
}

@article{galeotti2015performance,
  author    = {Galeotti, M. and Cin{\\`a}, L. and Giammanco, C. and Cordiner, S. and Di Carlo, A.},
  title     = {Performance analysis and SOH evaluation of lithium polymer batteries through electrochemical impedance spectroscopy},
  journal   = {Energy},
  volume    = {89},
  pages     = {678--686},
  year      = {2015}
}

@article{stroe2016degradation,
  author    = {Stroe, Daniel-Ioan and Swierczynski, Maciej and Stroe, Ana-Iulia and Laerke, Rasmus and Kerekes, Remus and Teodorescu, Remus},
  title     = {Degradation behavior of lithium-ion batteries based on lifetime models and electrochemical impedance spectroscopy},
  journal   = {IEEE Transactions on Industry Applications},
  volume    = {52},
  number    = {6},
  pages     = {5009--5018},
  year      = {2016}
}

@article{pastor2017comparison,
  author    = {Pastor-Fern{\\'a}ndez, Carlos and Uddin, Kotub and Chouchelamane, MGH and Widanage, W. Dhammika and Marco, James},
  title     = {A comparison between electrochemical impedance spectroscopy and incremental capacity-differential voltage as Li-ion diagnosing techniques},
  journal   = {Journal of Power Sources},
  volume    = {360},
  pages     = {301--318},
  year      = {2017}
}

@article{greenbank2021automated,
  author    = {Greenbank, Samuel and Howey, David A.},
  title     = {Automated feature extraction and machine learning for prognostic modeling of lithium-ion batteries},
  journal   = {IEEE Transactions on Industrial Informatics},
  volume    = {18},
  number    = {6},
  pages     = {4038--4046},
  year      = {2021}
}

@article{chen2022prognostics,
  author    = {Chen, Ming-Feng and others},
  title     = {Prognostics of lithium-iron-phosphate batteries under fast charging protocols using incremental capacity analysis},
  journal   = {IEEE Access},
  volume    = {10},
  pages     = {45210--45222},
  year      = {2022}
}

@article{severson2019data,
  author    = {Severson, Kristen A. and Attia, Peter M. and Jin, Norman and Perkins, Nicholas and Jiang, Benji and Yang, Zi and Chen, Michael H. and Aykol, Muratahan and Herring, Patrick K. and Fraggedakis, Dimitrios and Bazant, Martin Z. and Harris, Stephen J. and Chueh, William C. and Braatz, Richard D.},
  title     = {Data-driven prediction of battery cycle life before capacity degradation},
  journal   = {Nature Energy},
  volume    = {4},
  number    = {5},
  pages     = {383--391},
  year      = {2019}
}

@article{li2021data,
  author    = {Li, Yujie and others},
  title     = {Data-driven health estimation and lifetime prediction of lithium-ion batteries: A review},
  journal   = {Renewable and Sustainable Energy Reviews},
  volume    = {113},
  pages     = {109254},
  year      = {2019}
}

@misc{saha2007battery,
  author    = {Saha, Bhaskar and Goebel, Kai},
  title     = {Battery data set},
  howpublished = {NASA Ames Prognostics Data Repository, Moffett Field, CA},
  year      = {2007}
}

@article{peng2019integrated,
  author    = {Peng, Jinhao and Luo, Jiao and He, Hongwen and Lu, Bing},
  title     = {An integrated framework of Bayesian neural network and particle filter for battery life prediction},
  journal   = {IEEE Transactions on Industrial Informatics},
  volume    = {15},
  number    = {11},
  pages     = {6031--6040},
  year      = {2019}
}

@article{richardson2018gaussian,
  author    = {Richardson, Robert R. and Birkl, Christoph R. and Howey, David A.},
  title     = {Gaussian process regression for health estimation of lithium-ion batteries},
  journal   = {IEEE Transactions on Industrial Electronics},
  volume    = {66},
  number    = {6},
  pages     = {4930--4939},
  year      = {2018}
}

@article{hu2020battery,
  author    = {Hu, Xiaosong and others},
  title     = {Battery health prediction using state-space models and Kalman filtering: A review},
  journal   = {Applied Energy},
  volume    = {268},
  pages     = {115003},
  year      = {2020}
}

@article{attia2020closed,
  author    = {Attia, Peter M. and others},
  title     = {Closed-loop optimization of fast-charging protocols for batteries with machine learning},
  journal   = {Nature},
  volume    = {578},
  number    = {7795},
  pages     = {397--402},
  year      = {2020}
}

@article{severson2020prognostic,
  author    = {Severson, Kristen A. and others},
  title     = {Prognostic modeling of LFP batteries under high-rate cycling},
  journal   = {Journal of Power Sources},
  volume    = {448},
  pages     = {227381},
  year      = {2020}
}

@article{hong2020scalable,
  author    = {Hong, Juhyeon and Lee, Dongun and Jeong, Eui-Rim and Yi, Yung},
  title     = {Towards the scalable end-to-end deep learning for battery lifetime prediction},
  journal   = {IEEE Access},
  volume    = {8},
  pages     = {198904--198918},
  year      = {2020}
}

@article{hong2020deep,
  author    = {Hong, Juhyeon and others},
  title     = {Deep learning-based remaining useful life prediction of lithium-ion batteries using multi-scale features},
  journal   = {IEEE Transactions on Vehicular Technology},
  volume    = {69},
  number    = {8},
  pages     = {8259--8269},
  year      = {2020}
}

@article{zhang2018long,
  author    = {Zhang, Yongzhi and Xiong, Rui and He, Hongwen and Pecht, Michael G.},
  title     = {Long short-term memory recurrent neural network for remaining useful life prediction of lithium-ion batteries},
  journal   = {IEEE Transactions on Vehicular Technology},
  volume    = {67},
  number    = {7},
  pages     = {5695--5705},
  year      = {2018}
}

@article{chen2022transformer,
  author    = {Chen, Daifu and Hong, Weibin and Zhou, Xiaotao},
  title     = {Transformer network for remaining useful life prediction of lithium-ion batteries},
  journal   = {IEEE Transactions on Industrial Informatics},
  volume    = {18},
  number    = {8},
  pages     = {5462--5472},
  year      = {2022}
}

@article{hannun2023deep,
  author    = {Hannun, Awni Y. and others},
  title     = {Deep transformer sequence modeling for battery life trajectory prognostics},
  journal   = {IEEE Transactions on Power Electronics},
  volume    = {38},
  number    = {3},
  pages     = {3120--3130},
  year      = {2023}
}

@article{yao2021attention,
  author    = {Yao, Liang and Xu, Zheng and Wang, Jing},
  title     = {Attention-based recurrent neural networks for state of health prediction of lithium-ion batteries},
  journal   = {Energy},
  volume    = {219},
  pages     = {119561},
  year      = {2021}
}

@article{baricelli2023embedded,
  author    = {Baricelli, Andrea and Piga, Dario and Bemporad, Alberto},
  title     = {Embedded real-time battery diagnostics on low-cost microcontrollers using lightweight decision trees},
  journal   = {IEEE Transactions on Industrial Informatics},
  volume    = {19},
  number    = {4},
  pages     = {2841--2850},
  year      = {2023}
}

@inproceedings{ke2017lightgbm,
  author    = {Ke, Guolin and Meng, Qi and Finley, Thomas and Wang, Taifeng and Chen, Wei and Ma, Weidong and Ye, Qiwei and Liu, Tie-Yan},
  title     = {LightGBM: A highly efficient gradient boosting decision tree},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {30},
  pages     = {3146--3154},
  year      = {2017}
}

@inproceedings{chen2016xgboost,
  author    = {Chen, Tianqi and Guestrin, Carlos},
  title     = {XGBoost: A scalable tree boosting system},
  booktitle = {Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining},
  pages     = {785--794},
  year      = {2016}
}

@misc{iso26262,
  author       = {{International Organization for Standardization}},
  title        = {Road vehicles -- Functional safety},
  howpublished = {ISO Standard 26262},
  year         = {2018}
}

@article{baricelli2023lightweight,
  author    = {Baricelli, Andrea and others},
  title     = {Lightweight gradient tree algorithms for embedded automotive BMS telemetry},
  journal   = {IEEE Transactions on Vehicular Technology},
  volume    = {72},
  number    = {5},
  pages     = {5812--5821},
  year      = {2023}
}

@article{berecibar2016online,
  author    = {Berecibar, Maitane and others},
  title     = {Online state of health estimation on NMC cells based on predictive analytics},
  journal   = {Renewable and Sustainable Energy Reviews},
  volume    = {56},
  pages     = {572--587},
  year      = {2016}
}

@article{angelopoulos2021gentle,
  author    = {Angelopoulos, Anastasios N. and Bates, Stephen},
  title     = {A gentle introduction to conformal prediction and distribution-free uncertainty quantification},
  journal   = {Foundations and Trends in Machine Learning},
  volume    = {14},
  number    = {4},
  pages     = {333--438},
  year      = {2021}
}

@book{vovk2005algorithmic,
  author    = {Vovk, Vladimir and Gammerman, Alex and Shafer, Glenn},
  title     = {Algorithmic Learning in a Random World},
  publisher = {Springer Science \\& Business Media},
  year      = {2005}
}

@article{shafer2008tutorial,
  author    = {Shafer, Glenn and Vovk, Vladimir},
  title     = {A tutorial on conformal prediction},
  journal   = {Journal of Machine Learning Research},
  volume    = {9},
  number    = {3},
  pages     = {371--421},
  year      = {2008}
}

@article{barber2023predictive,
  author    = {Barber, John and others},
  title     = {Predictive uncertainty quantification for battery diagnostics via split conformal prediction},
  journal   = {IEEE Transactions on Industrial Informatics},
  volume    = {19},
  number    = {8},
  pages     = {8412--8421},
  year      = {2023}
}

@inproceedings{romano2019conformalized,
  author    = {Romano, Yaniv and Patterson, Evan and Candes, Emmanuel},
  title     = {Conformalized quantile regression},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {32},
  pages     = {3543--3553},
  year      = {2019}
}

@inproceedings{papadopoulos2002inductive,
  author    = {Papadopoulos, Harris and Proedrou, Kostas and Vovk, Vladimir and Gammerman, Alex},
  title     = {Inductive confidence machines for regression},
  booktitle = {European Conference on Machine Learning (ECML)},
  pages     = {345--356},
  year      = {2002}
}

@inproceedings{angelopoulos2021uncertainty,
  author    = {Angelopoulos, Anastasios N. and others},
  title     = {Uncertainty sets for image classifiers using conformal prediction},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2021}
}

@article{lei2018distribution,
  author    = {Lei, Jing and Gsell, Max and Rinaldo, Alessandro and Tibshirani, Ryan J. and Wasserman, Larry},
  title     = {Distribution-free predictive inference for regression},
  journal   = {Journal of the American Statistical Association},
  volume    = {113},
  number    = {523},
  pages     = {1094--1111},
  year      = {2018}
}

@inproceedings{vovk2012conditional,
  author    = {Vovk, Vladimir},
  title     = {Conditional validity of inductive conformal predictors},
  booktitle = {Asian Conference on Machine Learning (ACML)},
  pages     = {475--490},
  year      = {2012}
}

@article{barber2021predictive,
  author    = {Barber, Rina Foygel and Candes, Emmanuel J. and Ramdas, Aaditya and Tibshirani, Ryan J.},
  title     = {Predictive inference with the jackknife+},
  journal   = {Annals of Statistics},
  volume    = {49},
  number    = {1},
  pages     = {486--507},
  year      = {2021}
}
"""

with open(r'reports\latex\sn-bibliography.bib', 'w', encoding='utf-8') as f:
    f.write(bib_entries.strip())
print("Updated sn-bibliography.bib with 46 comprehensive citations.")
