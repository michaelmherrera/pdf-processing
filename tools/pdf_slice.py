from PyPDF2 import PdfFileReader, PdfFileWriter
import os.path as path
import os
import argparse

parser = argparse.ArgumentParser(description='Split pdfs and reorder the pages')
parser.add_argument('input_dir', type=str,
                    help='the directory where the pdfs are')
parser.add_argument('output_dir', type=str,
                    help='the directory in which to place the output')

page_order = {
    2:  (2,1),
    4:  (4,1,2,3),
    6:  (6,1,2,5,4,3),
    8:  (8,1,2,7,6,3,4,5),
    10: (10,1,2,9,8,3,4,7,6,5),
    12: (12,1,2,11,10,3,4,9,8,5,7,6),
    14: (14,1,2,13,12,3,4,11,10,5,6,9,8,7),
    16: (16,1,2,15,14,3,4,13,12,5,6,11,10,7,8,9),
    18: (18,1,2,17,16,3,4,15,14,5,6,13,12,7,8,11,10,9),
    20: (20,1,2,19,18,3,4,17,16,5,6,15,14,7,8,13,12,9,10,11),
    22: (22,1,2,21,20,3,4,19,18,5,6,17,16,7,8,15,14,9,10,13,12,11),
    24: (24,1,2,23,22,3,4,21,20,5,6,19,18,7,8,17,16,9,10,15,14,11,12,13)
}

def split(source_pdf: str, out_dir, skipped):
    base = os.path.basename(source_pdf)
    print(f'Splitting {base}')
    edition_issue = os.path.splitext(base)[0]
    dest_dir = path.join(out_dir, edition_issue)
    os.makedirs(dest_dir, exist_ok=True)

    with open(source_pdf, 'rb') as pdf:
        inputpdf = PdfFileReader(pdf)
        num_pages = inputpdf.numPages
        if num_pages % 2 != 0:
            skipped.append(base)
            return
        conversion = page_order[num_pages]
        for i in range(num_pages):
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(i))
            converted_num = conversion[i]
            page_num = str(converted_num).zfill(4)
            file_name = f'{page_num}.pdf'
            dest_path = path.join(dest_dir, file_name)
            with open(dest_path, 'wb') as outputstream:
                output.write(outputstream)

def main():
    args = parser.parse_args()
    print(args)
    input_dir = args.input_dir
    skipped = []
    for pdf in os.listdir(input_dir):
        input_path = path.join(input_dir, pdf)
        split(input_path, args.output_dir, skipped)
    print(f'Skipped {skipped}')
    

if __name__ == '__main__':
    main()