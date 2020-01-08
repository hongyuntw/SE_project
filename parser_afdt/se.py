# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expr evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex
import ply.yacc as yacc
from graphviz import Digraph


# Build the graph
g = Digraph()

data = '''
switch(a){
    case 1:
        a++;
        break;
    case 2:
    case 3:
        a--;
        break;
    default:
        d--;
        break;

}
abcd;
'''

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
    'case': 'CASE',
    'do': 'DO',
    'else': 'ELSE',
    'for': 'FOR',
    'goto': 'GOTO',
    'if': 'IF',
    'switch': 'SWITCH',
    'while': 'WHILE',
    'default': 'DEFAULT'
}
op_dict = {
}

tokens = list(keyword_dict.values()) + \
    list(delimiters_dict.values()) \
    + ['CONTENT']

# keyword
t_CASE = r'case'
t_DO = r'do'
t_ELSE = r'else'
t_FOR = r'for'
t_GOTO = r'goto'
t_IF = r'if'
t_SWITCH = r'switch'
t_WHILE = r'while'
t_DEFAULT = r'default'
# de
t_LP = r'\('
t_RP = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI = r';'
t_COLON = r':'

# Define a rule so we can track line numbers


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'
t_ignore_LINE_COMMENT = r'\/\/.+\n'
t_ignore_LINES_COMMENT = r'\/\*(.|\n)+\*\/'


def t_CONTENT(t):
    r'[a-zA-Z0-9_><=&\^%\!#$\\\*\+\-\[\]\?\|,]+'
    # r'[a-zA-Z0-9\^\+\[\]\?\-\|,=<>]+'
    t.type = keyword_dict.get(t.value, 'CONTENT')    # Check for reserved words
    print(t)
    return t


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Test it out


# global
casedict = {}
myowndict = {}
need_add_edge = {}
defaultnodes = {}
# 記錄每個node and edge for最後empty處理的部分
alledge = []
allnode = {}
seq = 1
layer = 0
empty = 0
loopflag = False
# break資訊
breaknodes = []
skipbreaknodes = []

previous_node = ''
skipbreaknodes = []
# Tokenize
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(tok)


def GetInitData():
    return {'headNodes': [],
            'tailNodes': []}


def p_stmts(p):
    '''stmts : stmt
             | stmt stmts'''
    global alledge
    global allnode
    global breaknodes
    global skipbreaknodes
    p[0] = GetInitData()
    if (len(p) == 2):
        p[0]['headNodes'] = p[1]['headNodes']
        p[0]['tailNodes'] = p[1]['tailNodes']
        # if allnode[p[1]['headNodes'][0]][0] == 'break;':
        #     breaknodes.append(p[1]['headNodes'][0])
    if (len(p) == 3):
        # check breaknodes
        for startNode in p[1]['tailNodes']:
            for endNode in p[2]['headNodes']:
                # if endNode in breaknodes:
                #     skipbreaknodes.append(startNode)
                # else:
                if not startNode in skipbreaknodes:
                    g.edge(startNode, endNode)
                    alledge.append((startNode, endNode, ''))
        # if p[2]['headNodes'][0] in breaknodes:
        #     p[0]['headNodes'] = p[1]['headNodes']
        #     p[0]['tailNodes'] = p[1]['tailNodes']
        # else:
        p[0]['headNodes'] = p[1]['headNodes']
        p[0]['tailNodes'] = p[2]['tailNodes']


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
        allnode[f'{seq}.{layer}.{empty}'] = ('empty', '')
        myowndict[f'{seq}.{layer}.{empty}'] = 'empty'
        empty += 1
    else:
        p[0]['headNodes'] = p[1]['headNodes']
        p[0]['tailNodes'] = p[1]['tailNodes']


def p_switch_stmt(p):
    '''switch_stmt : SWITCH LP bool_expr RP LBRACE case_stmt RBRACE stmt'''
    global myowndict
    global casedict
    global alledge
    global layer
    global skipbreaknodes
    global defaultnodes
    flag = False
    p[0] = GetInitData()

    tp = allnode[p[3]['headNodes'][0]]
    allnode[p[3]['headNodes'][0]] = (tp[0], 'house')

    # p0 headnode?
    edgedict = {}
    for head in p[6]['headNodes']:
        g.edge(p[3]['tailNodes'][0], head, label='switch')
        alledge.append((p[3]['tailNodes'][0], head, 'switch'))
        if (head in casedict):
            pass
        elif head in defaultnodes and defaultnodes[head][0] in skipbreaknodes and not(defaultnodes[head][0] in allnode):
            g.edge(head, p[8]['headNodes'][0], label='break')
            alledge.append((head, p[8]['headNodes'][0], 'break'))
        else:
            seq_t = int(head[: head.find('.')])
            layer_t = int(head[head.find('.')+1:])+1
            belinknode = f'{seq_t}.{layer_t}'
            if(head in defaultnodes):
                g.edge(head, defaultnodes[head][-1])
                alledge.append((head, defaultnodes[head][-1], ''))
                flag = True
            else:
                g.edge(head, belinknode)
                alledge.append((head, belinknode, ''))
                edgedict[head] = belinknode
    newcasedict = {}
    i = 0
    count = 0
    keys = casedict.keys()
    keys = list(keys)
    keys = [k for k in keys if k in p[6]['headNodes']]
    while (1):
        try:
            k = keys[i]
            v = casedict[k]
            newcasedict[k] = edgedict[v]
            edgedict[k] = edgedict[v]
            count += 1
            i += 1
            i = i % len(keys)
            if (count >= len(keys)):
                break
        except:
            i += 1
            if len(keys) > 0:
                i = i % len(keys)
            if (count >= len(keys)):
                break

    for k, v in newcasedict.items():
        g.edge(k, newcasedict[k])
        alledge.append((k, newcasedict[k], ''))

    for tail in p[6]['tailNodes']:
        if (tail in skipbreaknodes):
            g.edge(tail, p[8]['tailNodes'][0], label='break')
            alledge.append((tail, p[8]['tailNodes'][0], 'break'))
        else:
            g.edge(tail, p[8]['tailNodes'][0])
            alledge.append((tail, p[8]['tailNodes'][0], ''))
    p[0]['headNodes'].append(p[3]['headNodes'][0])
    p[0]['tailNodes'] = p[8]['tailNodes']
    if (not flag):
        g.edge(p[3]['headNodes'][0], p[8]['headNodes'][0])
        alledge.append((p[3]['headNodes'][0], p[8]['headNodes'][0], ''))


def p_case_stmt(p):
    '''case_stmt : CASE bool_expr COLON stmts
                 | DEFAULT COLON stmts
                 | CASE bool_expr COLON stmts case_stmt'''
    p[0] = GetInitData()
    global myowndict
    global casedict
    global defaultnodes
    global layer
    global alledge
    global allnode
    global skipbreaknodes
    if len(p) == 5:
        p[0]['headNodes'] = p[2]['headNodes']
        p[0]['tailNodes'] = p[4]['tailNodes']
    elif len(p) == 4:
        print('default')
        g.node(f'{seq}.{layer}', label='default', shape='box')
        allnode[f'{seq}.{layer}'] = ('default', 'box')
        p[0]['headNodes'].append(f'{seq}.{layer}')
        p[0]['tailNodes'] = p[3]['tailNodes']
        defaultnodes[f'{seq}.{layer}'] = p[3]['headNodes']
        # if p[3]['headNodes'] in skipbreaknodes:
        #     g.edge(p[3]['headNodes'][0],p[8]['headNodes'][0])
        #     alledge.append((p[3]['headNodes'][0], p[8]['headNodes'][0], ''))
        layer += 1

    elif len(p) == 6:
        if (myowndict[p[4]['headNodes'][0]] == 'empty'):
            casedict[p[2]['headNodes'][0]] = p[5]['headNodes'][0]
            p[0]['headNodes'] = p[2]['headNodes'] + p[5]['headNodes']
            # p[0]['headNodes'] = p[5]['headNodes']+ p[2]['headNodes']
            p[0]['tailNodes'] = p[5]['tailNodes']
        else:
            p[0]['headNodes'] = p[2]['headNodes'] + p[5]['headNodes']
            # p[0]['headNodes'] = p[5]['headNodes'] + p[2]['headNodes']
            p[0]['tailNodes'] = p[4]['tailNodes'] + p[5]['tailNodes']


def p_ifstmt(p):
    '''ifstmt : IF LP bool_expr RP stmt_block elifs stmt
              | IF LP bool_expr RP stmt_block stmt'''
    global alledge
    p[0] = GetInitData()
    p[0]['headNodes'] = p[3]['headNodes']
    g.edge(p[3]['tailNodes'][0], p[5]['headNodes'][0], label='true')
    alledge.append((p[3]['tailNodes'][0], p[5]['headNodes'][0], 'true'))

    if(len(p) == 8):
        p[0]['tailNodes'] = p[7]['tailNodes']
        g.edge(p[3]['tailNodes'][0], p[6]['headNodes'][0], label='false')
        alledge.append((p[3]['tailNodes'][0], p[6]['headNodes'][0], 'false'))
        for tail in (p[5]['tailNodes'] + p[6]['tailNodes']):
            g.edge(tail, p[7]['headNodes'][0])
            alledge.append((tail, p[7]['headNodes'][0], ''))
    elif(len(p) == 7):
        p[0]['tailNodes'] = p[6]['tailNodes']
        g.edge(p[3]['tailNodes'][0], p[6]['headNodes'][0], label='false')
        alledge.append((p[3]['tailNodes'][0], p[6]['headNodes'][0], 'false'))
        g.edge(p[5]['tailNodes'][0], p[6]['headNodes'][0])
        alledge.append((p[5]['tailNodes'][0], p[6]['headNodes'][0], ''))


def p_stmt_block(p):
    ''' stmt_block :  LBRACE stmts RBRACE
                    | stmt '''
    if(len(p) == 4):
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_elseif_s(p):
    '''elifs : else
             | elif
             | elif elifs '''
    p[0] = GetInitData()
    global alledge
    if(len(p) == 2):
        p[0] = p[1]
    elif(len(p) == 3):
        p[0]['headNodes'] = p[1]['headNodes']
        p[0]['tailNodes'] = p[1]['tailNodes'] + p[2]['tailNodes']
        g.edge(p[1]['headNodes'][0], p[2]['headNodes'][0], label='false')
        alledge.append((p[1]['headNodes'][0], p[2]['headNodes'][0], 'false'))


def p_elseif(p):
    '''elif : ELSE IF LP bool_expr RP stmt_block'''
    global alledge
    p[0] = {'headNodes': p[4]['headNodes'],
            'tailNodes': p[6]['tailNodes']}
    g.edge(p[4]['tailNodes'][0], p[6]['headNodes'][0], label='true')
    alledge.append((p[4]['tailNodes'][0], p[6]['headNodes'][0], 'true'))


def p_else(p):
    '''else : ELSE stmt_block'''
    print('else in')
    p[0] = {'headNodes': p[2]['headNodes'],
            'tailNodes': p[2]['tailNodes']}


def p_whilestmt(p):
    '''whilestmt : WHILE LP bool_expr RP stmt_block stmt'''
    p[0] = GetInitData()
    global alledge
    global skipbreaknodes
    p[0]['headNodes'] = p[3]['headNodes']
    p[0]['tailNodes'] = p[6]['tailNodes']
    # true
    g.edge(p[3]['tailNodes'][0], p[5]['headNodes'][0], label='true')
    alledge.append((p[3]['tailNodes'][0], p[5]['headNodes'][0], 'true'))
    # false
    g.edge(p[3]['tailNodes'][0], p[6]['headNodes'][0], label='false')
    alledge.append((p[3]['tailNodes'][0], p[6]['headNodes'][0], 'false'))

    if p[5]['tailNodes'][0] in skipbreaknodes:
        # break
        g.edge(p[5]['tailNodes'][0], p[6]['headNodes'][0], label='break')
        alledge.append((p[5]['tailNodes'][0], p[6]['headNodes'][0], 'break'))
    else:
        # loop
        g.edge(p[5]['tailNodes'][0], p[3]['headNodes'][0], label='loop')
        alledge.append((p[6]['tailNodes'][0], p[3]['headNodes'][0], 'loop'))


def p_forstmt(p):
    '''forstmt : FOR LP for_expr RP stmt_block stmt'''
    global alledge
    p[0] = GetInitData()
    p[0]['headNodes'] = p[3]['initNodes']
    p[0]['tailNodes'] = p[6]['tailNodes']
    g.edge(p[3]['initNodes'][0], p[3]['boolNodes'][0])
    alledge.append((p[3]['initNodes'][0], p[3]['boolNodes'][0], ''))

    g.edge(p[3]['boolNodes'][0], p[5]['headNodes'][0], label='true')
    alledge.append((p[3]['boolNodes'][0], p[5]['headNodes'][0], 'true'))

    g.edge(p[3]['boolNodes'][0], p[6]['headNodes'][0], label='false')
    alledge.append((p[3]['boolNodes'][0], p[6]['headNodes'][0], 'false'))

    if p[5]['tailNodes'][0] in skipbreaknodes:
        g.edge(p[5]['tailNodes'][0], p[6]['headNodes'][0], label='break')
        alledge.append((p[5]['tailNodes'][0], p[6]['headNodes'][0], 'break'))
        g.edge(p[5]['tailNodes'][0], p[3]['postNodes'][0], label='For Routine')
        alledge.append((p[5]['tailNodes'][0], p[3]
                        ['postNodes'][0], 'For Routine'))
        g.edge(p[3]['postNodes'][0], p[6]['headNodes'][0], label='break')
        alledge.append((p[3]['postNodes'][0], p[6]['headNodes'][0], 'break'))
    else:
        g.edge(p[5]['tailNodes'][0], p[3]['postNodes'][0], label='For Routine')
        alledge.append((p[5]['tailNodes'][0], p[3]
                        ['postNodes'][0], 'For Routine'))

    g.edge(p[3]['postNodes'][0], p[3]['boolNodes'][0], label='loop')
    alledge.append((p[3]['postNodes'][0], p[3]['boolNodes'][0], 'loop'))


def p_for_expr(p):
    '''for_expr : contents SEMI contents SEMI contents'''
    global layer
    global allnode
    p[0] = GetInitData()
    g.node(f'{seq}.{layer}', p[1], shape='box')
    allnode[f'{seq}.{layer}'] = (p[1], 'box')
    g.node(f'{seq}.{layer+1}', p[3], shape='diamond')
    allnode[f'{seq}.{layer+1}'] = (p[3], 'diamond')
    g.node(f'{seq}.{layer+2}', p[5], shape='box')
    allnode[f'{seq}.{layer+2}'] = (p[5], 'box')
    p[0]['initNodes'] = [f'{seq}.{layer}']
    p[0]['boolNodes'] = [f'{seq}.{layer+1}']
    p[0]['postNodes'] = [f'{seq}.{layer+2}']
    layer += 3


def p_bool_expr(p):
    '''bool_expr : contents'''
    global layer
    global myowndict
    global allnode
    p[0] = {'headNodes': [f'{seq}.{layer}'],
            'tailNodes': [f'{seq}.{layer}']}
    # create Node
    g.node(f'{seq}.{layer}', p[1], shape='diamond')
    allnode[f'{seq}.{layer}'] = (p[1], 'diamond')
    myowndict[f'{seq}.{layer}'] = p[1]
    layer += 1


def p_expr(p):
    '''expr : contents SEMI
            | func_expr SEMI'''
    global previous_node
    global skipbreaknodes
    global layer
    global myowndict
    # draw a node

    name = ''.join(p[1:])
    if name == 'break;':
        p[0] = {'headNodes': [previous_node],
                'tailNodes': [previous_node]}
        skipbreaknodes.append(previous_node)
    else:
        p[0] = {'headNodes': [f'{seq}.{layer}'],
                'tailNodes': [f'{seq}.{layer}']}
        g.node(f'{seq}.{layer}', name, shape='box')
        allnode[f'{seq}.{layer}'] = (name, 'box')
        myowndict[f'{seq}.{layer}'] = name
        previous_node = f'{seq}.{layer}'
        layer += 1
        print(''.join(p[1:]))
        print('expr in ')


def p_func(p):
    '''func_expr : contents LP params RP'''
    p[0] = ''.join(p[1:])


def p_param(p):
    '''param : contents
             | func_expr '''
    p[0] = ''.join(p[1:])


def p_params(p):
    '''params : param
              | param params'''
    p[0] = ''.join(p[1:])


def p_contents(p):
    ''' contents : CONTENT 
                 | CONTENT contents'''
    p[0] = ''
    if(len(p) == 2 and not p[1] == None):
        p[0] = p[1]
    elif(len(p) == 3):
        p[0] = p[1] + ' ' + p[2]


def p_error(p):
    raise 'Cannot Parse'
    # print('error')


# Build the lexer
lexer = lex.lex()
# Build the parser
parser = yacc.yacc()


def resetGlobals():
    global casedict
    global myowndict
    global need_add_edge
    global defaultnodes
    global alledge
    global allnode
    global seq
    global layer
    global empty
    global loopflag
    global breaknodes
    global skipbreaknodes
    global previous_node
    global skipbreaknodes
    casedict = {}
    myowndict = {}
    need_add_edge = {}
    defaultnodes = {}
    # 記錄每個node and edge for最後empty處理的部分
    alledge = []
    allnode = {}
    seq = 1
    layer = 0
    empty = 0
    loopflag = False
    # break資訊
    breaknodes = []
    skipbreaknodes = []
    previous_node = ''
    skipbreaknodes = []


def analysis_tool(code=data):
    global parser
    global lexer
    global g
    #
    g = Digraph(name='rawGraph', comment='Unprocessed Graph')
    # create a new graph without empty
    newg = Digraph(name='trueGraph', comment='Processed Graph')
    #
    resetGlobals()
    #
    parser.parse(code, lexer=lexer)

    emptylist = []
    for k, v in allnode.items():
        if v[0] != 'empty':
            newg.node(k, v[0].replace(';', ''), shape=v[1])
        else:
            emptylist.append(k)

    # 處理empty node
    for emptynode in emptylist:
        origin_empty_node = emptynode
        # tp = tuple
        for tp in alledge:
            startnode = tp[0]
            endnode = tp[1]
            label = tp[2]
            # 有連到empty的
            # a -> empty
            if endnode == emptynode and not (startnode in emptylist):
                # a->empty->b
                # a->empty->empty->b
                # 把a->b
                while (1):
                    flag = False
                    count = 0
                    # tp = tuple
                    for tp2 in alledge:
                        startnode2 = tp2[0]
                        endnode2 = tp2[1]
                        label2 = tp2[2]
                        # empty -> empty 不該處理
                        if startnode2 == emptynode and (not endnode2 in emptylist):
                            # check接下來
                            newg.edge(startnode, endnode2, label=label)
                            flag = True
                            count += 1
                            break
                        # empty->empty->empty case
                        elif startnode2 == emptynode and (endnode2 in emptylist):
                            emptynode = endnode2
                            count += 1
                            break
                    # nothing change 都好像沒有變
                    if flag or count == 0:
                        emptynode = origin_empty_node
                        break

    # for tp in alledge:
    #     startnode = tp[0]
    #     endnode = tp[1]
    #     label = tp[2]
    #     # *** -> break -> xxx
    #     if allnode[endnode][0] == 'break;':

    # 把之中沒有empty的edge連回去
    for tp in alledge:
        startnode = tp[0]
        endnode = tp[1]
        label = tp[2]
        if not (startnode in emptylist or endnode in emptylist):
            newg.edge(startnode, endnode, label=label)
    newg.render(filename='out.gv', format='png')
    # g.view()
    # newg.view()


# analysis_tool(data)
