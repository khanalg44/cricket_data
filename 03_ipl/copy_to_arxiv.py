#!/usr/bin/env python3

import numpy as np
import os, sys, glob, subprocess
from shutil import copyfile

def copy_to_arxiv(fil):
    fil_extn = fil.split('.')[-1]
    fil_base = fil.split(fil_extn)[0][:-1]

    if os.path.exists('./arxiv/'+fil):
        print ('File exists in the arxiv. Indexing the file.')
        fils = glob.glob('./arxiv/'+fil_base+'_*')
        new_index = 1
        if len(fils)>0:
            indices = [int(f.split('/')[-1].split(fil_base)[1].split(fil_extn)[0].strip('_').strip('.')) for f in fils]
            max_index = max(indices)
            new_index = max_index+1
            print ('\nAlready present indices: ', indices)

        new_file_name='./arxiv/'+fil_base+'_'+str(new_index)+'.'+fil_extn
        print('\nCopying the pevious file to max index: \t  ./arxiv/'+fil, new_file_name)
        copyfile('./arxiv/'+fil, new_file_name)

    new_file_name = './arxiv/'+fil
    print('\nCopying new file to arxiv: \n', fil, new_file_name)
    copyfile(fil, new_file_name)
        
if __name__=="__main__":

    if len(sys.argv) < 2:
        print ('Please provide the file name to arxiv')
        sys.exit()
    file_to_copy = sys.argv[-1]
    copy_to_arxiv(file_to_copy)
