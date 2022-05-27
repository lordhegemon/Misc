# import os
# from glob import glob
#
# new_path = "C:\\"
# searcher_var = "poster"
# files = glob(new_path + '/**/', recursive=True)
# for i in files:
#     try:
#         for j in os.listdir(i):
#             if searcher_var in j:
#                 print(i, j)
#     except:
#         pass
import urllib, PyPDF2
import cStringIO

wFile = urllib.urlopen('https://bitcoin.org/bitcoin.pdf')
lFile = PyPDF2.pdf.PdfFileReader( cStringIO.StringIO(wFile.read()) )