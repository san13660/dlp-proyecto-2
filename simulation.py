from statics import epsilon_symbol

def verify_token(state, afd, current_word):
    if(state in afd.final_states):
        matched_token = state.tokens[0]
        for token in state.tokens:
            #print('TOKEN {} | PRIORITY {} | EXCEPT_KEY {}'.format(token.id, token.priority, token.except_keywords))
            if((token.priority < matched_token.priority) or
                (not token.is_keyword and not token.except_keywords and matched_token.is_keyword) or
                (token.is_keyword and matched_token.except_keywords)):
                matched_token = token

        print('TOKEN {} : {} {}'.format(matched_token.id, repr(current_word), '(KEYWORD)' if matched_token.is_keyword else ''))
    else:
        print('INVALID TOKEN: {}'.format(repr(current_word)))

def simulate_afd(afd, string):
    current_state = afd.initial_state

    current_word = ''

    i = 0
    while(i < len(string)):
        s = string[i]
        found = False
        current_word += chr(s)
        for transition in afd.transitions:
            if(transition.symbol == s and transition.current_state == current_state):
                current_state = transition.next_state
                found = True
                break
        if(not found):
            if(len(current_word) > 1):
                i -= 1
                current_word = current_word[:-1]
            verify_token(current_state, afd, current_word)
            current_word = ''
            current_state = afd.initial_state
        i += 1
    if(len(current_word) > 0):
        verify_token(current_state, afd, current_word)
    return True


def recursive_simulation(afn, string, current_index, current_state, prev_e_states=[]):
    if(current_index == len(string)):
        if(current_state in afn.final_states):
            return True

    for transition in afn.transitions:
        if(transition.current_state == current_state):
            if(transition.symbol == epsilon_symbol):
                if(transition.next_state not in prev_e_states):
                    new_prev_e_states = prev_e_states.copy()
                    new_prev_e_states.append(current_state)
                    if(recursive_simulation(afn, string, current_index, transition.next_state, new_prev_e_states)):
                        return True
            elif(current_index < len(string) and transition.symbol == string[current_index]):
                if(recursive_simulation(afn, string, current_index+1, transition.next_state)):
                    return True
    
    return False

def simulate_afn(afn, string):
    current_state = afn.initial_state

    if(recursive_simulation(afn, string, 0, current_state)):
        return True
    else:
        return False