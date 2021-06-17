import sys
import locale
import ghostscript
import os
import argparse

parser = argparse.ArgumentParser(description='Derive tiffs from the pdfs')
parser.add_argument('input_dir', type=str,
                    help='the directory containing child directories of split pdfs')

def convert_file_to_tiff(path, file):
    file_prefix = os.path.splitext(file)[0]
    input_file = os.path.join(path, file)
    output_file = os.path.join(path, f'{file_prefix}.tif')
    if os.path.exists(output_file):
        print(f'     File {file_prefix}.tif already exists')
        return
    args = [
        "-dNOPAUSE", "-q", "-r300", "-dBATCH",
        "-sDEVICE=tiffgray", "-sCompression=lzw",
        "-sOutputFile=" + output_file,
        "-f",  input_file
        ]

    # arguments have to be bytes, encode them
    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]

    ghostscript.Ghostscript(*args)
    print(f'     Generated {file_prefix}.tif')

def convert_subdir(subdir):
    files: list = sorted(os.listdir(subdir))
    filtered_files = list(filter(lambda x: os.path.splitext(x)[1] == '.pdf', files))
    for file in filtered_files:
        convert_file_to_tiff(subdir, file)

def main():
    args = parser.parse_args()
    input_dir = args.input_dir
    children: list = sorted(os.listdir(input_dir))
    subdirs = list(filter(lambda x: os.path.isdir(os.path.join(input_dir, x)), children))
    for subdir in subdirs:
        print(f'Processing {subdir}')
        convert_subdir(os.path.join(input_dir, subdir))

if __name__ == '__main__':
    main()