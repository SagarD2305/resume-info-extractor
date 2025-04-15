import win32com.client
import os
import sys
from pathlib import Path

def convert_to_pdf(input_file):
    try:
        word = win32com.client.Dispatch('Word.Application')
        doc = word.Documents.Open(input_file)
        output_file = str(Path(input_file).with_suffix('.pdf'))
        doc.SaveAs(output_file, FileFormat=17)  # 17 represents PDF format
        doc.Close()
        word.Quit()
        return output_file
    except Exception as e:
        print(f"Error converting to PDF: {e}")
        return None

if __name__ == '__main__':
    # Get the absolute path of the input file
    input_file = os.path.abspath('sample_resume.docx')
    convert_to_pdf(input_file)
