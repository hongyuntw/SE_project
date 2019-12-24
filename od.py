
import ply.lex as lex
import ply.yacc as yacc
import math
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
t_ignore  = ' \t+'

# Error handling rule
def t_error(t):
    print ("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()
# '''
data = '''
if(1){
    1;

}
else if(000){
    a--;
    while(check){
        cccc;
    }
}
else{
    a--;
    d--;
    while(kkk){
        cccc;
    }
}
a--;
if(a){
    c==;
}
last;

'''
looplastflag = False
looploca = ''
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


def p_allstmt(p):
    '''allstmt : 
               | expression allstmt 
               | ifstmt allstmt  
               | whilestmt allstmt
               | forstmt allstmt'''
    if (len(p) == 1):
        print('this is empty allstmt')
    # p[0] = {'headNode': f'{seq}.{layer}','tailNode':f'{seq}.{layer}'}
    elif (len(p) == 3):
        print('allstmt in')
        if (not (p[2] is None)):
            p[0] = {'headNode': '','tailNode':''}
            p[0]['headNode'] = p[1]['headNode']
            p[0]['tailNode'] = p[2]['tailNode']
            g.edge(p[1]['tailNode'],p[2]['headNode'])
        else:
            p[0] = {'headNode': '','tailNode':''}
            p[0]['headNode'] = p[1]['headNode']
            p[0]['tailNode'] = p[1]['tailNode']


def p_forstmt(p):
    '''forstmt : for LP for_expression RP els LBRACE allstmt RBRACE ers allstmt'''
    # init
    g.edge(p[3]['initNode'], p[3]['judgeNode'])
    # true
    g.edge(p[3]['judgeNode'], p[7]['headNode'], label='true')
    # judge and do something...
    g.edge(p[7]['tailNode'], p[3]['doNode'])
    g.edge(p[3]['doNode'], p[3]['judgeNode'], label='loop')
    if (p[10] is None):
        p[0] = {'headNode': p[3]['initNode'], 'tailNode': p[7]['tailNode']}

    else:
        p[0] = {'headNode': p[3]['initNode'], 'tailNode': p[10]['tailNode']}
        # false
        g.edge(p[3]['judgeNode'], p[10]['headNode'], label='false')

      
def p_for(p):
    '''for : FOR'''
    print('for in ')

    
def p_for_expression(p):
    '''for_expression : CONTENT SEMI CONTENT SEMI CONTENT'''
    global layer
    global seq
    p[0] = {'initNode': f'{seq}.{layer}', 'judgeNode': f'{seq}.{layer+1}', 'doNode': f'{seq}.{layer+2}'}
    # create Node
    g.node(f'{seq}.{layer}', p[1],shape='box')
    g.node(f'{seq}.{layer+1}',p[3],shape='diamond')
    g.node(f'{seq}.{layer+2}',p[5],shape='box')
    layer = 0
    seq += 1
    print('for_expression in')


def p_ifstmt(p):
    '''ifstmt : IF LP if_expression RP els LBRACE allstmt RBRACE ers ifelseif gns
              | IF LP if_expression RP els LBRACE allstmt RBRACE ers allstmt'''
    global looplastflag
    global looploca
    if len(p) == 12:
        p[0] = {'headNode': p[3]['headNode'], 'tailNode': p[10]['tailNode']}
        # true
        g.edge(p[3]['tailNode'], p[7]['headNode'], label='true')
        # false
        g.edge(p[3]['tailNode'], p[10]['headNode'], label='false')

        # edge
        # 這邊代表if else if那邊還有下一層應該要連線，反之其實就是ifelseif後面沒東西了
        if math.floor(float(p[10]['headNode'])) != math.floor(float(p[10]['tailNode'])):
            g.edge(p[7]['tailNode'], p[10]['tailNode'])


    elif len(p) == 11:
        # true
        g.edge(p[3]['tailNode'], p[7]['headNode'], label='true')
        # 最後還有東西
        if not (p[10] is None):
            # tail or head tbd..
            p[0] = {'headNode': p[3]['headNode'], 'tailNode': p[10]['tailNode']}
            # false
            g.edge(p[3]['tailNode'], p[10]['headNode'], label='false')
            #  link
            # looplast
            if looplastflag and p[7]['tailNode']==looploca:
                g.edge(p[7]['tailNode'], p[10]['headNode'], label='false')
                looplastflag = False
            else:
                g.edge(p[7]['tailNode'], p[10]['headNode'])
        # 最後沒東西了
        else:
            p[0] = {'headNode': p[3]['headNode'], 'tailNode': p[7]['tailNode']}

            





def p_ifelseif(p):
    ''' ifelseif : ELSE IF LP if_expression RP els LBRACE allstmt RBRACE ers allstmt
                 | ELSE IF LP if_expression RP els LBRACE allstmt RBRACE ers ifelseif gns
                 | ELSE els LBRACE allstmt RBRACE ers allstmt'''
    global looplastflag
    global looploca
    if (len(p) == 12):
        # true
        g.edge(p[4]['tailNode'], p[8]['headNode'], label='true')
        # 最後一個allstmt有東西
        if not (p[11] is None):
            if looplastflag and p[8]['tailNode'] == looploca:
                g.edge(p[8]['tailNode'], p[11]['headNode'], label='false')
                looplastflag = False
            else:
                g.edge(p[8]['tailNode'], p[11]['headNode'])
            
            g.edge(p[4]['tailNode'], p[11]['headNode'], label='false')
            p[0] = {'headNode': p[4]['headNode'], 'tailNode': p[11]['headNode']}
        else:
            p[0] = {'headNode': p[4]['headNode'], 'tailNode': p[8]['tailNode']}

    elif len(p) == 13:
        p[0] = {'headNode': p[4]['headNode'], 'tailNode': p[11]['tailNode']}
        # true
        g.edge(p[4]['tailNode'], p[8]['headNode'], label='true')
        # false
        g.edge(p[4]['tailNode'], p[11]['headNode'], label='false')
        # 這邊判斷後面的ifelseif是不是同一層？是的話代表其實後面沒有其他stmt,不用特別連，是的話要連
        if math.floor(float(p[11]['headNode'])) != math.floor(float(p[11]['tailNode'])):
            g.edge(p[8]['tailNode'], p[11]['tailNode'])


    elif len(p) == 8:
        # 最後一個allstmt有東西
        if not (p[7] is None):
            if looplastflag and p[4]['tailNode'] ==looploca:
                looplastflag= False
                g.edge(p[4]['tailNode'], p[7]['headNode'], label='false')
            else:
                g.edge(p[4]['tailNode'], p[7]['headNode'])
            p[0] = {'headNode': p[4]['headNode'], 'tailNode': p[7]['headNode']}
        else:
            p[0] = {'headNode': p[4]['headNode'], 'tailNode': p[4]['tailNode']}


    print('ifelseif in ')



def p_whilestmt(p):
    '''whilestmt : while LP if_expression RP els LBRACE allstmt RBRACE ers allstmt'''
    global looplastflag
    global looploca
    looplastflag = False
    if len(p) == 11:
        # true
        g.edge(p[3]['tailNode'], p[7]['headNode'], label='true')
        # mark loop
        g.edge(p[7]['tailNode'], p[3]['headNode'], label='loop')
        if not (p[10] is None):
            p[0] = {'headNode': p[3]['headNode'], 'tailNode': p[10]['headNode']}
            # false
            g.edge(p[3]['tailNode'], p[10]['headNode'], label='false')
        # 後面沒東西
        else:
            # origin tail = p[7]
            p[0] = {'headNode': p[3]['headNode'], 'tailNode': p[3]['tailNode']}
            looplastflag = True
            looploca = p[3]['tailNode']
            
        



        

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
        g.node(f'{seq}.{layer}',p[1]['Content'],shape='diamond')
        layer += 1
    print('if_expression in ')



def p_expression(p):
    '''expression : CONTENT SEMI'''
    global layer
    # draw a node
    g.node(f'{seq}.{layer}', p[1] + p[2],shape='box')
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

