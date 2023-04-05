import string
import sys

class xFA:
        def __init__(self):
                self.nfa_states = [{}, {}] # nfa_states vector
                self.eps_map = [[], []]
                self.final_nfa_states_map = {}
                self.dfa_states = [{}, {}] # dfa_states vector
                self.final_dfa_states_map = {}
                self.dfa_to_nfa = [[]]

        def nfa_add_state(self, crt_state, c):
                if self.nfa_states[crt_state].get(c) == None:
                        self.nfa_states[crt_state][c] = [len(self.nfa_states)]
                else:
                        self.nfa_states[crt_state][c].append(len(self.nfa_states))
                crt_state = len(self.nfa_states)
                self.nfa_states.append({})  
                self.eps_map.append([])
                return crt_state         

        def nfa_add_reserved(self, rw, token):
                state = self.nfa_states[1].get(rw[0])
                if (state == None):
                        state = self.nfa_add_state(1,rw[0]) 
                else:
                        state = state[0]
                for c in rw[1:]:
                        state = self.nfa_add_state(state, c) 

                self.final_nfa_states_map[state] = token

        def nfa_add_digit(self, crt_state, f_state, eps):
                if eps:
                        state = self.nfa_add_state(crt_state, "eps")
                        self.eps_map[crt_state].append(state)
                else:
                        state = crt_state

                for i in range(10):
                        if i == 0 and f_state == -1:
                                f_state = self.nfa_add_state(state, "0")
                        elif self.nfa_states[state].get(str(i)) == None:
                                self.nfa_states[state][str(i)] = [f_state]
                        else:
                                self.nfa_states[state][str(i)].append(f_state)
                return f_state

        def nfa_add_num(self):
                f_state = self.nfa_add_digit(1, -1, 1)
                f_state = self.nfa_add_digit(f_state, -1, 1)
                self.eps_map[f_state].append(f_state - 1)
                self.final_nfa_states_map[f_state - 1] = "INT_NUM"

        def nfa_add_letter(self, crt_state, f_state, eps):
                if eps:
                        state = self.nfa_add_state(crt_state, "eps")
                        self.eps_map[crt_state].append(state)
                else:
                        state = crt_state

                for i in string.ascii_lowercase:
                        if i == "a" and f_state == -1:
                                f_state = self.nfa_add_state(state, "a")
                        elif self.nfa_states[state].get(i) == None:
                                self.nfa_states[state][i] = [f_state]
                        else:
                                self.nfa_states[state][i].append(f_state)
                for i in string.ascii_uppercase:
                        if self.nfa_states[state].get(i) == None:
                                self.nfa_states[state][i] = [f_state]
                        else:
                                self.nfa_states[state][i].append(f_state)
                return f_state

        def nfa_add_id(self):
                # [letter]+
                f_state = self.nfa_add_letter(1, -1, 1)
                f_state = self.nfa_add_letter(f_state, -1, 1)
                self.eps_map[f_state].append(f_state - 1)

                # [digit | letter | _]*
                crt_state = f_state - 1
                state = self.nfa_add_digit(crt_state, -1, 1)
                crt_state = state - 1
                self.eps_map[state].append(crt_state) 

                state = self.nfa_add_letter(crt_state, -1, 0)
                self.eps_map[state].append(crt_state)   

                state = self.nfa_add_state(crt_state, "_")
                self.eps_map[state].append(crt_state)  

                self.final_nfa_states_map[crt_state] = "ID"    

        def construct_nfa(self):
                self.nfa_add_reserved("int", "INT")
                self.nfa_add_reserved("main", "MAIN")
                self.nfa_add_reserved("void", "VOID")
                self.nfa_add_reserved("break", "BREAK")
                self.nfa_add_reserved("do", "DO")
                self.nfa_add_reserved("else", "ELSE")
                self.nfa_add_reserved("if", "IF")
                self.nfa_add_reserved("while", "WHILE")
                self.nfa_add_reserved("return", "RETURN")
                self.nfa_add_reserved("scanf", "READ")
                self.nfa_add_reserved("printf", "WRITE")

                self.nfa_add_reserved("{", "LBRACE")
                self.nfa_add_reserved("}", "RBRACE")
                self.nfa_add_reserved("[", "LSQUARE")
                self.nfa_add_reserved("]", "RSQUARE")
                self.nfa_add_reserved("(", "LPAR")
                self.nfa_add_reserved(")", "RPAR")
                self.nfa_add_reserved(";", "SEMI")
                self.nfa_add_reserved("+", "PLUS")
                self.nfa_add_reserved("-", "MINUS")
                self.nfa_add_reserved("*", "MUL_OP")
                self.nfa_add_reserved("/", "DIV_OP")
                self.nfa_add_reserved("&", "AND_OP")
                self.nfa_add_reserved("|", "OR_OP")
                self.nfa_add_reserved("!", "NOT_OP")
                self.nfa_add_reserved("=", "ASSIGN")
                self.nfa_add_reserved("<", "LT")
                self.nfa_add_reserved(">", "GT")
                self.nfa_add_reserved("<<", "SHL_OP")
                self.nfa_add_reserved(">>", "SHR_OP")
                self.nfa_add_reserved("==", "EQ")
                self.nfa_add_reserved("!=", "NOTEQ")
                self.nfa_add_reserved("<=", "LTEQ")
                self.nfa_add_reserved(">=", "GTEQ")
                self.nfa_add_reserved("&&", "ANDAND")
                self.nfa_add_reserved("||", "OROR")
                self.nfa_add_reserved(",", "COMMA")

                self.nfa_add_num()
                self.nfa_add_id()

        def closure(self, s, clo_s):
                if s not in clo_s:
                        clo_s.append(s)
                for i in self.eps_map[s]:
                        self.closure(i, clo_s)
                        
        def DFAedge(self, s, c):
                r = []
                for ns in self.dfa_to_nfa[s]:
                        try:
                                for i in self.nfa_states[ns][c]:
                                        self.closure(i, r)
                        except:
                                continue
                return r

        def nfa_to_dfa(self):
                self.dfa_to_nfa.append([])
                self.closure(1, self.dfa_to_nfa[1])
                p = 1
                j = 1
                while j <= p:
                        for m in self.dfa_to_nfa[j]:
                                for c in self.nfa_states[m].keys():
                                        e = self.DFAedge(j, c)
                                        for i in range(len(self.dfa_to_nfa)):
                                                if e == self.dfa_to_nfa[i]:
                                                        self.dfa_states[j][c] = i
                                                        break
                                        if self.dfa_states[j].get(c) == None:
                                                p += 1
                                                self.dfa_to_nfa.append(e)
                                                self.dfa_states[j][c] = p
                        j += 1
                        self.dfa_states.append({})
                        #print(j,p)

                for ds_i in range(1,len(self.dfa_to_nfa)):
                        for ns in self.dfa_to_nfa[ds_i]:
                                token_ns = self.final_nfa_states_map.get(ns)
                                if token_ns != None:
                                        self.final_dfa_states_map[ds_i] = token_ns
                                        break


        def scan(self, w):
                state = 1
                i = 0
                while i < len(w):
                        state = self.dfa_states[state].get(w[i])
                        i += 1
                        if state == None:
                                #print("Token: ERROR")
                                return False
                token = self.final_dfa_states_map.get(state)
                if token == None:
                        return False
                else:
                        return token


def proc_seg(dfa, w, tokens):
        w_len = 1
        token = dfa.scan(w)
        #print("----------------")
        #print("process", w)
        while token == False and w_len < len(w):
                #print("process", w[0:-w_len])
                token = dfa.scan(w[0:-w_len])
                w_len += 1
        if token == False:
                print("Token: ERROR")
                return
        else:
                #print("Token:", token)   
                tokens.append(token)
        
        if w_len == 1:
                return
        proc_seg(dfa, w[(len(w) - w_len + 1):], tokens)

def run(f):
        tokens = []
        dfa = xFA()
        dfa.construct_nfa()
        dfa.nfa_to_dfa()
        with open(f) as f:
        #with open("/home/sunnylin/csc4180_compiler/A2/TestCases/test1.c1") as f:
                lines = f.readlines()
                for line in lines:
                        ws = line.split()
                        for w in ws:
                                proc_seg(dfa, w, tokens)
        return tokens
                                
                                


                                






                        

        

                
