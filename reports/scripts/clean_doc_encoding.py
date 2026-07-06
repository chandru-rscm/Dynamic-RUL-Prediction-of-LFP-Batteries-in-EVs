import docx

def clean_doc_encoding(path):
    doc = docx.Document(path)
    for p in doc.paragraphs:
        if '\ufffd' in p.text:
            # We fix common patterns where \ufffd represents en-dash or em-dash
            # If between digits like 383\ufffd391 or [7]\ufffd[9] -> en-dash
            text = p.text
            # Replace in runs to keep formatting when possible, or update run text
            for run in p.runs:
                if '\ufffd' in run.text:
                    t = run.text
                    # Check if between brackets or numbers
                    import re
                    t = re.sub(r'(\d+)\ufffd(\d+)', r'\1–\2', t)
                    t = re.sub(r'(\]\s*)\ufffd(\s*\[)', r'\1–\2', t)
                    t = re.sub(r'(\])\ufffd(\[)', r'\1–\2', t)
                    # Other standalone \ufffd in sentences usually em-dash or en-dash
                    t = t.replace('\ufffd', ' — ')
                    t = re.sub(r'\s+—\s+', ' — ', t)
                    run.text = t
    doc.save(path)
    print(f"Cleaned encoding in {path}")

if __name__ == "__main__":
    clean_doc_encoding(r"D:\chandru project\Final_Manuscript_Abstract_Intro_RelatedWork.docx")
    clean_doc_encoding(r"reports\Final_Manuscript_Abstract_Intro_RelatedWork.docx")
