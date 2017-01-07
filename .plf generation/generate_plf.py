# -*- coding: utf-8 -*-

from estnltk import analyze
from collections import defaultdict

import ntpath
import os
import sys
 

def generate_plf(in_file,out_file):
    
    
    with open(in_file) as sf, open(out_file,'w') as of:
        
        for line in sf:
            
            # Find lattice represenation of the sentence
            lattice = find_lattice(line)
                    
            # Write lattice into a file         
            write_into_file(lattice,of)

                
def find_lattice(text):

    
    lattice_list = []
    analysis = analyze(text.strip())
        
    # Iterate over all words in analysis
    for word in analysis:
        
        lattice_init = defaultdict(list)
        lattice_final = defaultdict(list)
        
        # Save original word found from text
        original_word = word['text']
        
        # Iterate over different possible forms of the word 
        #for word_form in word['analysis']:
        word_form = word['analysis'][-1]
        ''' 
        Let's consider both lemmatized and original forms of the word
        as alternative choices in lattices 
        '''
        # ------------------------------------------------------------------------ #
        # 1. Lemmatized 
        # ------------------------------------------------------------------------ #
        
        root_tokens_init =  word_form['root_tokens']
        head_root_tokens = root_tokens_init[:-1] 
        lemmatized_ending = [word_form['lemma'][len(''.join(head_root_tokens)):]]
        root_tokens = head_root_tokens + lemmatized_ending
        
        # ------------------------------------------------------------------------ #
        # 2. Original form
        # ------------------------------------------------------------------------ #
        
        if CONFIGURATION == lattice_confs['USE_BOTH'] or CONFIGURATION == lattice_confs['USE_ORIGINAL_FORM']:
            # Exclude the last token as it should contain the case ending, which is removed in analysis:    
            head_tokens = root_tokens[:-1] 
            
            # Find original ending for the last root token:
            original_ending = [original_word[len(''.join(head_tokens)):]]
            
            # Compose new list, where the last root token is substituted with the original ending
            root_tokens_orig = head_tokens + original_ending
            
            if '' in root_tokens_orig:
                root_tokens_orig.remove('')
        # ------------------------------------------------------------------------ #
        

            
        if '' in root_tokens:
            root_tokens.remove('')

        # Find possible segmentations of the word for both lemmatized and original form
        if CONFIGURATION == lattice_confs['USE_BOTH'] or CONFIGURATION == lattice_confs['USE_ORIGINAL_FORM']:
            segments_org = [(''.join(root_tokens_orig[start:end+1]),end-start+1) \
                                      for start in xrange(len(root_tokens_orig)) \
                                      for end in xrange(start, len(root_tokens_orig))]
         
        if CONFIGURATION == lattice_confs['USE_BOTH'] or CONFIGURATION == lattice_confs['USE_LEMMAS']:                
            segments_lem = [(''.join(root_tokens[start:end+1]),end-start+1) \
                                      for start in xrange(len(root_tokens)) \
                                      for end in xrange(start, len(root_tokens))]
                                          
        
        
        
        # Divide segments into a dictionary, where keys represent graph node indices and 
        # the values words starting from node with index i

        if CONFIGURATION == lattice_confs['USE_BOTH'] or \
           CONFIGURATION == lattice_confs['USE_ORIGINAL_FORM']:
            segments = segments_org  
            root_tokens_x = root_tokens_orig
        else:
            segments = segments_lem
            root_tokens_x = root_tokens
            
        i = 0
        # First do it for the original form (or lemmatized version, if that was the only choice)
        for segment in segments:
  
            if segment[0].startswith(root_tokens_x[i]):
                lattice_init[i].append(segment)
                
            else:
                lattice_init[i+1].append(segment)
                i+=1
        
        if CONFIGURATION == lattice_confs['USE_BOTH']:
            i = 0   
            # Now add also the lemmatized version as alternative roots
            for segment in segments_lem:

                if segment[0].startswith(root_tokens[i]):
                    if segment not in lattice_init[i]:
                        lattice_init[i].append(segment)
                    else:
                        continue
                elif segment not in lattice_init[i] and segment not in lattice_init[i+1]:
                    lattice_init[i+1].append(segment)
                    i+=1

        
        # Construct new lattice graph to add edge probabilities
        for node in lattice_init.keys():
            p = round(1/float(len(lattice_init[node])),2)

            for word,d in lattice_init[node]:
                lattice_final[node].append((word,p,d))
 
                  
        lattice_list.append(lattice_final)
    
    return lattice_list

    

def write_into_file(lattice_list,f):
    
    f.write('(')
    for lattice in lattice_list:
        
        sorted_keys = sorted(lattice.keys())
        
        for key in sorted_keys:
            f.write('(')
            for edge in lattice[key]:
                f.write('(')
                for i in range(len(edge)):
                    if type(edge[i]) == unicode:

                        f.write("'"+''.join(edge[i].encode('utf-8').strip())+"'")
                    else:
                        f.write(str(edge[i]))
                    if i != len(edge) - 1:
                        f.write(',')
                        
                f.write('),')
            
            f.write('),')
            
    f.write(')')
    f.write('\n')

      
if __name__ == "__main__":
    
    in_file = sys.argv[1] 
    
    # Choose, if .plf file contains both lemmas and original form as alternative choices or
    # only one of them:
    lattice_confs = {'USE_ORIGINAL_FORM':1,'USE_LEMMAS':2,'USE_BOTH':3}
    
    CONFIGURATION = 3
        
    directory, file_name_ext = ntpath.split(in_file)
    file_name = os.path.splitext(file_name_ext)[0]
    suffix = '.plf'
    out_file = os.path.join(directory,file_name+suffix)

    generate_plf(in_file,out_file)
    

   
   
    