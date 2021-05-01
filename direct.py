from statics import concat_symbol, epsilon_symbol
from tree import Node
from automaton import State, Transition, AF
from file_parser import Token

def find_node_stuff(node, symbol_ids):
    if(node.is_leaf()):
        if(node.data == epsilon_symbol):
            node.nullable = True
        else:
            node.nullable = False
            node.assign_symbol_id()
            symbol_ids.append({
                'id':node.symbol_id,
                'symbol':node.data
            })
            node.first_pos = {node.symbol_id}
            node.last_pos = {node.symbol_id}
    else:
        if(len(node.left.first_pos) == 0):
            find_node_stuff(node.left, symbol_ids)
        if(node.right and len(node.right.first_pos) == 0):
            find_node_stuff(node.right, symbol_ids)

        if(node.data == concat_symbol):
            if(node.left.nullable and node.right.nullable):
                node.nullable = True

            node.first_pos.update(node.left.first_pos)
            if(node.left.nullable):
                node.first_pos.update(node.right.first_pos)

            node.last_pos.update(node.right.last_pos)
            if(node.right.nullable):
                node.last_pos.update(node.left.last_pos)
        elif(node.data in '*?'):
            node.nullable = True
            node.first_pos.update(node.left.first_pos)
            node.last_pos.update(node.left.last_pos)
        elif(node.data == '+'):
            if(node.left.nullable):
                node.nullable = True
            node.first_pos.update(node.left.first_pos)
            node.last_pos.update(node.left.last_pos)
        elif(node.data == '|'):
            if(node.left.nullable or node.right.nullable):
                node.nullable = True

            node.first_pos.update(node.left.first_pos)
            node.first_pos.update(node.right.first_pos)

            node.last_pos.update(node.left.last_pos)
            node.last_pos.update(node.right.last_pos)

        #print('Nodo: ({}) | nullable: {} | first_pos: {} | last_pos: {}'.format(node.data, node.nullable, node.first_pos, node.last_pos))

def recursive(afd_direct, current_state, alphabet, symbol_ids, follow_pos_table, final_state_symbol_ids, tokens):
    for letter in alphabet:
        new_state_id = set()

        for symbol_id in symbol_ids:
            if(symbol_id['symbol'] == letter and symbol_id['id'] in current_state.id):
                new_state_id.update(follow_pos_table[symbol_id['id']])
                #print('S:{}   I:{}   IDS:{}'.format(current_state.id, symbol_id['symbol'], new_state_id))

        if(len(new_state_id)==0):
            continue
    
        found_state = None
        for state in afd_direct.states:
            if(state.id == new_state_id):
                found_state = state
                break

        if(found_state):
            afd_direct.transitions.append(Transition(current_state,found_state,letter))
        else:
            new_state = State(new_state_id)
            afd_direct.states.append(new_state)
            afd_direct.transitions.append(Transition(current_state,new_state,letter))

            flag = False
            for id in new_state.id:
                if(str(id) in final_state_symbol_ids):
                    flag = True
                    for token in tokens:
                        if(token.id == final_state_symbol_ids[str(id)]):
                            new_state.tokens.append(token)
                            break
            if(flag):
                afd_direct.final_states.append(new_state)

            recursive(afd_direct,new_state,alphabet,symbol_ids,follow_pos_table,final_state_symbol_ids,tokens)

def find_tree_values(tree, token):
    symbol_ids = []
    find_node_stuff(tree, symbol_ids)

    return tree, symbol_ids

def recursive_follow_pos(current_node, symbol_ids, follow_pos_table):
    for symbol_id in symbol_ids:
        if(current_node.data == concat_symbol and symbol_id['id'] in current_node.left.last_pos):
            follow_pos_table[symbol_id['id']].update(current_node.right.first_pos)
        elif(current_node.data in ['*','+'] and symbol_id['id'] in current_node.last_pos):
            follow_pos_table[symbol_id['id']].update(current_node.first_pos)
    
    if(current_node.left):
        recursive_follow_pos(current_node.left, symbol_ids, follow_pos_table)

    if(current_node.right):
        recursive_follow_pos(current_node.right, symbol_ids, follow_pos_table)

current_node_id = 0
current_node_symbol_id = 0

def recursive_fix_tree_ids(tree):
    global current_node_id
    global current_node_symbol_id

    tree.id = current_node_id
    current_node_id += 1

    if(tree.symbol_id != -1):
        tree.symbol_id = current_node_symbol_id
        current_node_symbol_id += 1
    
    if(tree.left):
        recursive_fix_tree_ids(tree.left)
    if(tree.right):
        recursive_fix_tree_ids(tree.right)

def unite_trees(trees):
    full_tree = Node(-1, None, data='|', left=trees[0], right=trees[1])
    trees[0].parent = full_tree
    trees[1].parent = full_tree

    for i in range(2, len(trees)):
        temp_tree = Node(-1, None, data='|', left=full_tree, right=trees[i])
        full_tree.parent = temp_tree
        trees[i].parent = temp_tree
        full_tree = temp_tree

    recursive_fix_tree_ids(full_tree)

    return full_tree
        

def create_direct_afd(tree, symbol_ids, alphabet, tokens):
    follow_pos_table = {}

    final_state_symbol_ids = {}

    for symbol_id in symbol_ids:
        follow_pos_table[symbol_id['id']] = set()
        if(type(symbol_id['symbol']) is str and len(symbol_id['symbol'])>1 and symbol_id['symbol'].startswith('#')):
            final_state_symbol_ids[str(symbol_id['id'])] = symbol_id['symbol'][1:]

    #print('FINAL: {}'.format(final_state_symbol_ids))

    recursive_follow_pos(tree, symbol_ids, follow_pos_table)

    #print('follow_pos: {}'.format(follow_pos_table))

    afd_direct = AF()

    initial_state = State(tree.first_pos)
    afd_direct.states.append(initial_state)
    afd_direct.initial_state = initial_state

    flag = False
    for id in initial_state.id:
        if(str(id) in final_state_symbol_ids):
            flag = True
            for token in tokens:
                if(token.id == final_state_symbol_ids[str(id)]):
                    initial_state.tokens.append(token)
                    break
    if(flag):
        afd_direct.final_states.append(initial_state)

    current_state = initial_state

    recursive(afd_direct,current_state,alphabet,symbol_ids,follow_pos_table,final_state_symbol_ids, tokens)

    return afd_direct
