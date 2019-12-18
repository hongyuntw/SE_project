# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex
import ply.yacc as yacc
from graphviz import Digraph
delimiters_dict = {
    '(': 'LP',
    ')': 'RP',
    '{': 'LBRACE',
    '}': 'RBRACE',
    ' ': 'SPACE',
    '/*': 'LCOM',
    '*/': 'RCOM',
    '//': 'COM',
    ';': 'SEMI'
}
keyword_dict = {
    'break': 'BREAK',
    'case': 'CASE',
    'continue': 'CONTINUE',
    'do': 'DO',
    'else': 'ELSE',
    'for': 'FOR',
    'goto': 'GOTO',
    'if': 'IF',
    'return': 'RETURN',
    'switch': 'SWITCH',
    'while': 'WHILE'
}
op_dict = {
}
tokens = ['CONTENT'] + list(op_dict.values()) + list(keyword_dict.values()) + list(delimiters_dict.values())


def t_CONTENT(t):
    r'[a-zA-Z_><=&^%!#$*0-9+\[\]\?\--]+'
    t.type = keyword_dict.get(t.value,'CONTENT')    # Check for reserved words
    return t

# keyword
t_BREAK = r'break'
t_CASE = r'case'
t_CONTINUE = r'continue'
t_DO= r'do'
t_ELSE = r'else'
t_FOR = r'for'
t_GOTO = r'goto'
t_IF = r'if'
t_RETURN = r'return'
t_SWITCH = r'switch'
t_WHILE = r'while'
# de
t_LP = r'\('
t_RP = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SPACE = r'\s'
t_LCOM = r'/\*'
t_RCOM = r'\*/'
t_COM = r'//'
t_SEMI = r';'

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print ("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Test it out
data = '''if(a>3){a++;}else{b++;c++;} k++;'''

lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    print(tok)

g = Digraph('G', filename='cluster.gv')

seq = 1

# def p_elseifstmt(p):
#     '''elseifstmt : else '''

# def p_ifstmt(p):
#     '''ifstmt : if LP if_expression RP els LBRACE stmt RBRACE ers stmt brs'''






def p_stmt(p):
    '''stmt : 
            | expression stmt
            | if LP if_expression RP els LBRACE stmt RBRACE ers stmt brs
            | while LP if_expression RP els LBRACE stmt RBRACE ers stmt brs
            | else LBRACE stmt RBRACE stmt'''
    if (len(p) == 1):
        p[0] = ''
    elif (len(p) == 3):
        p[0] = p[1] + p[2]

    # else .....
    if (len(p) == 5 and p[1] == 'else'):
        p[0] = p[3]
    # while
    if (len(p) == 12 and p[1] == 'while'):
        # judgement
        g.node(str(p[11]), str(p[3]))
        # if true do....
        g.node(str(p[5]), str(p[7]))
        # not break while loop do stmt
        g.node(str(p[9]), str(p[10]))
        
        # true
        g.edge(str(p[11]), str(p[5]),label='true')
        g.edge(str(p[5]), str(p[11]),label='loop')
        # break loop
        g.edge(str(p[11]),str(p[9]),label='false')
        


    #  if ......
    if (len(p) == 12 and p[1]=='if'):
        # els
        g.node(str(p[5]),str(p[7]))
        # ers
        g.node(str(p[9]),str(p[10]))
        # judgement
        g.node(str(p[11]), str(p[3]))
        # link the edge and node
        # lhs
        g.edge(str(p[11]), str(p[9]),label='false')
        # rhs
        g.edge(str(p[11]), str(p[5]),label='true')

        
        

    print('Parse stmt!!!', len(p))
    
# enter left side scope
def p_els(p):
    '''els : '''
    global seq
    seq += 1
    p[0] = seq
        # set current scope to left.

# enter right side scope
def p_ers(p):
    '''ers : '''
    global seq
    seq += 1
    p[0] = seq 
        # set current scope to left.

# back to last layer
def p_brs(p):
    '''brs : '''
    global seq
    p[0] = seq // 2

def p_if(p):
    '''if : IF'''
    p[0] = 'if'
    print('if in ')


def p_else(p):
    '''else : ELSE'''
    p[0] = 'else'
    print('else if in')

def p_while(p):
    '''while : WHILE'''
    p[0] = 'while'
    print('while in ')
    
def p_if_expression(p):
    '''if_expression :  CONTENT 
                     | LP if_expression RP'''
    # if p.slice[1].type == 'CONTENT':
    #     p.slice[0].value = p.slice[1].value
    # elif p.slice[2].type == 'if_expression':
    #     p.slice[0].value = p.slice[2].value
    p[0] = ''.join(p[1:])
    for i in range(1,len(p)):
        print(p[i])
    if (len(p) == 2):
        p[0] = p[1]
    print('if_expression in ')
        
def p_expression(p):
    '''expression : CONTENT SEMI
                  | expression CONTENT SEMI '''
    # for i in range(1,len(p)):
    print(''.join(p[1:]))
    p[0] = ''.join(p[1:])
    print('expression in ')

    
def p_error(p):
    print('error')

# Build the parser
parser = yacc.yacc()

parser.parse(data, lexer=lexer)
g.view()

