# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expr evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex
import ply.yacc as yacc
from graphviz import Digraph


class TailNode:
    def __init__(self, name, label=''):
        self.nodeName = name
        self.outlabel = label


delimiters_dict = {
    '(': 'LP',
    ')': 'RP',
    '{': 'LBRACE',
    '}': 'RBRACE',
    ' ': 'SPACE',
    '/*': 'LCOM',
    '*/': 'RCOM',
    '//': 'COM',
    ';': 'SEMI',
    ':': 'COLON',
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
    'while': 'WHILE',
    'default':'DEFAULT'
}
op_dict = {
}
tokens = ['CONTENT'] + list(op_dict.values()) + \
    list(keyword_dict.values()) + list(delimiters_dict.values())


def t_CONTENT(t):
    r'[a-zA-Z_><=&^%!#$*0-9+\[\]\?\--\/]+'
    t.type = keyword_dict.get(t.value, 'CONTENT')    # Check for reserved words
    return t


# keyword
t_BREAK = r'break'
t_CASE = r'case'
t_CONTINUE = r'continue'
t_DO = r'do'
t_ELSE = r'else'
t_FOR = r'for'
t_GOTO = r'goto'
t_IF = r'if'
t_RETURN = r'return'
t_SWITCH = r'switch'
t_WHILE = r'while'
t_DEFAULT = r'default'
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
t_COLON = r':'

# Define a rule so we can track line numbers


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t+'

# Error handling rule


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Test it out

data = '''
switch(ccc){
    case 4:
    case 5:
        thisis5;
}

'''

casedict = {}
myowndict = {}
lexer.input(data)
need_add_edge = {}
# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break      # No more input
    print(tok)

g = Digraph('G', filename='cluster.gv')
seq = 1
layer = 0
empty = 0
loopflag = False


def GetInitData():
    return {'headNodes': [],
            'tailNodes': []}


def p_stmts(p):
    '''stmts : stmt
             | stmt stmts'''
    p[0] = GetInitData()
    if(len(p) == 2):
        p[0]['headNodes'] = p[1]['headNodes']
        p[0]['tailNodes'] = p[1]['tailNodes']
    if (len(p) == 3):
        p[0]['headNodes'] = p[1]['headNodes']
        p[0]['tailNodes'] = p[2]['tailNodes']
        for startNode in p[1]['tailNodes']:
            for endNode in p[2]['headNodes']:
                g.edge(startNode, endNode)


def p_stmt(p):
    '''stmt :
            | expr
            | ifstmt
            | whilestmt
            | forstmt
            | switch_stmt'''
    global empty
    global myowndict
    p[0] = GetInitData()
    if(len(p) == 1):
        p[0]['headNodes'] = [f'{seq}.{layer}.{empty}']
        p[0]['tailNodes'] = p[0]['headNodes']
        g.node(f'{seq}.{layer}.{empty}', 'empty')
        myowndict[f'{seq}.{layer}.{empty}'] = 'empty'
        empty += 1
    else:
        p[0]['headNodes'] = p[1]['headNodes']
        p[0]['tailNodes'] = p[1]['tailNodes']



def p_switch_stmt(p):
    '''switch_stmt : SWITCH LP CONTENT RP LBRACE case_stmt RBRACE stmt'''
    global myowndict
    global casedict
    p[0] = GetInitData()
    # p0 headnode?
    case_head_node = []
    for head in p[6]['headNodes']:
        text = p[3]
        temp = text + '==' + myowndict[head]
        # 把原本的nodes換掉
        origin_node = '\t' + head
        g.node(head,label=temp,shape='diamond')
        # true link
        # get current head seq and layer
        if (head in casedict):
            g.edge(head,casedict[head],label='true')
        else:

            seq_t = int(head[: head.find('.')])
            layer_t = int(head[head.find('.')+1 :])+1
            belinknode = f'{seq_t}.{layer_t}'
            g.edge(head, belinknode, label='true')
    # false link

    # record the edge
    edgedict = {}
    alreadylink = []

    for i in range(len(p[6]['headNodes'])):
        if not p[6]['headNodes'][i] in casedict:
            try:
                g.edge(p[6]['headNodes'][i], p[6]['headNodes'][i + 1], label='false')
                edgedict[p[6]['headNodes'][i]] = [p[6]['headNodes'][i + 1]]
            except:
                g.edge(p[6]['headNodes'][i], p[8]['headNodes'][0], label='false')
                edgedict[p[6]['headNodes'][i]] = p[8]['headNodes'][0]
    # update casedict
    newcasedict = {}
    for k, v in sorted(list(casedict.items()), key=lambda x:x[0].lower(), reverse=True):
        if v in newcasedict:
            newcasedict[k] = newcasedict[v]
        else:
            newcasedict[k] = v

    for k,v in newcasedict.items():
        g.edge(k, edgedict[v], label='false')
        

    # for i in range(len(p[6]['headNodes'])-1, -1, -1):
    #     if i == len([6]['headNodes']) - 1:
    #         g.edge(p[6]['headNodes'][i], p[8]['headNodes'][0], label='false')
    #     else:
    #         if p[6]['headNodes'][i] in casedict:
    #         else:
    #             g.edge



            

    
    for tail in p[6]['tailNodes']:
        g.edge(tail,p[8]['tailNodes'][0])

    p[0]['headNodes'].append(p[6]['headNodes'][0])
    p[0]['tailNodes'] = p[8]['tailNodes']

    
        

    

def p_case_stmt(p):
    '''case_stmt : CASE bool_expr COLON stmts
                 | DEFAULT COLON stmts
                 | CASE bool_expr COLON stmts case_stmt'''
    p[0] = GetInitData()
    global myowndict
    global casedict
    if len(p) == 5:
        p[0]['headNodes'] = p[2]['headNodes']
        p[0]['tailNodes'] = p[4]['tailNodes']
    elif len(p) == 6:
        if (myowndict[p[4]['headNodes'][0]] == 'empty'):
            casedict[p[2]['headNodes'][0]] = p[5]['headNodes'][0]
            p[0]['headNodes'] = p[2]['headNodes']+ p[5]['headNodes']
            # p[0]['headNodes'] = p[5]['headNodes']+ p[2]['headNodes']
            p[0]['tailNodes'] = p[5]['tailNodes']
        else :
            p[0]['headNodes'] = p[2]['headNodes'] + p[5]['headNodes']
            # p[0]['headNodes'] = p[5]['headNodes'] + p[2]['headNodes']
            p[0]['tailNodes'] = p[4]['tailNodes'] + p[5]['tailNodes']

        


        


def p_ifstmt(p):
    '''ifstmt : IF LP bool_expr RP LBRACE stmts RBRACE elif stmt
              | IF LP bool_expr RP LBRACE stmts RBRACE stmt'''
    p[0] = GetInitData()
    p[0]['headNodes'] = p[3]['headNodes']
    g.edge(p[3]['tailNodes'][0], p[6]['headNodes'][0], label='true')
    if(len(p) == 10):
        p[0]['tailNodes'] = p[9]['tailNodes']
        g.edge(p[3]['tailNodes'][0], p[8]['headNodes'][0], label='false')
        for tail in (p[6]['tailNodes'] + p[8]['tailNodes']):
            g.edge(tail, p[9]['headNodes'][0])
    elif(len(p) == 9):
        p[0]['tailNodes'] = p[8]['tailNodes']
        g.edge(p[3]['tailNodes'][0], p[8]['headNodes'][0], label='false')
        g.edge(p[6]['tailNodes'][0], p[8]['headNodes'][0])


def p_elseif_s(p):
    '''elifs : else
             | elif
             | elif elifs '''
    p[0] = GetInitData()
    if(len(p) == 2):
        p[0] = p[1]
    elif(len(p) == 3):
        p[0]['headNodes'] = p[1]['headNodes']
        p[0]['tailNodes'] = p[1]['tailNodes'] + p[2]['tailNodes']
        g.edge(p[1]['headNodes'][0], p[2]['headNodes'][0], label='false')


def p_elseif(p):
    '''elif : ELSE IF LP bool_expr RP LBRACE stmts RBRACE'''
    p[0] = {'headNodes': p[4]['headNodes'],
            'tailNodes': p[7]['tailNodes']}
    g.edge(p[4]['tailNodes'][0], p[7]['headNodes'][0], label='true')


def p_else(p):
    '''else : ELSE LBRACE stmts RBRACE'''
    p[0] = {'headNodes': p[3]['headNodes'],
            'tailNodes': p[3]['tailNodes']}


def p_whilestmt(p):
    '''whilestmt : WHILE LP bool_expr RP LBRACE stmts RBRACE stmt'''
    p[0] = GetInitData()
    p[0]['headNodes'] = p[3]['headNodes']
    p[0]['tailNodes'] = p[8]['tailNodes']
    # true
    g.edge(p[3]['tailNodes'][0], p[6]['headNodes'][0], label='true')
    # false
    g.edge(p[3]['tailNodes'][0], p[8]['headNodes'][0], label='false')
    # loop
    g.edge(p[6]['tailNodes'][0], p[3]['headNodes'][0], label='loop')


def p_forstmt(p):
    '''forstmt : FOR LP for_expr RP LBRACE stmts RBRACE stmt'''
    p[0] = GetInitData()
    p[0]['headNodes'] = p[3]['initNodes']
    p[0]['tailNodes'] = p[8]['tailNodes']
    g.edge(p[3]['initNodes'][0], p[3]['boolNodes'][0])
    g.edge(p[3]['boolNodes'][0], p[6]['headNodes'][0], label='true')
    g.edge(p[3]['boolNodes'][0], p[8]['headNodes'][0], label='false')
    g.edge(p[6]['tailNodes'][0], p[3]['postNodes'][0], label='For Routine')
    g.edge(p[3]['postNodes'][0], p[3]['boolNodes'][0], label='loop')


def p_for_expr(p):
    '''for_expr : contents SEMI contents SEMI contents'''
    global layer
    p[0] = GetInitData()
    g.node(f'{seq}.{layer}', p[1], shape='box')
    g.node(f'{seq}.{layer+1}', p[3], shape='diamond')
    g.node(f'{seq}.{layer+2}', p[5], shape='box')
    p[0]['initNodes'] = [f'{seq}.{layer}']
    p[0]['boolNodes'] = [f'{seq}.{layer+1}']
    p[0]['postNodes'] = [f'{seq}.{layer+2}']
    layer += 3


def p_bool_expr(p):
    '''bool_expr : contents'''
    global layer
    global myowndict
    p[0] = {'headNodes': [f'{seq}.{layer}'],
            'tailNodes': [f'{seq}.{layer}']}
    # create Node
    g.node(f'{seq}.{layer}', p[1], shape='diamond')
    myowndict[f'{seq}.{layer}'] = p[1]

    layer += 1


def p_expr(p):
    '''expr : contents SEMI'''
    global layer
    global myowndict
    # draw a node
    p[0] = {'headNodes': [f'{seq}.{layer}'],
            'tailNodes': [f'{seq}.{layer}']}
    g.node(f'{seq}.{layer}', p[1] + p[2], shape='box')
    myowndict[f'{seq}.{layer}'] = p[1] + p[2]

    layer += 1
    print(''.join(p[1:]))
    print('expr in ')


def p_contents(p):
    ''' contents : CONTENT 
                 | CONTENT contents'''
    p[0] = ''
    if(len(p) == 2 and not p[1] == None):
        p[0] = p[1]
    elif(len(p) == 3):
        p[0] = p[1] + ' ' + p[2]


def p_error(p):
    print('error')


# Build the parser
parser = yacc.yacc()

parser.parse(data, lexer=lexer)
g.view()
