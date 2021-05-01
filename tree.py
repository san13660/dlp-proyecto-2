from graphviz import Digraph
from statics import symbols, concat_symbol, epsilon_symbol, unary_operators, binary_operators

class Node:
    current_node_id = 0
    current_symbol_id = 0

    def __init__(self, id, parent, data=None, left=None, right=None):
        self.id = id
        self.data = data
        self.left = left
        self.right = right
        self.parent = parent

        self.nullable = False
        self.first_pos = set()
        self.last_pos = set()
        self.symbol_id = -1

    def print_node(self):
        print('  {}  '.format(self.data))
        print('{}   {}'.format(self.left.data if self.left else '-', self.right.data if self.right else '-'))
    
    def data_ready(self):
        if(len(self.data) > 1):
            return False
        else:
            return True

    def is_leaf(self):
        if(not self.left and not self.right):
            return True
        else:
            return False

    def assign_symbol_id(self):
        if(self.is_leaf):
            self.symbol_id = Node.current_symbol_id
            Node.current_symbol_id += 1

    def graph_node(self, dot, show_pos):
        if(type(self.data) is int):
            label = repr(chr(self.data))
        else:
            label = self.data
        if(show_pos):
            if(len(self.first_pos)>0 and len(self.last_pos)>0):
                label = '{}-{}\n{}'.format(self.first_pos, self.last_pos, self.data)
        dot.node(str(self.id), label)
        if(self.left):
            self.left.graph_node(dot, show_pos)
            dot.edge(str(self.id), str(self.left.id))
        if(self.right):
            self.right.graph_node(dot, show_pos)
            dot.edge(str(self.id), str(self.right.id))

    def graph_tree(self, filename, title, show_pos=False):
        dot = Digraph(comment='The Round Table')
        dot.attr(size='15', label=title, labelloc='t', fontsize='20.0')
        self.graph_node(dot, show_pos)
        dot.render('output/{}.gv'.format(filename), view=True)
        

    @classmethod
    def create_node(cls, parent, data=None, left=None, right=None):
        node = Node(cls.current_node_id, parent, data, left, right)
        cls.current_node_id += 1
        return node

    @classmethod
    def initialize_tree(cls, regex, token):
        cls.current_node_id = 0
        tree = Node(-1, None, data=concat_symbol)
        tree.right = cls.create_node(tree, data='#'+token.id)
        tree.left = cls.create_node(tree, data=regex)        
        return tree

def separate_children(root):
    alphabet = recursive_separate_children(root.left)
    return alphabet

def recursive_separate_children(node):
        alphabet = set()

        letter = find_subnodes(node)
        if(letter):
            alphabet.add(letter)

        if(node.left):
            letter = recursive_separate_children(node.left)
            if(letter):
                alphabet.update(letter)

        if(node.right):
            letter = recursive_separate_children(node.right)
            if(letter):
                alphabet.update(letter)

        return alphabet

def is_inside_parenthesis(data, index):
    open_parenthesis = 0
    for i in range(index+1, len(data)):
        prev_i = i-1 if i>0 else 0
        if(data[i] == ')'  and data[prev_i] != '\\'):
            open_parenthesis += 1
        elif(data[i] == '('  and data[prev_i] != '\\'):
            open_parenthesis -= 1

    if(open_parenthesis == 0):
        return False
    else:
        return True


def find_parentheses(data, p_2):
    #print('Parentesis: ' + data)
    open_p = data.count('(')
    open_p -= data.count('\\(')
    close_p = data.count(')')
    close_p -= data.count('\\)')
    
    if(open_p > close_p):
        raise Exception("Parentesis abierto pero no cerrado")
    
    if(close_p > open_p):
        raise Exception("Parentesis cerrado pero no abierto")

    p_1 = -1
    open_parenthesis = 0
    for i in reversed(range(p_2)):
        prev_i = i-1 if i>0 else 0
        if(data[i] == ')' and data[prev_i] != '\\'):
            open_parenthesis += 1
        elif(data[i] == '(' and data[prev_i] != '\\'):
            if(open_parenthesis > 0):
                open_parenthesis -= 1
            else:
                p_1 = i
                break

    return p_1


def find_subnodes(node):
    #print('Analizando: ' + node.data)
    if(not node.data or len(node.data)==0):
        raise Exception('Sintax Error')

    if(node.data[0] in symbols):
        raise Exception("Syntax Error")

    data = node.data

    if(len(data) == 1):
        if(data not in symbols):
            if(data != epsilon_symbol):
                node.data = data[0]
                return data[0]
            else:
                return None
        else:
            raise Exception("Syntax Error")

    if(len(data) == 2 and data[0] == '\\'):
        node.data = data[1]
        return data[1]

    node_left_data = None
    node_right_data = None

    for i in reversed(range(len(data))):
        prev_i = i-1 if i>0 else 0
        if(data[i] in binary_operators and data[prev_i] != '\\'):
            if(not is_inside_parenthesis(data, i)):
                node_left_data = data[:i]
                node_right_data = data[i+1:]
                node.data = data[i]
                node.left = Node.create_node(node, data=node_left_data)
                node.right = Node.create_node(node, data=node_right_data)
                #print('Nodo: ({}) | c1: {} | c2: {}'.format(node.data, node_left_data, node_right_data))
                return None

    if(data[-1] in unary_operators and data[-2] != '\\'):
        if(data[-2] == ')' and data[-3] != '\\'):
            p_2 = len(data)-2
            p_1 = find_parentheses(data, p_2)
            if(p_1 == 0):
                node_left_data = data[p_1+1:p_2]
                node_right_data = None
                node.data = data[-1]
            else:
                node_left_data = data[:p_1]
                node_right_data = data[p_1:]
                node.data = concat_symbol
        elif(data[-2] not in symbols):
            if(len(data) == 2):
                node_left_data = data[-2]
                node_right_data = None
                node.data = data[-1]
            else:
                node_left_data = data[:-2]
                node_right_data = data[-2:]
                node.data = concat_symbol
        elif(data[-2] in unary_operators and data[-3] != '\\'):
            node_left_data = data[:-1]
            node_right_data = None
            node.data = data[-1]
        else:
            raise Exception("Syntax Error")
    else:
        right_start = -1
        right_end = len(data)
        left_end = -1
        if(data[-1] == ')' and data[-2] != '\\'):
            p_2 = len(data)-1
            p_1 = find_parentheses(data, p_2)
            right_end = p_2
            right_start = p_1 + 1
            left_end = p_1
            if(p_1 == 0):
                node.data = data[right_start:right_end]
                return find_subnodes(node)

        if(data[-2] == '\\'):
            left_end = -2

        node_left_data = data[:left_end]
        node_right_data = data[right_start:right_end]
        node.data = concat_symbol

    node.left = Node.create_node(node, data=node_left_data)
    if(node_right_data):
        node.right = Node.create_node(node, data=node_right_data)

    #if(node.data in unary_operators):
        #print('Nodo: ({}) | c1: {}'.format(node.data, node_left_data))
    #else:
        #print('Nodo: ({}) | c1: {} | c2: {}'.format(node.data, node_left_data, node_right_data))

    return None