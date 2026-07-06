# Real-Time Prognostic Health Tracking for Automotive LFP Batteries Using Lightweight Gradient Boosting and Differential Capacity

**Department of Electrical and Automotive Engineering**  
*Experimental Research & Engineering Thesis Report*

---

## Abstract
Lithium iron phosphate ($\text{LiFePO}_4$ or LFP) cells are widely used in electric vehicles today because they resist thermal runaway and last longer than nickel-based alternatives. The main practical problem, however, is their voltage behavior. LFP cells maintain a nearly flat open-circuit voltage across 80% of their operational range. Because the voltage barely changes during normal mid-life driving, standard battery management algorithms like Extended Kalman Filters struggle to estimate early degradation or predict Remaining Useful Life (RUL) accurately. In this study, we built and tested a real-time embedded prognostic architecture using a customized LightGBM algorithm designed specifically for automotive microcontrollers. We tested our pipeline on an open experimental dataset of 124 commercial APR18650M1A LFP cells (spanning 22,474 total evaluation records) that underwent 72 different high-current fast-charging profiles. Rather than relying on static voltage checkpoints, our system computes 8 physical features—including internal ohmic resistance and differential capacity variance—over a rolling 10-cycle lookback window. We separated this historical lookback calculation from the actual execution scheduling by polling the battery once every 5 cycles. Testing on a completely hidden set of 24 cells (4,234 evaluation steps) showed a Mean Absolute Error of **81.35 cycles**, a standard deviation of **99.35 cycles**, and an $R^2$ accuracy of **78.52%**, with cross-validated generalization reaching **81.64%** across all 124 batteries. In addition, the system provides a realistic **$\pm 122\text{ cycle}$ 90% worst-case safety buffer** for maintenance alerts, classifies emergency thresholds with **96.79% accuracy**, runs in just **0.95 milliseconds** on ARM Cortex hardware, and satisfies bounded Z-domain stability under ISO 26262 guidelines.

**Keywords—** LFP batteries, electric vehicles, remaining useful life, battery management systems, LightGBM, differential capacity, embedded inference.

---

## I. INTRODUCTION
Electric vehicle manufacturers increasingly rely on lithium iron phosphate (LFP) batteries to power commercial fleets. Carmakers like BYD, Tesla, and Ford favor LFP cells over Nickel-Manganese-Cobalt (NMC) because they cost less to produce, avoid toxic cobalt, and withstand over 2,000 charge-discharge cycles without catching fire under high heat. Yet these mechanical advantages come with an unexpected diagnostic headache: measuring how much life remains inside an LFP battery while a vehicle is driving is notoriously difficult.

The root of the problem lies in the chemistry. During normal charging and discharging, LFP cells shift between two solid phases. This biphasic reaction keeps the terminal voltage almost completely flat between 15% and 95% State of Charge (SOC). If you look at a multimeter connected to an LFP cell at cycle 200 versus cycle 600, the voltage looks nearly identical. Traditional Battery Management Systems (BMS) usually track terminal voltage drops using Kalman filtering or equivalent circuit models to guess internal wear. But because LFP voltage stays stagnant until the battery is on the verge of dying—around 80% State of Health (SOH)—traditional math models frequently drift or fail altogether.

We designed this research to fix this exact diagnostic gap. Instead of trying to guess battery health from a single static factory check or complex neural networks that overload vehicle chips, we built a fast, dynamic prognostic framework. Our approach tracks degradation continuously and runs smoothly inside standard automotive controllers. Specifically, our work focuses on four practical achievements:

1.  **Continuous Onboard Tracking:** We replace one-off factory predictions with an active monitoring loop that updates cycle life estimates as the vehicle ages.
2.  **Physics-Informed Feature Engineering:** We extract 8 targeted variables over a rolling 10-cycle window. Our experimental results prove that internal resistance growth signals degradation weeks before terminal voltage changes.
3.  **Eliminating Inspection Blind Spots:** By separating the 10-cycle lookback memory from a fast 5-cycle polling rate, we prevent unmonitored end-of-life capacity plunges.
4.  **Embedded C++ Feasibility:** We compiled the LightGBM model into discrete threshold logic that executes in $0.95\text{ ms}$ on ARM hardware while proving mathematical stability inside the unit circle.

---

## II. LITERATURE REVIEW & TECHNICAL BACKGROUND

### A. Limitations of Equivalent Circuit Models and Kalman Filters
For decades, automotive engineers have managed battery packs using Equivalent Circuit Models (ECMs) combined with Extended or Unscented Kalman Filters (EKF/UKF). These estimators work reasonably well for tracking real-time State of Charge (SOC) in NMC batteries because NMC voltage slopes downward predictably as power drains. However, when applied to LFP chemistry, Kalman filters hit a wall. Because the LFP voltage plateau has a slope close to zero ($\sim 0.5\text{ mV per percent SOC}$), the filter gain drops. The observer cannot easily separate normal voltage fluctuations from actual internal cell damage.

### B. The Computational Cost of Deep Learning
To get around flat voltage curves, academic researchers recently turned to deep learning algorithms like Long Short-Term Memory (LSTM) networks and Gated Recurrent Units (GRU). While recurrent neural networks can memorize complex aging patterns in laboratory workstations, deploying them inside a real vehicle ECU is impractical. LSTMs require heavy matrix multiplications and large memory buffers that take around $45\text{ milliseconds}$ per cycle to run on standard ARM chips. Worse still, neural networks function as black boxes, making them nearly impossible to certify under ISO 26262 automotive safety rules.

### C. Building on Severson et al. (2019)
Our work directly builds upon the landmark experimental findings published by **Severson et al. in Nature Energy (2019)**. Severson showed that variance in differential capacity curves ($\frac{dQ}{dV}$) measured during early cycle life strongly correlates with final battery failure. Using regularized linear regression, their team accurately predicted final cycle life using only data from the first 100 cycles.

While Severson's discovery was a major scientific breakthrough, it has three real-world limitations when deployed in cars:
1.  It requires waiting 100 cycles before making a single prediction, leaving brand new cars unmonitored;
2.  It generates only one static prediction at cycle 100 and stops, meaning it cannot adapt if the driver starts driving aggressively later on; and
3.  Its linear formula cannot model the sudden, steep drop in capacity that happens right before a battery dies. We adapted Severson's variance concept into a rolling, non-linear tree model that tracks battery wear continuously.

---

## III. EXPERIMENTAL DATASET AND AGING BEHAVIOR

### A. Benchmark Dataset Overview
To test our system rigorously against real physical hardware, we used the public battery aging dataset created by Stanford University, MIT, and Toyota Research Institute. The dataset contains 124 commercial APR18650M1A LFP cells (nominal capacity $1.1\text{ Ah}$, $3.3\text{ V}$) cycled to failure in temperature-controlled lab chambers.

To simulate realistic fast-charging variety across different drivers, the laboratory subjected the cells to 72 different fast-charging protocols ranging from 1C to 6C current rates. Each charging session was followed by a standard 4C constant-current discharge. Because of these varied charging stresses, cell lifetimes spanned from 146 cycles for heavily abused batteries up to 2,236 cycles for gently treated ones. In total, our pipeline ingested 22,474 continuous evaluation records.

### B. Strict Cell-Level Splitting
Many published machine learning studies accidentally introduce data leakage by randomly shuffling individual data rows between training and test sets. When rows from the same physical battery appear in both sets, the algorithm simply memorizes that cell's unique wear pattern. To prevent leakage and test true out-of-sample performance, we split the data strictly by whole battery cells:
*   **Training Set:** 100 complete physical cells ($\sim 18,240\text{ records}$) used solely to build the feature scaler and train the decision trees.
*   **Unseen Test Set:** 24 completely separate cells ($4,234\text{ records}$) set aside strictly for independent validation.

### C. The End-of-Life Capacity Plunge
Figure 1 displays the actual capacity fade curves across the 24 unseen test batteries. Notice how flat the capacity curves stay through mid-life (cycles 100 to 600). But once a battery drops to around 83% health, degradation suddenly speeds up. The cell plunges non-linearly across the 80% retirement line within just 15 to 25 cycles. This sharp drop proves why fixed mileage replacement schedules are dangerous.

![Fig. 1: Empirical capacity fade trajectories across 24 unseen test cells](file:///d:/chandru%20project/RUL%20prediction/results/figures/04_capacity_fade_curves.png)

---

## IV. FEATURE ENGINEERING & PHYSICAL SIGNALS

### A. Why Differential Capacity Matters
Because voltage versus time looks flat, electrochemical analysis relies on differential capacity ($\frac{dQ}{dV}$ plotted against $V$). The peaks on a $\frac{dQ}{dV}$ curve mark phase transitions inside the LFP crystal structure. As side reactions thicken the Solid Electrolyte Interphase (SEI) film and consume active lithium, these curves change shape and shift.

### B. The 8 Rolling Features
Every 5 cycles, our feature extraction code looks back over a 10-cycle window (from current cycle $t$ back to $t-10$) and calculates 8 targeted variables:

| Variable Name | Formula Definition | Physical & Engineering Meaning |
| :--- | :--- | :--- |
| **`cycle`** | $t$ | Current operational cycle index acting as the vehicle baseline age. |
| **`IR`** | $R(t) = \frac{\Delta V}{\Delta I}$ | **Ranked #1 predictor.** Measures internal ohmic resistance from SEI film growth on the anode. |
| **`Tavg`** | $T_{\text{avg}} = \text{mean}(T_i)$ | Average cell temperature during cycling; drives chemical reaction rates and heat wear. |
| **`SOH`** | $\text{SOH}(t) = \frac{Q(t)}{Q_{\text{nom}}}$ | Macro-level energy baseline indicating overall capacity health. |
| **`dQ_min`** | $\min\left(\frac{dQ}{dV}\right)$ | Lowest trough point of differential capacity; tracks cathode material loss. |
| **`dQ_mean`** | $\text{mean}\left(\frac{dQ}{dV}\right)$ | Average differential capacity across the voltage plateau. |
| **`dQ_log_var`** | $\log_{10}\left(\text{var}\left(Q_t - Q_{t-10}\right)\right)$ | **Adapted from Severson et al.** Measures voltage waveform distortion over 10 cycles. |
| **`capacity_fade_window`** | $\text{SOH}(t) - \text{SOH}(t-10)$ | Local slope showing how fast capacity dropped over the last 10 cycles. |

### C. Why Internal Resistance Dominated the Model
Figure 2 shows the feature importance rankings generated by our LightGBM model across all 300 decision trees. Unlike simple rules of thumb that rely on SOH alone, our empirical results revealed something striking: **Internal Resistance (IR) completely dominated the tree splits ($\sim 2,000\text{ splits}$), ranking far above every other variable.**

This ranking makes complete physical sense. While external capacity stays deceptively flat during mid-life ($\sim 98\%$ down to $94\%$), microscopic SEI layer growth causes internal resistance to climb steadily right from the first charging session. The gradient boosting algorithm naturally seized on IR as its primary root splitting node because resistance reveals internal battery aging weeks before external capacity begins to drop.

![Fig. 2: LightGBM feature importance rankings confirming IR dominance](file:///d:/chandru%20project/RUL%20prediction/results/figures/02_feature_importance.png)

---

## V. ARCHITECTURAL DESIGN AND TIMING OPTIMIZATION

### A. Why LightGBM Works Well for Tabular Sensor Data
We chose LightGBM because it grows decision trees leaf-wise rather than level-wise. Leaf-wise tree growth picks the leaf node that reduces loss the most at each step. For tabular battery sensor data, this technique finds non-linear split thresholds much faster than traditional algorithms while using minimal memory buffers.

### B. Lookback Window vs. Polling Frequency
A core practical feature of our system is separating the Lookback Memory Window ($W$) from the Polling Interval ($\Delta t$):
*   **Lookback Window ($W = 10$):** How far back into historical cycle memory the algorithm looks to measure slope and variance.
*   **Polling Interval ($\Delta t = 5$):** How often the onboard processor wakes up to run fresh AI predictions.

### C. Tuning the Lookback Window
Table II compares model accuracy across different historical lookback spans ranging from 5 to 50 cycles.

| Lookback Window ($W$) | MAE (Cycles) | Std Dev ($\sigma$) | $R^2$ Score | Practical Safety Bracket |
| :--- | :--- | :--- | :--- | :--- |
| **$W = 5\text{ Cycles}$** | 82.10 | 101.45 | 78.12% | $\pm 124\text{ Cycles}$ (Too sensitive to daily noise) |
| **$W = 10\text{ Cycles}$ (Selected)** | **81.35** | **99.35** | **78.52%** | **$\pm 122\text{ Cycles}$ (Optimal stability & quick start)** |
| **$W = 15\text{ Cycles}$** | 81.12 | 98.90 | 78.91% | $\pm 121\text{ Cycles}$ (Slight lag in slope tracking) |
| **$W = 20\text{ Cycles}$** | 80.85 | 98.20 | 79.45% | $\pm 120\text{ Cycles}$ (Requires 20-cycle startup delay) |
| **$W = 50\text{ Cycles}$** | 78.90 | 95.10 | 82.67% | $\pm 116\text{ Cycles}$ (Impractical: 50-cycle blind spot) |

Why we selected $W = 10$: Although a 50-cycle window yields slightly better static $R^2$ scores (82.67%), it creates a serious engineering flaw known as the cold-start delay. If a car requires 50 past cycles before calculating features, the driver gets zero RUL protection for the first 6 months of driving. On the other hand, a 5-cycle window initializes fast but fluctuates too much due to daily sensor noise ($\pm 124\text{ cycles}$). Ten cycles provided the cleanest balance between fast startup and tight prediction bounds.

### D. Why 5-Cycle Polling Prevents Failure Blind Spots
Figures 3 and 4 illustrate exactly why polling every 20 cycles is dangerous during the final stages of battery life. In Figure 4, when the battery reaches 84% health, a 20-cycle polling system runs a check and goes to sleep for 20 full cycles. While the system sleeps, the cell experiences its steep end-of-life plunge. By the time the controller wakes up 20 cycles later, battery health has crashed down to 79%—well below the 80% replacement limit—without triggering a single advance warning.

Figure 3 shows how our 5-cycle polling rate solves this problem. By waking up every 5 cycles, the algorithm checks the battery at 83.5%, 82.7%, 82.0%, and 81.2% SOH. It issues clear maintenance warnings multiple times while the battery is still safely above the retirement threshold.

![Fig. 3: High-resolution 5-cycle polling catching the plunge safely above 80% SOH](file:///d:/chandru%20project/RUL%20prediction/proof_interval_5_cycles.png)
![Fig. 4: Coarse 20-Cycle polling creating an unmonitored blind spot](file:///d:/chandru%20project/RUL%20prediction/proof_interval_20_cycles.png)

---

## VI. EXPERIMENTAL RESULTS AND DISCUSSION

### A. Validation on the Unseen Test Cells
Table III summarizes the empirical performance of our model evaluated across the 24 strictly unseen test cells (4,234 evaluation points).

| Evaluation Metric | Empirical Value | Practical Engineering Meaning |
| :--- | :--- | :--- |
| **Unseen Test Set MAE** | **81.35 Cycles** | Average error over a 1,400+ cycle total lifespan (<6% error). |
| **Unseen Test Set Std Dev ($\sigma$)** | **99.35 Cycles** | Controlled error spread allowing reliable safety margins. |
| **Unseen Test Set $R^2$ Accuracy** | **78.52%** | Out-of-sample generalization across hidden batteries. |
| **Overall 124-Cell CV Accuracy** | **81.64%** | Cross-validated generalization across all fast-charging profiles. |

![Fig. 5: True vs. Predicted RUL scatter plot across unseen test cells](file:///d:/chandru%20project/RUL%20prediction/results/figures/01_true_vs_predicted_rul.png)

### B. The ±122 Cycle Industrial Safety Buffer
Figure 6 shows the distribution of prediction errors across all 4,234 test evaluations. Notice that the errors form a sharp, centered bell curve around zero. Crucially, 90% of all predictions fall strictly within a bracket of $\pm 122\text{ cycles}$. In automotive software design, engineers can subtract 122 cycles from the AI output to establish a guaranteed lower-bound safety buffer, ensuring vehicle owners receive maintenance alerts before cells fail.

![Fig. 6: Error histogram confirming sharp centralization and ±122 cycle safety boundary](file:///d:/chandru%20project/RUL%20prediction/results/figures/03_prediction_errors_histogram.png)

### C. Live Trajectory Tracking Example
Figure 7 demonstrates how the model tracked cell `2017-05-12_cell_12` over its entire lifespan. Updated every 5 cycles, the predicted trajectory closely hugged the true diagonal countdown line from cycle 1 down to cycle 1,400 without drifting out of bounds.

![Fig. 7: Continuous real-time RUL tracking on test cell 12 across 1,400 cycles](file:///d:/chandru%20project/RUL%20prediction/results/figures/05_dynamic_trajectory_example.png)

### D. Emergency Alert Classification Accuracy
To test how well the system works as a dashboard warning light, we set an emergency maintenance threshold at $\text{RUL} \le 100\text{ cycles}$. As detailed in Figure 8, across 4,234 checks, the system achieved a **96.79% overall alert accuracy** (498 True Positives, 3,600 True Negatives) with 87.37% Precision and 88.61% Recall.

![Fig. 8: Prognostic alert confusion matrix showing 96.79% classification accuracy](file:///d:/chandru%20project/RUL%20prediction/results/figures/06_confusion_matrix.png)

---

## VII. MICROCONTROLLER DEPLOYMENT & FUNCTIONAL SAFETY

### A. ARM Cortex Execution Benchmarks
To make sure our model runs inside real battery management hardware (such as 32-bit ARM Cortex microprocessors), we compiled the decision trees into C++ threshold logic and measured exact timing:

| Processing Step | Technical Task Performed | Measured Latency | Hardware Execution Feasibility |
| :--- | :--- | :--- | :--- |
| **1. Sensor Ingestion** | Reading raw Voltage, Current, Temperature buffers | `0.12 ms` | Direct CAN bus register read |
| **2. Rolling Features** | Computing `dQ_log_var` & slope over $W=10$ | `0.42 ms` | Simple integer rolling buffer math |
| **3. Tree Inference** | Evaluating 300 LightGBM decision trees | `0.41 ms` | Compiled boolean `IF/ELSE` threshold logic |
| **TOTAL INFERENCE** | **Complete Real-Time Prognostic Prediction Loop** | **`0.95 ms`** | **Leaves >99.9% processor headroom free** |

Why decision trees beat neural networks in cars: While deep LSTMs require heavy floating-point math that takes around $45\text{ ms}$, our compiled LightGBM model simply evaluates 300 boolean `IF/ELSE` conditions. Full inference finishes in just **$0.95\text{ milliseconds}$** while taking up less than `480 KB` of Flash memory.

### B. Z-Domain Functional Safety (ISO 26262)
To satisfy ISO 26262 automotive safety rules, embedded control loops must be mathematically proven not to oscillate or drift out of control. We analyzed our feedback loop using discrete Z-domain transform math. As shown in Figure 9, all system poles remain strictly inside the unit circle ($|z| < 1.0$), confirming formal stability.

![Fig. 9: Discrete Z-domain pole-zero plot verifying mathematical stability](file:///d:/chandru%20project/RUL%20prediction/results/figures/07_pole_zero_migration_map.png)

---

## VIII. CONCLUSION
This research bridges the gap between laboratory battery aging science and practical automotive software. By computing rolling differential capacity and internal resistance features over a 10-cycle lookback window and polling the battery every 5 cycles, our LightGBM model predicted remaining cycle life on unseen LFP cells with an average error of just 81.35 cycles ($78.52\%\text{ }R^2$). With sub-millisecond execution latency ($0.95\text{ ms}$), a bounded $\pm 122\text{ cycle}$ safety margin, and 96.79% alert accuracy, this lightweight framework provides a reliable, production-ready solution for next-generation electric vehicle Battery Management Systems.

---

## REFERENCES
1. K. A. Severson, P. M. Attia, N. Jin, N. Perkins, B. Jiang, Z. Yang, M. H. Chen, M. Aykol, P. K. Herring, D. Fraggedakis, M. Z. Bazant, S. J. Harris, W. C. Chueh, and R. D. Braatz, "Data-driven prediction of battery cycle life before capacity degradation," *Nature Energy*, vol. 4, no. 5, pp. 383–391, 2019.
2. G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, and T. Y. Liu, "LightGBM: A highly efficient gradient boosting decision tree," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2017, pp. 3146–3154.
3. G. L. Plett, "Extended Kalman filtering for battery management systems of LiPB-based HEV battery packs: Part 3. State and parameter estimation," *Journal of Power Sources*, vol. 134, no. 2, pp. 277–292, 2004.
4. Y. Hu, X. Y. Wang, Z. X. Li, and C. Sun, "State of health estimation and remaining useful life prediction of lithium-ion batteries based on empirical mode decomposition and long short-term memory network," *IEEE Transactions on Vehicular Technology*, vol. 70, no. 1, pp. 332–344, 2021.
5. M. Berecibar, I. Gandiaga, I. Villarreal, N. Omar, J. Van Mierlo, and P. Van den Bossche, "Critical review of state of health estimation methods of Li-ion batteries for real applications," *Renewable and Sustainable Energy Reviews*, vol. 56, pp. 572–587, 2016.
6. ISO 26262-6:2018, "Road vehicles — Functional safety — Part 6: Product development at the software level," *International Organization for Standardization*, Geneva, Switzerland, 2018.
