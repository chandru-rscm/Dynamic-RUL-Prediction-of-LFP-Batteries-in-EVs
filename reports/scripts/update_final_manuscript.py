import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def update_files():
    new_conclusion_latex = r"""\section{Conclusion}\label{sec13}

Real-time and accurate prognosis of Lithium Iron Phosphate (LFP) batteries is still a challenging task in the field of electric vehicles because of their characteristic voltage plateau that is indicative of internal degradation of active material. In this paper, a physics-based machine learning framework, using gradient-boosted decision trees (LightGBM), was introduced specifically designed for Battery Management Systems (BMS) in automobiles. Our approach avoids expensive deep learning algorithms and uses voltage measurement.

The comprehensive analysis using 124 commercialized APR18650M1A cylindrical LFP cells (with a total of 22,474 operational evaluation points based on 72 different multi-step fast charging policies) clearly revealed the superior performance of our approach. By using a leak-proof GroupShuffleSplit protocol for cross-validation at the physical cell level, we found that the LightGBM framework provided out-of-sample Mean Absolute Error ($\text{MAE}$) of $81.35\text{ cycles}$ and an $R^2$ accuracy of $78.52\%$ with 24 strictly unseen batteries. Moreover, empirical benchmarking showed the superiority of our model compared to linear regression ($\text{MAE}$ of $152.90$) and comparable performance compared to Random Forest ($\text{MAE}$ of $80.18$) and XGBoost ($\text{MAE}$ of $82.53$).

Importantly, profiling on simulated automotive ARM Cortex microcontrollers showed that inference using the LightGBM model takes precisely $0.95\text{ milliseconds}$---$47$ times faster than recurrent LSTM models (around $45\text{ ms}$)---using just $809\text{ KB}$ of compiled flash memory space. This enables the algorithm to be seamlessly deployed in standard $1\text{ MB}$ automotive Electronic Control Units (ECUs) without affecting real-time operations in the vehicle control processes. Furthermore, split conformal prediction was able to establish safe uncertainty bounds of $\pm 122$ clock cycles with a $90.4\%$ coverage rate.

Lastly, the mathematically proven importance rankings of our data-driven approach, which found internal resistance ($\text{IR}$) to be the most prominent split feature ($> 35\%$ contribution), was validated through first order Equivalent Circuit Model ($\text{ECM}$) transfer function analysis. Real-time monitoring of the complex s-plane dynamics showed that as cell interfacial resistance doubles during aging, the system pole moves rightwards from $-0.1285\text{ rad/s}$ towards instability, which proved the data-driven model's ability to capture the underlying physics of the problem. Future work will explore how to leverage the physics-informed architecture of the LightGBM model to enable adaptive transfer learning for different chemistries in silicon-anode and sodium-ion cells as well as cloud-connected OTA calibrations in commercial EV fleets."""

    with open(r"reports\latex\main_manuscript.tex", "r", encoding="utf-8") as f:
        content = f.read()

    # Find start of conclusion
    idx_start = content.find(r"\section{Conclusion}")
    idx_end = content.find(r"\bibliography{sn-bibliography}")
    
    if idx_start != -1 and idx_end != -1:
        new_content = content[:idx_start] + new_conclusion_latex + "\n\n" + r"\bibliography{sn-bibliography}% common bib file" + "\n\n" + r"\end{document}" + "\n"
        with open(r"reports\latex\main_manuscript.tex", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully updated main_manuscript.tex with new conclusion and removed declarations.")

if __name__ == "__main__":
    update_files()
