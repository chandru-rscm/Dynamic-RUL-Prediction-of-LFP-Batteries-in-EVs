import os

def fix_manuscript():
    with open(r"reports\latex\main_manuscript.tex", "r", encoding="utf-8") as f:
        content = f.read()

    # Replace \bibliography{sn-bibliography} with \nocite{*} \bibliography{sn-bibliography}
    old_bib = r"\bibliography{sn-bibliography}% common bib file"
    new_bib = r"""\nocite{*}
\bibliography{sn-bibliography}% common bib file"""

    if old_bib in content and r"\nocite{*}" not in content:
        content = content.replace(old_bib, new_bib)
        with open(r"reports\latex\main_manuscript.tex", "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated main_manuscript.tex with \\nocite{*} above \\bibliography{sn-bibliography}")
    else:
        print("Already updated or pattern not found.")

if __name__ == "__main__":
    fix_manuscript()
