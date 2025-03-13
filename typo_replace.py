#!/usr/bin/env python3

import os
import sys
import re
import shutil


# input and output
input_file = sys.argv[1]
if not os.path.isfile(input_file):
    print('Falsche Eingabedatei. Syntax: ./typo_replace.py path/to/inputfile')
    sys.exit(1)

# parameters
context_length = 42
replacements = {'HYPHEN-MINUS': r'\s-(\s|,)',
                'QUOTATION MARK open': r'(^|\s)"',
                'QUOTATION MARK close': r'\S"',
                'SINGLE QUOTE open': r"(^|\s)'",
                'SINGLE QUOTE close': r"\S'",
                'APOSTROPHE': r"\S'"}

def show_match_context(txt_stream, start, end):

    """Print match and context in text."""
    
    pos_max = len(txt_stream) - 1
    pos_min = 0
    con_start = max(pos_min, start - context_length)
    con_end = min(pos_max, end + context_length)
    print(f'{txt_stream[con_start:start]}'
          f'\033[01m{txt_stream[start:end]}\033[0m'
          f'{txt_stream[end:con_end]}')


# read the text file
with open(input_file, 'r') as input_text:
    text = input_text.read()

for match_case in replacements:
    pattern = replacements[match_case]
    print(f'\n\n###  {match_case}  ###\n')

    for occurance in re.finditer(pattern, text):
        start, end = occurance.span()
        the_match = occurance.group(0)
        if match_case == 'HYPHEN-MINUS':
            sub_text = text[:start] + the_match.replace('-', '–') + text[start+3:]
            mark_text = text[:start] + the_match.replace('-', '#') + text[start+3:]
        elif match_case == 'QUOTATION MARK open':
            sub_text = text[:start] + the_match.replace('"', '„') + text[start+2:]
            mark_text = text[:start] + the_match.replace('"', '#') + text[start+2:]
        elif match_case == 'QUOTATION MARK close':
            sub_text = text[:start] + the_match.replace('"', '“') + text[start+2:]
            mark_text = text[:start] + the_match.replace('"', '#') + text[start+2:]
        elif match_case == 'SINGLE QUOTE open':
            sub_text = text[:start] + the_match.replace("'", "‚") + text[start+2:]
            mark_text = text[:start] + the_match.replace("'", "#") + text[start+2:]
        elif match_case == 'SINGLE QUOTE close':
            sub_text = text[:start] + the_match.replace("'", "‘") + text[start+2:]
            mark_text = text[:start] + the_match.replace("'", "#") + text[start+2:]
        elif match_case == 'APOSTROPHE':
            sub_text = text[:start] + the_match.replace("'", "’") + text[start+2:]
            mark_text = text[:start] + the_match.replace("'", "#") + text[start+2:]

        print('\nOriginal:')
        show_match_context(text, start, end)
        print('\nÄnderung:')
        show_match_context(sub_text, start, end)
        
        action = input('\n[Enter] = Änderung übernehmen, "M" = markieren, "I" = ignorieren > ')
        if action == '':
            text = sub_text
            print('----> Änderung übernommen.')
            continue
        elif action.upper() == 'M':
            text = mark_text
            print('----> Stelle markiert.')
        else:
            print('----> Nichts geändert.')

# check if the numbers at least match
n_quot_op = text.count('„')
n_quot_cl = text.count('“')
n_squot_op = text.count('‚')
n_squot_cl = text.count('‘')
old_quot = text.count('"')
old_squot = text.count("'")

if n_quot_op != n_quot_cl:
    print('\nWARNING: Mismatch found.')
    print(f'    „ = {n_quot_op}')
    print(f'    “ = {n_quot_cl}')

if n_squot_op != n_squot_cl:
    print('\nWARNING: Mismatch found.')
    print(f'    ‚ = {n_squot_op}')
    print(f'    ‘ = {n_squot_cl}')

if old_quot != 0:
    print('\nWARNING: Some original quotes have survived.')
    print(f'    " = {old_quot}')
if old_squot != 0:
    print('\nWARNING: Some original single quotes have survived.')
    print(f'    " = {old_squot}')

# final warning
input_invalid = True
while input_invalid:
    action = input('\nType "save" to write changes.   > ')
    if action == '':
        continue
    elif action == 'save':
        input_invalid = False
    else:
        print('----> No changes were written to file.\n')
        sys.exit(0) 

# backup the input textfile
print('Backing up the original file.')
shutil.copyfile(input_file, f'{input_file}_before_typo_repl.bak')

# write changed text to file
print('Writing changes to original file.')
with open(input_file, 'w') as outputfile:
    outputfile.write(text)

print('Done.')

