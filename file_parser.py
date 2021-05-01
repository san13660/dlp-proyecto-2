FIND_COMPILER_HEADER = 0
READ_COMPILER_NAME = 1
FIND_CHARACTERS_HEADER = 2
CHARACTER_NAME = 3
CHARACTER_DEFINITION = 4
KEYWORD_NAME = 5
KEYWORD_DEFINITION = 6
TOKEN_NAME = 7
TOKEN_DEFINITION = 8
IGNORE = 9
END = 9

class Token():
    def __init__(self, id, priority, regex, is_keyword=False, except_keywords=False):
        self.id = id
        self.priority = priority
        self.is_keyword = is_keyword
        self.except_keywords = except_keywords
        self.regex = regex

    def __str__(self):
        string_regex = ''
        for r in self.regex:
            if(type(r) is int):
                string_regex += chr(r)
            else:
                string_regex += r
        return 'ID:{} | PRIORITY:{} | REGEX:{}'.format(self.id, self.priority, repr(string_regex))

class CharacterSet:
    def __init__(self, id):
        self.id = id
        self.include = set()
    
    def __contains__(self, key):
        return key in self.include

    def __str__(self):
        return 'ID:{} | SET:{}'.format(self.id, repr(self.include))

    def add(self, s):
        if(type(s) is int):
            self.include.add(s)
        else:
            s = set(s)
            self.include.update(s)

    def discard(self, s):
        if(type(s) is int):
            self.include.discard(s)
        else:
            s = set(s)
            self.include = self.include-s

    def add_any(self):
        for i in range(256):
            self.include.add(i)

    def add_range(self, start, end):
        for i in range(start, end+1):
            self.include.add(i)


def create_keyword(id, string, token_priority):
    print('KEYWORD\n{}: {}'.format(id, string))
    string = string.strip()
    buffer = []
    for s in string:
        if(s == '"' or s == ' '):
            continue
        buffer.append(ord(s))
    
    token = Token(id, token_priority, buffer, is_keyword=True)
    print(token)
    print('')
    return token
    


def create_character_set(id, string, character_sets):
    print('CHARACTER\n{}: {}'.format(id, string))
    string = string.strip()
    inside_quotes = False
    char_range = False
    last_char = -1
    operation = '+'
    character_set = CharacterSet(id)
    buffer = ''
    for s in string:
        if(s == '"' or s== "'"):
            buffer = ''
            inside_quotes = not inside_quotes
            continue

        if(inside_quotes):
            if(char_range):
                    character_set.add_range(last_char,ord(s))
                    last_char = -1
                    char_range = False
            elif(operation == '+'):
                character_set.add(ord(s))
                last_char = int(ord(s))
            elif(operation == '-'):
                character_set.discard(ord(s))
            else:
                raise Exception("Caracter invalido")
            buffer = ''
        else:
            if(s == ' '):
                continue
            if(s == '+'):
                operation = '+'
                continue
            elif(s == '-'):
                operation = '-'
                continue

            if(buffer.startswith('CHR(') and s == ')'):
                if(char_range):
                    character_set.add_range(last_char,int(buffer[4:]))
                    last_char = -1
                    char_range = False
                elif(operation == '+'):
                    character_set.add(int(buffer[4:]))
                    last_char = int(buffer[4:])
                elif(operation == '-'):
                    character_set.discard(int(buffer[4:]))
                else:
                    raise Exception("Caracter invalido")
                operation = ''
                buffer = ''
                continue
            
            buffer += s

            if(buffer=='ANY'):
                character_set.add_any()
                buffer = ''
            elif(buffer=='..'):
                char_range = True
                buffer = ''
            else:
                for c in character_sets:
                    if(buffer==c.id):
                        if(operation == '+'):
                            character_set.add(c.include)
                        elif(operation == '-'):
                            print('DISCARD: {} {}'.format(buffer, c.include))
                            character_set.discard(c.include)
                        else:
                            raise Exception("Caracter invalido")
                        buffer = ''

    print(character_set)
    print('')
    return character_set


def create_token_definition(id, string, character_sets, token_priority):
    print('TOKEN\n{}: {}'.format(id, string))
    string = string.strip()
    buffer = ''

    inside_quotes = False
    except_keywords = False

    regex = []

    for indx in range(len(string)):
        s = string[indx]
        if(s == '"'):
            buffer = ''
            inside_quotes = not inside_quotes
            continue

        if(inside_quotes):
            #if(s in '()|*?+\\'):
                #regex += ord('\\')
            regex.append(ord(s))
            continue
        
        if(s == '{'):
            regex.append('(')
            continue
        elif(s == '}'):
            regex.append(')')
            regex.append('*')
            continue
        elif(s == '['):
            regex.append('(')
            continue
        elif(s == ']'):
            regex.append(')')
            regex.append('?')
            continue
        elif(s == '|'):
            regex.append('|')
            continue
        
        buffer += s

        if(buffer.strip() == 'EXCEPT KEYWORDS'):
            except_keywords = True
            buffer = ''
            continue
        
        if(indx+1 == len(string) or string[indx+1] in ' |}{[]"'):
            for c in character_sets:
                if(buffer.strip()==c.id):
                    regex.append('(')
                    for o in c.include:
                        #if(o in '()|*?+\\'):
                        #    new_string += '\\'
                        regex.append(o)
                        regex.append('|')
                    regex.pop()
                    regex.append(')')
                    buffer = ''
    
    
    token = Token(id, token_priority, regex, except_keywords=except_keywords)
    print(token)
    print('')
    return token

def parse_coco(content):
    ignored_chars = ' '
    string_buffer = ''

    name = ''

    current_state = FIND_COMPILER_HEADER

    current_token_priority = 0

    character_sets = []
    tokens = []

    current_character = ''
    open_quotes = False

    ignore_set = set() 

    for i in range(len(content)):
        char = content[i]
        if(current_character == END):
            break

        if(current_state == FIND_COMPILER_HEADER):
            string_buffer += char
            if(char == '\n'):
                string_buffer = ''
            if(string_buffer == 'COMPILER '):
                current_state = READ_COMPILER_NAME
                string_buffer = ''
        elif(current_state == READ_COMPILER_NAME):
            if(char in ignored_chars):
                continue
            string_buffer += char
            if(char == '\n'):
                name = string_buffer
                print('COMPILER: {}'.format(name))
                string_buffer = ''
                current_state = FIND_CHARACTERS_HEADER
        elif(current_state == FIND_CHARACTERS_HEADER):
            if(char in ignored_chars):
                continue
            if(char == '\n'):
                string_buffer = ''
                continue
            string_buffer += char
            if(string_buffer == 'CHARACTERS'):
                string_buffer = ''
                current_state = CHARACTER_NAME
                print('READING CHARACTERS')
        elif(current_state == CHARACTER_NAME):
            if(char in ignored_chars):
                continue
            if(char == '\n'):
                string_buffer = ''
                continue
            if(char == '='):
                current_character = string_buffer
                string_buffer = ''
                current_state = CHARACTER_DEFINITION
                continue
            
            string_buffer += char
            if(string_buffer == 'KEYWORDS'):
                current_state = KEYWORD_NAME
        elif(current_state == CHARACTER_DEFINITION):
            if(char == '"'):
                open_quotes = not open_quotes
            if(char == '.' and not open_quotes and (content[i+1] != '.' and content[i-1] != '.')):
                character_sets.append(create_character_set(current_character, string_buffer, character_sets))
                string_buffer = ''
                current_state = CHARACTER_NAME
            else:
                string_buffer += char
        elif(current_state == KEYWORD_NAME):
            if(char in ignored_chars):
                continue
            if(char == '\n'):
                string_buffer = ''
                continue
            if(char == '='):
                current_character = string_buffer
                string_buffer = ''
                current_state = KEYWORD_DEFINITION
                continue
            
            string_buffer += char
            if(string_buffer == 'TOKENS'):
                current_state = TOKEN_NAME

        elif(current_state == KEYWORD_DEFINITION):
            if(char == '"'):
                open_quotes = not open_quotes
            if(char == '.' and not open_quotes):
                tokens.append(create_keyword(current_character, string_buffer, current_token_priority))
                current_token_priority += 1
                string_buffer = ''
                current_state = KEYWORD_NAME
            else:
                string_buffer += char
        elif(current_state == TOKEN_NAME):
            if(char in ignored_chars):
                continue
            if(char == '\n'):
                string_buffer = ''
                continue
            if(char == '='):
                current_character = string_buffer
                string_buffer = ''
                current_state = TOKEN_DEFINITION
                continue
            
            string_buffer += char
            if(string_buffer == 'END'):
                current_state = END
            elif(string_buffer.strip() == 'IGNORE'):
                current_state = IGNORE
                string_buffer = ''

        elif(current_state == TOKEN_DEFINITION):
            if(char == '"'):
                open_quotes = not open_quotes
            if(char == '.' and not open_quotes):
                tokens.append(create_token_definition(current_character, string_buffer, character_sets, current_token_priority))
                current_token_priority += 1
                string_buffer = ''
                current_state = TOKEN_NAME
            else:
                string_buffer += char

        elif(current_state == IGNORE):
            if(char == ' ' or char == '\n'):
                for character_set in character_sets:
                    if(character_set.id == string_buffer.strip()):
                        ignore_set = character_set.include
                        current_state = END
                        break
            else:
                string_buffer += char

    return tokens, ignore_set