#!/usr/bin/env python3

# join_and_reformat.py fügt die Textdateien aus einem Ordner in einer neuen
# Textdatei zusammen.
# 
# Die Syntax ist:
#
#     $ ./join_and_reformat.py <Quellordner> <Zielordner>
#
# Das Skript führt folgende Operationen aus:
#
#     - Alle Zeilen werden in eine große Liste geschrieben. Dabei wird
#       aus den Quelldateien nur verwendet, was oberhalb der Leerzeile
#       gefolgt von drei Geviertstrichen steht ('———'). Alles darunter
#       wird ignoriert.
#       Der Name der Archivquelle wird in eckigen Klammern als SOURCE_ID
#       vorangestellt.
#     - Die Zeilen werden zusammengefügt.
#     - Die Newlines (Zeilenumbrüche) werden entfernt, außer die Zeile
#       endet mit einem Punkt, Doppelpunkt etc. In der überwiegenden Anzahl
#       der Fälle wird so ein Absatzende markiert. Ein Absatz entspricht
#       jetzt einer Zeile.
#     - Leerzeilen bleiben erhalten.
#     - Es werden alle Worttrennungen angezeigt. Der User entscheidet in
#       jedem Fall, wie damit zu verfahren ist. In der Regel kann die
#       Trennung einfach entfernt werden. Ausnahmen sind "ck"-Trennungen
#       als "k-k" oder Worte mit Bindestrichen, die in der Quelle zufällig
#       an einem Zeilenende lagen.
#     - Das Ergebnis wird eine neue Textdatei geschrieben.


import sys
import os
import re

# get positional parameters
input_folder = sys.argv[1]
output_folder = sys.argv[2]

print()
print(f'Verwende Textdateien aus: {input_folder}')
print(f'Schreibe Ergebnis nach: {output_folder}')
print()

# get the input files (one file per page)
input_files = []
for file in os.listdir(input_folder):
    if file.endswith('.txt'):
        input_files.append(file)
input_files = sorted(input_files)
print('Folgende Dateien wurden gefunden:')
for file in input_files:
    print(file)

# join input files in list of lines. start by adding the source id.
# ignore additions at the bottom of the page.
joined_lines = []
for file in input_files:
    with open(os.path.join(input_folder, file), 'r') as textfile:
        current_page = []
        source_id = file.split('.')[0]
        current_page.append(f'[SOURCE_ID:{source_id}]\n')
        for line in textfile:
            current_page.append(line)
        for index, line in enumerate(current_page):
            if line.isspace() and current_page[index + 1] == '———\n':
                break
            else:
                joined_lines.append(line)

# make paragraphs by eliminating newlines when appropriate.
paragraphs = []
paragraph = ''
par_ends = ('.\n', ':\n', '?\n', '!\n', ')\n', '"\n')
for index, line in enumerate(joined_lines):
    if line.isspace():
        paragraphs.append('\n')
        paragraph = ''
    elif line.endswith(par_ends) or joined_lines[index + 1].isspace():
        paragraph = ' '.join([paragraph, line])
        paragraphs.append(paragraph.lstrip())   # or one line par starts with " "
        paragraph = ''
    else:
        if len(paragraph) == 0:
            paragraph = line.rstrip()
        else:
            paragraph = ' '.join([paragraph, line.rstrip()])

# unhyphenate based on user input
print()
print('Im Folgenden werden Worttrennungen zusammengefügt. Die Möglichkeiten sind:\n'
      '    [Enter]   Normale Trennungen. Das Trennzeichen wird gelöscht, die beiden\n'
      '              Worthälften zusammengefügt.\n'
      '       B      Es handelt sich um einen Bindestrich, der erhalten bleiben muss.\n'
      '       N      Sonderfall ohne Änderungsbedarf.\n'
      '       M      Sonderfall, der manuell nachkorrigiert werden muss. Das Trenn-\n'
      '              Zeichen wird durch "####" ersetzt.')
for par_index, paragraph in enumerate(paragraphs):
    words = paragraph.split(' ')
    words_to_remove = []
    for word_index, word in enumerate(words):
        next_word_index = word_index + 1
        try:
            next_word = words[next_word_index]
        except IndexError:
            next_word = None
        if re.search('[a-zäüöß]+-$', word):
            userinput_makes_no_sense  = True
            while userinput_makes_no_sense:
                print(f'\n>>>   {word} {next_word}\n')
                action = input('[Enter] = Trennung aufheben, "B" = Bindestrich, '
                               '"N" = nichts tun, "M" = markieren\n> ')
                if action == '':
                    joined_word = word.rstrip('-') + next_word
                    words[word_index] = joined_word
                    words_to_remove.append(next_word_index)
                    userinput_makes_no_sense  = False
                elif action.upper() == 'N':
                    userinput_makes_no_sense  = False
                    break
                elif action.upper() == 'B':
                    joined_word = word + next_word
                    words[word_index] = joined_word
                    words_to_remove.append(next_word_index)
                    userinput_makes_no_sense  = False
                elif action.upper() == 'M':
                    joined_word = word.rstrip('-') + '####' + next_word
                    words[word_index] = joined_word
                    words_to_remove.append(next_word_index)
                    userinput_makes_no_sense  = False
                else:
                    print('Falsche Eingabe. Bitte noch einmal.\n')
    words_to_remove = sorted(words_to_remove, reverse=True)
    for position in words_to_remove:
        del words[position]
    paragraphs[par_index] = ' '.join(words)

# write reformatted paragraphs to output file
source_id = input_folder.rstrip('/')
output_filename = f'{source_id}_joined.txt'
with open(os.path.join(output_folder, output_filename), 'w') as outfile:
    outfile.writelines(paragraphs)
print(f'Ausgabedatei: {os.path.join(output_folder, output_filename)}')
print('Done.')

