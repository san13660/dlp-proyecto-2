from graphviz import Digraph
from tree import Node, separate_children
from automaton import State, Transition, AF
from direct import find_tree_values, create_direct_afd, unite_trees
from simulation import simulate_afd, simulate_afn
from file_parser import parse_coco

import time
import traceback
import sys

if(len(sys.argv) != 2):
    print('ARGUMENTOS INVALIDOS')
    exit()

filename = sys.argv[1]
flag = True
ignore_set = set()
while(flag):
    try:
        with open(filename, encoding='utf-8') as fp:
            content = fp.read()
        tokens, ignore_set = parse_coco(content)
        flag = False
    except:
        print('-ERROR AL ABRIR EL ARCHIVO-\n')

try:
    #check_for_errors(rules)
    #rules = fix_errors(rules)

    print('\n---Creando arbol---\n')

    trees = []
    symbol_ids_l = []
    alphabet = set()

    for token in tokens:
        tree = Node.initialize_tree(token.regex, token)
        alphabet.update(separate_children(tree))
        trees.append(tree)
    
    
    full_tree = unite_trees(trees)
    full_tree, symbol_ids = find_tree_values(full_tree, token)

    #print('SYMBOLS: {}'.format(symbol_ids))
    #print('ALPHABET: {}'.format(alphabet))

    full_tree.graph_tree('Arbol_Directo', 'Arbol (Directo) - {}'.format(filename))

    print('\n---Creando AFD por metodo directo---\n')

    afd_direct = create_direct_afd(full_tree,symbol_ids,alphabet,tokens)
    afd_direct.assign_state_numbers()
    #afd_direct.graph_fsm('AFD_Directo', 'AFD (Directo) - {}'.format('ss'))

    flag=False
except Exception as e:
    print(traceback.format_exc())
    print('\n** ERROR: {} **'.format(e))


new_file = '''
from automaton import State, Transition, AF
from simulation import simulate_afd
from file_parser import Token
import sys

afd = AF()
'''

for state in afd_direct.states:
    new_file += 'tokens = []\n'
    for token in state.tokens:
        new_file += 'tokens.append(Token(id="{}", priority={}, regex=[], is_keyword={}, except_keywords={}))\n'.format(token.id, token.priority, token.is_keyword, token.except_keywords)
    new_file += 'state = State({}, tokens)\n'.format(state.id)
    new_file += 'afd.states.append(state)\n'
    if(state == afd_direct.initial_state):
        new_file += 'afd.initial_state = state\n'
    if(state in afd_direct.final_states):
        new_file += 'afd.final_states.append(state)\n'

new_file += 'transitions = []\n'
for transition in afd_direct.transitions:
    new_file += 'transition = Transition(current_state=State({}), next_state=State({}), symbol={})\n'.format(transition.current_state.id, transition.next_state.id, transition.symbol)
    new_file += 'transitions.append(transition)\n'

new_file += 'afd.transitions = transitions\n'
new_file += 'afd.assign_state_numbers()\n'
new_file += 'ignore_set = set({})\n'.format(ignore_set)
new_file += '''
print(sys.argv)
if(len(sys.argv) == 2):
    filename = sys.argv[1]
    with open(filename, encoding='utf-8') as fp:
                string = fp.read()
    print("")
    print("---------------------------------------")
    print("")

    char_array = []

    for s in string:
        if(ord(s) not in ignore_set):
            char_array.append(ord(s))

    print("")

    result_afd_direct = simulate_afd(afd, char_array)
else:
    print('ARGUMENTOS INVALIDOS')
'''

with open('scanner.py', 'w', encoding='utf-8') as fp:
    fp.write(new_file)

print('\n----------------scanner.py CREADO----------------')