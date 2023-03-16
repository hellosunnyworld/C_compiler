import string
import sys

class xFA:
        def __init__(self):
                self.nfa_states = [{}, {}] # nfa_states vector
                self.eps_map = []
                self.final_nfa_states_map = {}
                self.dfa_states = [{}, {}] # dfa_states vector
                self.final_dfa_states_map = {}

        def nfa_add_state(self, crt_state, c):
                self.nfa_states[crt_state][c] = len(self.nfa_states)
                crt_state = len(self.nfa_states)
                self.nfa_states.append({})  
                return crt_state         

        def nfa_add_reserved(self, rw, token):
                state = self.nfa_states[1].get(rw[0])
                if (state == None):
                        state = self.nfa_add_state(1,rw[0]) 

                for c in rw[1:]:
                        state = self.nfa_add_state(state, c) 

                self.final_nfa_states_map[state] = token

        def nfa_add_digit(self, crt_state, f_state, eps):
                if eps:
                        state = self.nfa_add_state(crt_state, "eps")
                        self.eps_map[crt_state] = state
                else:
                        state = crt_state

                for i in range(10):
                        if i == 0 and f_state == -1:
                                f_state = self.nfa_add_state(state, "0")
                        else:
                                self.nfa_states[state][str(i)] = f_state
                return f_state

        def nfa_add_num(self):
                f_state = self.nfa_add_digit(1, -1, 1)
                f_state = self.nfa_add_digit(f_state, -1, 1)
                self.nfa_states[f_state]["eps"] = f_state - 1
                self.eps_map[f_state] = f_state - 1
                self.final_nfa_states_map[f_state - 1] = "INT_NUM"

        def nfa_add_letter(self, crt_state, f_state, eps):
                if eps:
                        state = self.nfa_add_state(crt_state, "eps")
                        self.eps_map[crt_state] = state
                else:
                        state = crt_state

                for i in string.ascii_lowercase:
                        if i == "a" and f_state == -1:
                                f_state = self.nfa_add_state(state, "a")
                        else:
                                self.nfa_states[state][i] = f_state
                for i in string.ascii_uppercase:
                        self.nfa_states[state][i] = f_state
                return f_state

        def nfa_add_id(self):
                # [letter]+
                f_state = self.nfa_add_letter(1, -1, 1)
                f_state = self.nfa_add_letter(f_state, -1, 1)
                self.nfa_states[f_state]["eps"] = f_state - 1
                self.eps_map[f_state] = f_state - 1

                # [digit | letter | _]*
                crt_state = f_state - 1
                state = self.nfa_add_digit(crt_state, -1, 1)
                crt_state = state - 1
                self.nfa_states[state]["eps"] = crt_state
                self.eps_map[state] = crt_state 

                state = self.nfa_add_letter(crt_state, -1, 0)
                self.nfa_states[state]["eps"] = crt_state
                self.eps_map[state] = crt_state   

                state = self.nfa_add_state(crt_state, "_")
                self.nfa_states[state]["eps"] = crt_state
                self.eps_map[state] = crt_state  

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



        def nfa_to_dfa(self):
                return


        def scan(self, w):
                state = 1
                i = 0
                while i < len(w):
                        state = self.dfa_states[state][w[i]]
                        i += 1
                        if state == None:
                                print("Token: ERROR")
                                return
                token = self.final_dfa_states_map[state]
                if token == None:
                        print("Token: ERROR")
                else:
                        print("Token:", token)



if __name__ == "__main__":
        dfa = xFA()
        dfa.construct_nfa()
        dfa.nfa_to_dfa()
        with open(sys.argv[1]) as f:
                lines = f.readlines()
                for line in lines:
                        ws = line.split()
                        for w in ws:
                                dfa.scan(w)
                                






                        

        

                
