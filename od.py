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
    r'[a-zA-Z_><=&^%!#$*0-9+\[\]\?\--\/]+'
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
data = '''
    if(a>0){
        c--;
        d++;
    }
    else if(a<0){
        c++;
    }
    else if(k<0){
        k++;
    }
    else{
        fuck;
    }
'''

lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    print(tok)

g = Digraph('G', filename='cluster.gv')

seq = 1
layer = 0
# def p_elseifstmt(p):
#     '''elseifstmt : else '''

def p_allstmt(p):
    '''allstmt : 
               | expression allstmt 
               | ifstmt allstmt  
               | whilestmt allstmt  '''
    if (len(p) == 1):
        print('this is empty allstmt')
    # p[0] = {'headNode': f'{seq}.{layer}','tailNode':f'{seq}.{layer}'}
    if (len(p) == 2):
        p[0]['headNode'] = p[1]['headNode']
        p[0]['tailNode'] = p[1]['headNode']
    elif (len(p) == 3):
        if (not (p[2] is None)):
            p[0] = {'headNode': '','tailNode':''}
            p[0]['headNode'] = p[1]['headNode']
            p[0]['tailNode'] = p[2]['tailNode']
            g.edge(p[1]['tailNode'],p[2]['headNode'])
        else:
            p[0] = {'headNode': '','tailNode':''}
            p[0]['headNode'] = p[1]['headNode']
            p[0]['tailNode'] = p[1]['tailNode']


# def p_stmt(p):
#     '''stmt : expression
#             | expression stmt'''
#     if (len(p) == 1):
#         p[0] = ''
#     elif (len(p) == 3):
#         p[0] = p[1] + p[2]
#     print('Parse stmt!!!', len(p))

# def p_elseifstmt(p):
#     '''elseifstmt : else ifstmt brs'''
#     print('test elseif')


def p_ifstmt(p):
    '''ifstmt : IF LP if_expression RP els LBRACE allstmt RBRACE ers ifelseif
              | IF LP if_expression RP els LBRACE allstmt RBRACE ers'''
    
    if len(p) == 11:
        p[0] = {'headNode': p[3]['headNode'], 'tailNode': p[10]['tailNode']}
        # true
        g.edge(p[3]['tailNode'], p[7]['headNode'], label='true')
        # false
        g.edge(p[3]['tailNode'], p[10]['headNode'], label='false')
    elif len(p) == 10:
        p[0] = {'headNode': p[3]['headNode'], 'tailNode': f'{seq}.{layer}'}
        # true
        g.edge(p[3]['tailNode'], p[7]['headNode'], label='true')





def p_ifelseif(p):
    ''' ifelseif : ELSE IF LP if_expression RP els LBRACE allstmt RBRACE ers gns
                 | ELSE IF LP if_expression RP els LBRACE allstmt RBRACE ers ifelseif gns
                 | ELSE LBRACE allstmt RBRACE gns'''
    if (len(p) == 12):
        # p[0] = {'headNode': p[4]['headNode'], 'tailNode': f'{seq}.{layer}'}
        p[0] = {'headNode': p[4]['headNode'], 'tailNode': p[8]['tailNode']}
        # create edge
        # true
        g.edge(p[4]['tailNode'],p[8]['headNode'],label='true')
    elif len(p) == 13:
        p[0] = {'headNode': p[4]['headNode'], 'tailNode': p[11]['tailNode']}
        # create edge
        # true
        g.edge(p[4]['tailNode'], p[8]['headNode'], label='true')
        # false
        g.edge(p[4]['tailNode'], p[11]['headNode'], label='false')
    elif len(p) == 6:
        p[0] = {'headNode': p[3]['headNode'], 'tailNode': p[3]['tailNode']}



    print('ifelseif in ')



def p_whilestmt(p):
    '''whilestmt : while LP if_expression RP els LBRACE allstmt RBRACE ers allstmt brs'''
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
        

def p_gns(p):
    '''gns : '''

# enter left side scope
def p_els(p):
    '''els : '''
    print('els in')
    global seq
    global layer
    seq += 1
    layer = 0
    p[0] = seq
        # set current scope to left.

# enter right side scope
def p_ers(p):
    '''ers : '''
    print('ers in')
    global seq
    global layer
    seq += 1
    layer = 0
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
    print('else in')


def p_while(p):
    '''while : WHILE'''
    p[0] = 'while'
    print('while in ')

def p_if_exp_p(p):
    ''' if_exp_p :    CONTENT 
                 | LP if_exp_p RP'''
    p[0] = {'Content': ''.join(p[1:])}
    
def p_if_expression(p):
    '''if_expression : if_exp_p'''
    global layer
    if (len(p) == 2):
        p[0] = {'headNode': f'{seq}.{layer}', 'tailNode': f'{seq}.{layer}'}
        # create Node
        g.node(f'{seq}.{layer}',p[1]['Content'])
        layer += 1
    print('if_expression in ')



def p_expression(p):
    '''expression : CONTENT SEMI'''
    global layer
    # draw a node
    g.node(f'{seq}.{layer}', p[1] + p[2])
    p[0] = {'headNode': f'{seq}.{layer}', 'tailNode': f'{seq}.{layer}'}
    layer += 1
    print(''.join(p[1:]))
    print('expression in ')

    
def p_error(p):
    print('error')

# Build the parser
parser = yacc.yacc()

parser.parse(data, lexer=lexer)
g.view()

