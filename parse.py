import scanner as sc
import copy, sys

def cmp_ls(ls1, ls2):
    if len(ls1) != len(ls2):
        return False
    for i in range(len(ls1)):
        if ls1[i] not in ls2:
            return False
    return True
        
class item:
    def __init__(self, cfg):
        self.lhs = []
        self.rhs = []
        self.dot_pos = 0
        self.lookahead = []
        self.first = []
        self.no = 0
        self.cfg = cfg

    def __eq__(self, other):
        if self.lhs != other.lhs:
            return False
        if not cmp_ls(self.rhs, other.rhs):
            return False
        if self.dot_pos != other.dot_pos:
            return False
        if not cmp_ls(self.cfg.rule_dict[self.lhs][0].lookahead, self.cfg.rule_dict[other.lhs][0].lookahead):
            return False
        return True
        
        
class cfg:
    def __init__(self):
        self.rule_dict = {} # easy to query
        self.rule_num = 0
        self.rules = []

    def first(self, X, fx):
        if self.rule_dict.get(X) == None:
            if (X not in fx):
                fx.append(X)
        else:
            for item in self.rule_dict[X]:
                if item.rhs[0] != X:
                    self.first(item.rhs[0], fx)
                try:
                    nullable = item.rhs.index('VDS', 0, -1)
                except:
                    nullable = 0
                else:
                    if item.rhs[1] != X:
                        self.first(item.rhs[1], fx)

    def init_rule(self, key, rhs_ls):
        if self.rule_dict.get(key) == None:
            self.rule_dict[key] = []
        self.rule_dict[key].append(item(self))
        self.rule_dict[key][-1].lhs = key
        self.rule_dict[key][-1].rhs = rhs_ls
        self.rule_dict[key][-1].no = self.rule_num
        self.rules.append(self.rule_dict[key][-1])
        self.rule_num += 1

    def init_rules(self):
        # S -> PEOF
        self.init_rule('S',['P','EOF'])

        # P -> VDS STS (EOF)
        # program -> var_declaration statements
        self.init_rule('P',['VDS','STS'])      
        self.rule_dict['P'][-1].lookahead.append("EOF")

        # VDS -> VDS VD 
        # VDS -> VD
        self.init_rule('VDS',['VDS','VD'])     
        self.init_rule('VDS',['VD']) 

        # VD -> INT DLS SEMI
        # var_declaration -> INT declaration_list SEMI
        self.init_rule('VD',['INT','DLS','SEMI'])         

        # declaration_list -> dls COMMA decla | decla
        self.init_rule('DLS',['DLS','COMMA','D'])     
        self.init_rule('DLS',['D'])      

        # decla -> ID ASSIGN INT_NUM | ID[INT_NUM] | ID
        self.init_rule('D',['ID', 'ASSIGN', 'INT_NUM'])
        # self.init_rule('D', ['ID', 'LSQUARE', 'INT_NUM', 'RSQUARE'])
        self.init_rule('D', ['ID'])

        # code_block -> stat | {stats}          
        # self.init_rule('CB', ['ST'])
        # self.init_rule('CB', ['LBRACE', 'STS', 'RBRACE'])

        # stats -> stats stat | stat
        self.init_rule('STS', ['STS', 'ST'])
        self.init_rule('STS', ['ST'])

        # stat -> assign_stat; | ctrl_stat | rw_stat; | ;
        self.init_rule('ST', ['AST', 'SEMI'])
        self.init_rule('ST', ['CST'])
        # self.init_rule('ST', ['RWST', 'SEMI'])
        self.init_rule('ST', ['SEMI'])

        # ctrl_stat -> if_stat | while_stat | do_while_stat; | RETURN;
        # self.init_rule('CST', ['IFST'])
        # self.init_rule('CST', ['WHST'])
        # self.init_rule('CST', ['DWST', 'SEMI'])
        self.init_rule('CST', ['RETURN', 'SEMI']) 

        # rw_stat -> r_stat | w_stat
        # self.init_rule('RWST', ['RST'])
        # self.init_rule('RWST', ['WST'])

        # # assign_stat -> ID[exp] := exp | ID := exp
        # self.init_rule('AST', ['ID', 'LSQUARE', 'E', 'RSQUARE', 'ASSIGN', 'E'])
        self.init_rule('AST', ['ID', 'ASSIGN', 'E'])

        # if_stat -> if_stmt | if_stmt ELSE code_block
        # self.init_rule('IFST', ['IFSTMT']) 
        # self.init_rule('IFST', ['IFSTMT', 'ELSE', 'CB'])

        # # if_stmt -> if (exp) code_block
        # self.init_rule('IFSTMT', ['IF', 'LPAR', 'E', 'RPAR', 'CB'])

        # # while_stat -> WHILE (exp) code_block
        # self.init_rule('WHST', ['WHILE', 'LPAR', 'E', 'RPAR', 'CB'])

        # # do_while_stat -> DO code_block WHILE (exp)
        # self.init_rule('DWST', ['DO', 'CB', 'WHILE', 'LPAR', 'E', 'RPAR']) 

        # # r_stat -> READ(ID)
        # self.init_rule('RST', ['READ', 'LPAR', 'ID', 'RPAR'])

        # # w_stat -> write(exp)
        # self.init_rule('WST', ['WRITE', 'LPAR', 'E', 'RPAR'])

        # exp -> 
        self.init_rule('E', ['INT_NUM'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['ID'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        # self.init_rule('E', ['ID', 'LSQUARE', 'E', 'RSQUARE'])
        # self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
        #                                  "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
        #                                  'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['NOT_OP', 'E']) # ! has the highest priority
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', 'AND_OP', 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'ANDAND', 'OROR', 'OR_OP', 'AND_OP']

        self.init_rule('E', ['E', "OR_OP", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'ANDAND', 'OROR', 'OR_OP']

        self.init_rule('E', ['E', "PLUS", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "MINUS", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "MUL_OP", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "DIV_OP", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "LT", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP',
                                         'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "GT", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP',
                                         'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "EQ", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP', 'EQ', 
                                         'NOTEQ', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "NOTEQ", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP', 'EQ', 
                                         'NOTEQ', 'ANDAND', 'OROR']
        
        self.init_rule('E', ['E', "LTEQ", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "GTEQ", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "SHL_OP", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP',
                                         'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "SHR_OP", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP',
                                         'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "ANDAND", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'ANDAND', 'OROR']

        self.init_rule('E', ['E', "OROR", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OROR']

        self.init_rule('E', ['LPAR', 'E', 'RPAR'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('E', ["MINUS", 'E'])
        self.rule_dict['E'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.first('S', self.rule_dict['S'][0].first)
        self.first('P', self.rule_dict['P'][0].first)
        self.first('VDS', self.rule_dict['VDS'][0].first)
        self.first('VD', self.rule_dict['VD'][0].first)
        self.first('DLS', self.rule_dict['DLS'][0].first)
        self.first('D', self.rule_dict['D'][0].first)
        #self.first('CB', self.rule_dict['CB'][0].first)
        self.first('STS', self.rule_dict['STS'][0].first)
        self.first('ST', self.rule_dict['ST'][0].first)
        self.first('CST', self.rule_dict['CST'][0].first)
        #self.first('RWST', self.rule_dict['RWST'][0].first)
        self.first('AST', self.rule_dict['AST'][0].first)
        # self.first('IFST', self.rule_dict['IFST'][0].first)
        # self.first('IFSTMT', self.rule_dict['IFSTMT'][0].first)
        # self.first('WHST', self.rule_dict['WHST'][0].first)
        # self.first('DWST', self.rule_dict['DWST'][0].first)
        # self.first('RST', self.rule_dict['RST'][0].first)
        # self.first('WST', self.rule_dict['WST'][0].first)
        self.first('E', self.rule_dict['E'][0].first)

        # init lookaheads
        for i in self.rule_dict.values():
            for item in i:
                for ri in range(len(item.rhs) - 1):
                    if item.rhs[ri] != 'P' and item.rhs[ri] != 'E' and item.rhs[ri] != 'S' and self.rule_dict.get(item.rhs[ri]) != None:
                        if self.rule_dict.get(item.rhs[ri + 1]) != None:
                            for i in self.rule_dict[item.rhs[ri + 1]][0].first:
                                if i not in self.rule_dict[item.rhs[ri]][0].lookahead:
                                    self.rule_dict[item.rhs[ri]][0].lookahead.append(i)

                        elif item.rhs[ri + 1] not in self.rule_dict[item.rhs[ri]][0].lookahead:
                            self.rule_dict[item.rhs[ri]][0].lookahead.append(item.rhs[ri + 1])
        for i in self.rule_dict.values():
            for item in i:
                if item.rhs[-1] != 'E' and self.rule_dict.get(item.rhs[-1]) != None:
                    for c in self.rule_dict[item.lhs][0].lookahead:
                        if c not in self.rule_dict[item.rhs[-1]][0].lookahead:
                            self.rule_dict[item.rhs[-1]][0].lookahead.append(c)

    def print_first(self):
        for r in self.rule_dict.keys():
            print(r, self.rule_dict[r][0].lookahead)

class LR1:
    def __init__(self, cfg):
        self.table = [] #[{},{},{}] index:state
        self.states = [] #[ [item, item, item, ...], ...]
        self.cfg = cfg
        self.mapE = []

    def closure(self, crt_s):
        old_s = []
        while old_s != crt_s:
            old_s = copy.deepcopy(crt_s)
            for it in crt_s:
                if it.dot_pos < len(it.rhs) and self.cfg.rule_dict.get(it.rhs[it.dot_pos]) != None: # it: A -> a.X
                    for p in self.cfg.rule_dict[it.rhs[it.dot_pos]]:
                        # prelook = []
                        # if it.dot_pos < len(it.rhs) - 1: # it: A -> a.XB (z)
                        #     beta = it.rhs[it.dot_pos + 1]
                        #     if cfg.rule_dict.get(beta) != None: # B is non-terminal
                        #         prelook += (cfg.rule_dict[beta][0].first)
                        #     else: # B is terminal
                        #         prelook.append(beta)
                        # else: # it: A -> a.X (z)
                        #     prelook += cfg.rule_dict[it.lhs][0].lookahead

                        # for w in prelook:
                        #     crt_s.append()
                        if p not in crt_s:
                            crt_s.append(copy.deepcopy(p))
        return crt_s
    
    def goto(self, crt_s, X):
        J = []
        for it in crt_s:
            if it.dot_pos < len(it.rhs) and it.rhs[it.dot_pos] == X:
                j_it = copy.deepcopy(it)
                j_it.dot_pos += 1
                J.append(j_it)
        return self.closure(J)
        # ! "accept" case
    
    def construct_map(self):
        init_state = self.cfg.rule_dict['S']
        self.states.append(self.closure(init_state))
        self.mapE.append({})
        self.table.append({})
        old_states = []
        old_map = []

        count = 0
        while old_states != self.states or old_map != self.mapE:
            print(count)
            old_states = copy.deepcopy(self.states)
            old_map = copy.deepcopy(self.mapE)

            for si in range(len(self.states)):
                for it in self.states[si]:
                    # A -> aX.
                    # add r into table
                    if it.dot_pos == len(it.rhs):
                        if it.lhs != 'E':
                            for z in self.cfg.rule_dict[it.lhs][0].lookahead:
                                self.table[si][z] = 'r' + str(it.no)
                        else:
                            for z in it.lookahead:
                                self.table[si][z] = 'r' + str(it.no)

                    elif self.table[si].get(it.rhs[it.dot_pos]) == None: # A -> a.X
                        X = it.rhs[it.dot_pos]
                        J = self.goto(self.states[si], X)
                        state_j = -1
                        # check if this state has existed
                        for i in range(len(self.states)):
                            if cmp_ls(self.states[i], J):
                                state_j = i
                                break
                        # if a new state
                        if state_j == -1:
                            self.states.append(J)
                            self.mapE.append({})
                            self.table.append({})
                            state_j = len(self.states) - 1
                        # update map
                        self.mapE[si][X] = state_j
                        # update table
                        if self.cfg.rule_dict.get(X) == None:
                            self.table[si][X] = 's' + str(state_j)
                        else:
                            self.table[si][X] = 'g' + str(state_j)
            count+= 1
        final_s = int(self.table[0]['P'][1:])
        self.table[final_s]['EOF'] = 'a'

def parse(t, stack, crt_s):
    print('state:',crt_s, end='	')
    print('next type:', t, end='		')

    act = p.table[crt_s][t]
    if act[0] == 's':
        stack.append([crt_s,t])
        crt_s = int(act[1:])
        print('shift to state', crt_s)

    elif act[0] == 'r':
        rule = g.rules[int(act[1:])]
        for i in rule.rhs:
            last_t = stack.pop()
        print('reduce by grammar', act[1:], ':', rule.lhs,'->', ' '.join(rule.rhs))

    elif act == 'a':
        print('Accept!')
        return
    
    print('current situation:', end=' ')
    for c in stack:
        print(c[1], end=' ')
    print('|', end=' ')

    if act[0] == 'r':
        print(rule.lhs)
        print()
        print('state:', last_t[0], end='	')
        print('next type:', rule.lhs, end='		')

        stack.append([last_t[0], rule.lhs])
        crt_s = int(p.table[last_t[0]][rule.lhs][1:])
        print('shift to state', crt_s)

        print('current situation:', end=' ')
        for c in stack:
            print(c[1], end=' ')
        print('|\n')

        # Now deal with t
        crt_s = parse(t, stack, crt_s)
    else:
        print('\n')  
    return crt_s                     


if __name__ == "__main__":
    g = cfg()
    g.init_rules()
    print('Scanned Tokens:')
    tokens = sc.run(sys.argv[1])
    #tokens = sc.run('test1.c1')
    for t in tokens:
        print(t, end=' ')
    print('\n')
    tokens.append('EOF')

    p = LR1(g)
    p.construct_map()
    crt_s = 0
    stack = []
    print('Parsing Process:')
    for t in tokens:
        crt_s = parse(t, stack, crt_s)
