from graphviz import Digraph

class State:
    def __init__(self, id, tokens=None):
        self.id = id
        if(tokens):
            self.tokens = tokens
        else:
            self.tokens = []

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, State):
            return self.id == other.id
        return NotImplemented

class Transition:
    def __init__(self, current_state, next_state, symbol):
        self.current_state = current_state
        self.next_state = next_state
        self.symbol = symbol

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Transition):
            if(self.current_state == other.current_state and self.next_state == other.next_state and self.symbol == other.symbol):
                return True
            else:
                return False 
        return NotImplemented

class AF:
    def __init__(self, start_node_id = 0):
        self.states = []
        self.initial_state = None
        self.final_states = []
        self.transitions = []
        self.alphabet = set()
        self.current_node_id = start_node_id

    def create_state(self):
        state = State(self.current_node_id)
        self.current_node_id += 1
        return state

    def create_add_state(self, is_initial=False, is_final=False, tokens=None):
        state = State(self.current_node_id)
        self.current_node_id += 1
        self.states.append(state)
        if(is_initial):
            self.initial_state = state
        if(is_final):
            self.final_states.append(state)
        if(tokens):
            self.tokens = tokens

    def assign_state_numbers(self):
        for transition in self.transitions:
            for state in self.states:
                if(state == transition.current_state):
                    transition.current_state = state
                if(state == transition.next_state):
                    transition.next_state = state

        i = self.current_node_id

        self.initial_state.id = i
        i += 1
        
        for state in self.states:
            if(state != self.initial_state and state not in self.final_states):
                state.id = i
                i += 1

        for state in self.final_states:
            state.id = i
            i += 1

        i = 0

        self.initial_state.id = i
        i += 1
        
        for state in self.states:
            if(state != self.initial_state and state not in self.final_states):
                state.id = i
                i += 1

        for state in self.final_states:
            state.id = i
            i += 1

    def graph_fsm(self, filename, title):
        d = Digraph(comment='Finite State Machine')
        d.attr(rankdir='LR', size='15', label=title, labelloc='t', fontsize='20.0')

        for state in self.states:
            if(state in self.final_states):
                d.attr('node', shape='doublecircle')
            else:
                d.attr('node', shape='circle')
            d.node(str(state.id))

        d.attr('node', shape='plaintext')
        d.node('start', label='')
        d.attr('node', shape='circle')
        d.edge('start', str(self.initial_state.id), label='start')

        for transition in self.transitions:
            d.edge(str(transition.current_state.id), str(transition.next_state.id), label=str(transition.symbol))

        d.render('output/{}.gv'.format(filename), view=True)