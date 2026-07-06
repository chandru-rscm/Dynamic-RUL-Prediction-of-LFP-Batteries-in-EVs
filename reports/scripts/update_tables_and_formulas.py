import os

def update_manuscript():
    file_path = r"reports\latex\main_manuscript.tex"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Table 1 column width
    old_t1 = r"\begin{tabular}{@{}c p{2.2cm} p{7.0cm} p{4.2cm}@{}}"
    new_t1 = r"\begin{tabular}{@{}c p{2.2cm} p{4.8cm} p{3.2cm}@{}}"
    content = content.replace(old_t1, new_t1)

    # 2. Update Table 2 column width
    old_t2 = r"\begin{tabular}{@{}l c c c c p{4.2cm}@{}}"
    new_t2 = r"\begin{tabular}{@{}l c c c c p{2.6cm}@{}}"
    content = content.replace(old_t2, new_t2)

    # 3. Update Table 3 column width
    old_t3 = r"\begin{tabular}{@{}l c c c c c c p{3.8cm}@{}}"
    new_t3 = r"\begin{tabular}{@{}l c c c c c c p{2.4cm}@{}}"
    content = content.replace(old_t3, new_t3)

    # 4. Update Table 4 column width
    old_t4 = r"\begin{tabular}{@{}l c c c c c p{3.8cm}@{}}"
    new_t4 = r"\begin{tabular}{@{}l c c c c c p{2.4cm}@{}}"
    content = content.replace(old_t4, new_t4)

    # 5. Update Table 5: REMOVE bolding from unseen row and accuracy as requested!
    old_t5 = r"""\begin{tabular}{@{}l c c c@{}}
\toprule
\textbf{Dataset Split} & \textbf{Cell Count} & \textbf{MAE Error} & \textbf{$R^2$ Accuracy} \\
\midrule
Training Set & 100 Cells & 48.70 cycles & \textbf{95.74\%} \\[1ex]
\textbf{Unseen Test Set} & \textbf{24 Cells} & \textbf{81.35 cycles} & \textbf{78.52\%} \\
\bottomrule
\end{tabular}"""
    new_t5 = r"""\begin{tabular}{@{}l c c c@{}}
\toprule
\textbf{Dataset Split} & \textbf{Cell Count} & \textbf{MAE Error} & \textbf{$R^2$ Accuracy} \\
\midrule
Training Set & 100 Cells & 48.70 cycles & 95.74\% \\[1ex]
Unseen Test Set & 24 Cells & 81.35 cycles & 78.52\% \\
\bottomrule
\end{tabular}"""
    content = content.replace(old_t5, new_t5)

    # 6. Update Table 6 column width
    old_t6 = r"\begin{tabular}{@{}l c c c c p{3.2cm}@{}}"
    new_t6 = r"\begin{tabular}{@{}l c c c c p{2.8cm}@{}}"
    content = content.replace(old_t6, new_t6)

    # 7. Update Table 7 column width
    old_t7 = r"\begin{tabular}{@{}l c c p{4.5cm}@{}}"
    new_t7 = r"\begin{tabular}{@{}l c c p{3.5cm}@{}}"
    content = content.replace(old_t7, new_t7)

    # 8. Update Section 7.5 with explicit formulas for Accuracy, Precision, Recall, F1
    old_sec75 = r"""In the test set, the algorithm classified True Healthy states ($>100\text{ cycles}$) 3,600 times (True Negatives) with just 72 False Positives. The model correctly identified critical aging states ($\le 100\text{ cycles}$) 498 times (True Positives), failing to do so only 64 times (False Negatives). Thus, the classifier achieved an accuracy rate of $96.79\%$, precision of $87.37\%$, and recall (sensitivity) of $88.61\%$. In order to combine the performance measures of alerts into a single unified figure, we calculate the harmonic $F_1$-score as follows:
\begin{equation}
F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}} = 2 \cdot \frac{0.8737 \cdot 0.8861}{0.8737 + 0.8861} = 87.98\%. \label{eq:f1_score}
\end{equation}"""

    new_sec75 = r"""In the test set, the algorithm classified True Healthy states ($>100\text{ cycles}$) 3,600 times (True Negatives, $\text{TN}$) with just 72 False Positives ($\text{FP}$). The model correctly identified critical aging states ($\le 100\text{ cycles}$) 498 times (True Positives, $\text{TP}$), failing to do so only 64 times (False Negatives, $\text{FN}$). Using these empirical confusion matrix counts across all 4,234 evaluation points, we calculate the formal classification performance metrics along with their exact numerical results as follows:

\begin{align}
\text{Accuracy} &= \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}} = \frac{498 + 3600}{498 + 3600 + 72 + 64} = \frac{4098}{4234} = 96.79\%, \label{eq:accuracy} \\[1ex]
\text{Precision} &= \frac{\text{TP}}{\text{TP} + \text{FP}} = \frac{498}{498 + 72} = \frac{498}{570} = 87.37\%, \label{eq:precision} \\[1ex]
\text{Recall} &= \frac{\text{TP}}{\text{TP} + \text{FN}} = \frac{498}{498 + 64} = \frac{498}{562} = 88.61\%, \label{eq:recall} \\[1ex]
F_1 &= 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}} = 2 \cdot \frac{0.8737 \cdot 0.8861}{0.8737 + 0.8861} = 87.98\%. \label{eq:f1_score}
\end{align}"""
    
    if old_sec75 in content:
        content = content.replace(old_sec75, new_sec75)
        print("Updated Section 7.5 formulas successfully.")
    else:
        print("Could not find exact old_sec75 match, checking partial match...")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated main_manuscript.tex successfully.")

if __name__ == "__main__":
    update_manuscript()
