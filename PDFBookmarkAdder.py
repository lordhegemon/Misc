import os
from PyPDF2 import PdfFileWriter, PdfFileReader

# Add a bookmark to the first page of each PDF.
def add_bookmark(bookmark_one, directory, filename):
    os.chdir(directory)
    output = PdfFileWriter()
    input = PdfFileReader(open(filename, 'rb'))
    n = input.getNumPages()

    for i in range(n):
        output.addPage(input.getPage(i))
    output.addBookmark(bookmark_one, 0, parent=None)

    # for i in range(n):
    #     output.addPage(input.getPage(i)) if i != 0 else output.addBookmark(bookmark_one, i, parent=None)


    os.chdir(r'C:\Work\Test scripts\PDFBookmarkAdder\results')
    output.setPageMode("/UseOutlines")
    outputStream = open(filename, 'wb')
    output.write(outputStream)
    outputStream.close()

def add_bookmark_directory_parser(bookmark_one, directory):
    for files in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, files)):
            print("\nProcessing - ", os.path.join(directory, files))
            try:
                add_bookmark(bookmark_one, directory, files)
                print("This operation has been completed.")
            except OSError:
                print(files, "had errors")


add_bookmark('OPERATOR-CHG', r'C:\Work\Test scripts\PDFBookmarkAdder', "4304756025.PDF")
# add_bookmark_directory_parser('OPERATOR-CHG', 'DIRECTORY')