import scanner as sc
import copy, sys, pickle
import mips_gen as mg

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
                    nullable = item.rhs.index('var_declarations', 0, -1)
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
        self.init_rule('Start',['program','EOF'])

        # P -> VDS STS (EOF)
        # program -> var_declaration statements
        self.init_rule('program',['var_declarations','statements'])      
        self.rule_dict['program'][-1].lookahead.append("EOF")

        #self.init_rule('program',['statements'])      

        # VDS -> VDS VD 
        # VDS -> VD
        self.init_rule('var_declarations',['var_declarations','var_declaration'])     
        self.init_rule('var_declarations',['sigma']) 
        #self.init_rule('var_declarations',['var_declaration']) 

        # VD -> INT DLS SEMI
        # var_declaration -> INT declaration_list SEMI
        self.init_rule('var_declaration',['INT','declaration_list','SEMI'])         

        # declaration_list -> dls COMMA decla | decla
        self.init_rule('declaration_list',['declaration_list','COMMA','declaration'])     
        self.init_rule('declaration_list',['declaration'])      

        # decla -> ID ASSIGN INT_NUM | ID[INT_NUM] | ID
        self.init_rule('declaration',['ID', 'ASSIGN', 'INT_NUM'])
        self.init_rule('declaration', ['ID', 'LSQUARE', 'INT_NUM', 'RSQUARE'])
        self.init_rule('declaration', ['ID'])

        # code_block -> stat | {stats}          
        self.init_rule('code_block', ['statement'])
        self.init_rule('code_block', ['LBRACE', 'statements', 'RBRACE'])

        # stats -> stats stat | stat
        self.init_rule('statements', ['statements', 'statement'])
        self.init_rule('statements', ['statement'])

        # stat -> assign_stat; | ctrl_stat | rw_stat; | ;
        self.init_rule('statement', ['assign_statement', 'SEMI'])
        self.init_rule('statement', ['control_statement'])
        self.init_rule('statement', ['read_write_statement', 'SEMI'])
        self.init_rule('statement', ['SEMI'])

        # ctrl_stat -> if_stat | while_stat | do_while_stat; | RETURN;
        self.init_rule('control_statement', ['if_statement'])
        self.init_rule('control_statement', ['while_statement'])
        self.init_rule('control_statement', ['do_while_statement', 'SEMI'])
        self.init_rule('control_statement', ['RETURN', 'SEMI']) 

        # rw_stat -> r_stat | w_stat
        self.init_rule('read_write_statement', ['read_statement'])
        self.init_rule('read_write_statement', ['write_statement'])

        # assign_stat -> ID[exp] := exp | ID := exp
        self.init_rule('assign_statement', ['ID', 'LSQUARE', 'exp', 'RSQUARE', 'ASSIGN', 'exp'])
        self.init_rule('assign_statement', ['ID', 'ASSIGN', 'exp'])

        # if_stat -> if_stmt | if_stmt ELSE code_block
        self.init_rule('if_statement', ['if_stmt']) 
        self.init_rule('if_statement', ['if_stmt', 'ELSE', 'code_block'])

        # if_stmt -> if (exp) code_block
        self.init_rule('if_stmt', ['IF', 'LPAR', 'exp', 'RPAR', 'code_block'])

        # while_stat -> WHILE (exp) code_block
        self.init_rule('while_statement', ['WHILE', 'LPAR', 'exp', 'RPAR', 'code_block'])

        # do_while_stat -> DO code_block WHILE (exp)
        self.init_rule('do_while_statement', ['DO', 'code_block', 'WHILE', 'LPAR', 'exp', 'RPAR']) 

        # r_stat -> READ(ID)
        self.init_rule('read_statement', ['READ', 'LPAR', 'ID', 'RPAR'])

        # w_stat -> write(exp)
        self.init_rule('write_statement', ['WRITE', 'LPAR', 'exp', 'RPAR'])

        # exp -> 
        self.init_rule('exp', ['INT_NUM'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['ID'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['ID', 'LSQUARE', 'exp', 'RSQUARE'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['NOT_OP', 'exp']) # ! has the highest priority
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', 'AND_OP', 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'ANDAND', 'OROR', 'OR_OP', 'AND_OP']

        self.init_rule('exp', ['exp', "OR_OP", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'ANDAND', 'OROR', 'OR_OP']

        self.init_rule('exp', ['exp', "PLUS", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "MINUS", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "MUL_OP", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "DIV_OP", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "LT", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP',
                                         'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "GT", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP',
                                         'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "EQ", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP', 'EQ', 
                                         'NOTEQ', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "NOTEQ", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP', 'EQ', 
                                         'NOTEQ', 'ANDAND', 'OROR']
        
        self.init_rule('exp', ['exp', "LTEQ", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "GTEQ", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "SHL_OP", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP',
                                         'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "SHR_OP", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', 'AND_OP',
                                         'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "ANDAND", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'ANDAND', 'OROR']

        self.init_rule('exp', ['exp', "OROR", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OROR']

        self.init_rule('exp', ['LPAR', 'exp', 'RPAR'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.init_rule('exp', ["MINUS", 'exp'])
        self.rule_dict['exp'][-1].lookahead = ['RSQUARE', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                                         "MINUS", 'LT', 'GT', 'EQ', 
                                         'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

        self.first('Start', self.rule_dict['Start'][0].first)
        self.first('program', self.rule_dict['program'][0].first)
        self.first('var_declarations', self.rule_dict['var_declarations'][0].first)
        self.first('var_declaration', self.rule_dict['var_declaration'][0].first)
        self.first('declaration_list', self.rule_dict['declaration_list'][0].first)
        self.first('declaration', self.rule_dict['declaration'][0].first)
        self.first('code_block', self.rule_dict['code_block'][0].first)
        self.first('statements', self.rule_dict['statements'][0].first)
        self.first('statement', self.rule_dict['statement'][0].first)
        self.first('control_statement', self.rule_dict['control_statement'][0].first)
        self.first('read_write_statement', self.rule_dict['read_write_statement'][0].first)
        self.first('assign_statement', self.rule_dict['assign_statement'][0].first)
        self.first('if_statement', self.rule_dict['if_statement'][0].first)
        self.first('if_stmt', self.rule_dict['if_stmt'][0].first)
        self.first('while_statement', self.rule_dict['while_statement'][0].first)
        self.first('do_while_statement', self.rule_dict['do_while_statement'][0].first)
        self.first('read_statement', self.rule_dict['read_statement'][0].first)
        self.first('write_statement', self.rule_dict['write_statement'][0].first)
        self.first('exp', self.rule_dict['exp'][0].first)

        # init lookaheads
        for i in self.rule_dict.values():
            for item in i:
                for ri in range(len(item.rhs) - 1):
                    if item.rhs[ri] != 'program' and item.rhs[ri] != 'exp' and item.rhs[ri] != 'Start' and self.rule_dict.get(item.rhs[ri]) != None:
                        if self.rule_dict.get(item.rhs[ri + 1]) != None:
                            for i in self.rule_dict[item.rhs[ri + 1]][0].first:
                                if i not in self.rule_dict[item.rhs[ri]][0].lookahead:
                                    self.rule_dict[item.rhs[ri]][0].lookahead.append(i)

                        elif item.rhs[ri + 1] not in self.rule_dict[item.rhs[ri]][0].lookahead:
                            self.rule_dict[item.rhs[ri]][0].lookahead.append(item.rhs[ri + 1])
        for i in self.rule_dict.values():
            for item in i:
                if item.rhs[-1] != 'exp' and self.rule_dict.get(item.rhs[-1]) != None:
                    for c in self.rule_dict[item.lhs][0].lookahead:
                        if c not in self.rule_dict[item.rhs[-1]][0].lookahead:
                            self.rule_dict[item.rhs[-1]][0].lookahead.append(c)

class LR1:
    def __init__(self, cfg):
        self.table = [] #[{},{},{}] index:state
        self.states = [] #[ [item, item, item, ...], ...]
        self.cfg = cfg
        self.mapE = []

    def closure(self, crt_s):
        old_s = []
        check = 0
        change = 1 # bool
        #while old_s != crt_s:
        while change:
            #print('c', check)
            #old_s = copy.deepcopy(crt_s)
            change = 0
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
                            change = 1
            check += 1
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
        try:
            with open("table", "rb") as fp:   # Unpickling
                self.table = pickle.load(fp)
            return
        except:
            pass

        init_state = self.cfg.rule_dict['Start']
        self.states.append(self.closure(init_state))
        self.mapE.append({})
        self.table.append({})
        old_states = []
        old_map = []

        changed_map = 1
        changed_states = 1 # two bool
        count = 0
        #while old_states != self.states or old_map != self.mapE:
        while changed_map or changed_states:
            #print(count)
            #old_states = copy.deepcopy(self.states)
            #old_map = copy.deepcopy(self.mapE)
            changed_states = 0
            changed_map = 0
            for si in range(len(self.states)):
                for it in self.states[si]:
                    # A -> aX.
                    # add r into table
                    if it.dot_pos == len(it.rhs):
                        if it.lhs != 'exp':
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
                            changed_states = 1
                            self.mapE.append({})
                            changed_map = 1
                            self.table.append({})
                            state_j = len(self.states) - 1
                        # update map
                        if self.mapE[si].get(X) == None or self.mapE[si][X] != state_j:
                            self.mapE[si][X] = state_j
                            changed_map = 1
                        # update table
                        if self.cfg.rule_dict.get(X) == None:
                            self.table[si][X] = 's' + str(state_j)
                        else:
                            self.table[si][X] = 'g' + str(state_j)
            count+= 1
        final_s = int(self.table[0]['program'][1:])
        self.table[final_s]['EOF'] = 'a'
        with open("table", "wb") as fp:   #Pickling
            pickle.dump(self.table, fp)

def parse(t, stack, reg_stack, crt_s, w):
    print('state:',crt_s, end='	')
    print('next type:', t, end='		')

    if p.table[crt_s].get(t) != None:
        act = p.table[crt_s][t]
    else:
        while (p.table[crt_s].get(t) == None):
            act = p.table[crt_s]['sigma']
            stack.append([crt_s,t])
            reg_stack.append(w)
            crt_s = int(act[1:])
        act = p.table[crt_s][t]
    if act[0] == 's':
        stack.append([crt_s,t])
        reg_stack.append(w)
        crt_s = int(act[1:])
        print('shift to state', crt_s)

    elif act[0] == 'r':
        rule = g.rules[int(act[1:])]
        arg_txt = ''
        for i in rule.rhs:
            if len(stack) > 0:
                last_t = stack.pop()
                last_w = reg_stack.pop()
                if last_t[1] not in reserved and last_w not in reserved:
                    if type(last_w) == str:
                        arg_txt = '\"' + last_w + '\",' + arg_txt
                    else:
                        arg_txt = str(last_w) +',' + arg_txt
            else:
                break
        print('reduce by grammar', act[1:], ':', rule.lhs,'->', ' '.join(rule.rhs))
        arg_txt = arg_txt[:-1]
        cmd = 'code_gen.' + act + '(' + arg_txt + ')'
        print(cmd)
        X_reg = eval(cmd)

    elif act == 'a':
        print('Accept!')
        return
    
    print('current situation:', end=' ')
    for c in stack:
        print(c[1], end=' ')
    print('|', end=' ')
    print()
    for r in reg_stack:
        print(r, end=' ')
    print('|', end=' ')

    if act[0] == 'r':
        print(rule.lhs)
        print()
        print('state:', last_t[0], end='	')
        print('next type:', rule.lhs, end='		')

        stack.append([last_t[0], rule.lhs])
        reg_stack.append(X_reg)
        crt_s = int(p.table[last_t[0]][rule.lhs][1:])
        print('shift to state', crt_s)

        print('current situation:', end=' ')
        for c in stack:
            print(c[1], end=' ')
        print('|')
        for r in reg_stack:
            print(r, end=' ')
        print('|\n')

        # Now deal with t
        crt_s = parse(t, stack, reg_stack, crt_s, w)
    #else:
        print('\n')  
    return crt_s                     


if __name__ == "__main__":
    # reserved = ['INT', 'MAIN', 'VOID', 'BREAK', 'DO', 'ELSE', 'IF', 'WHILE', 'RETURN', 'READ', 'WRITE',
    #                 'LBRACE', 'RBRACE', 'LSQUARE', 'RSQUARE', 'LPAR', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
    #                 "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 'ASSIGN', 'COMMA', 'sigma', None, 'program'
    #                 'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR', 'var_declarations', 'statements',
    #                 'var_declaration', 'declaration_list', 'declaration', 'code_block', 'statement', 'statements',
    #                 'assign_statement', 'control_statement', 'read_write_statement', 'if_statement', 'while_statement',
    #                 "do_while_statement", 'read_write_statement', 'read_statement', 'write_statement', 'exp', 'if_stmt', 'Start', 'EOF']
    reserved = ['INT', 'MAIN', 'VOID', 'BREAK', 'DO', 'ELSE', 'IF', 'WHILE', 'RETURN', 'READ', 'WRITE',
                    'LBRACE', 'RBRACE', 'LSQUARE', 'RSQUARE', 'LPAR', 'RPAR', 'SEMI', 'OR_OP', "PLUS", 'AND_OP',
                    "MINUS", "MUL_OP", "DIV_OP", 'LT', 'GT', 'EQ', 'ASSIGN', 'COMMA', 'sigma', None,
                    'NOTEQ', "LTEQ", "GTEQ", 'SHL_OP', 'SHR_OP', 'ANDAND', 'OROR']

    g = cfg()
    g.init_rules()
    print('Scanned Tokens:')
    #tokens, words = sc.run(sys.argv[1])
    tokens, words = sc.run('test0.c1')
    for t in tokens:
        print(t, end=' ')
    print('\n')
    for w in words:
        print(w, end=' ')
    print('\n')
    tokens.append('EOF')
    words.append('EOF')


    p = LR1(g)
    p.construct_map()
    crt_s = 0
    stack = []
    reg_stack = []
    code_gen = mg.generator()

    print('Parsing Process:')
    for i in range(len(tokens)):
        crt_s = parse(tokens[i], stack, reg_stack, crt_s, words[i])
    code_gen.print_codes()
