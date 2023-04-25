
class generator:
        def __init__(self):
                self.codes = []
                self.sym_table = {} #[c, addr]
                self.saved_reg_aval = [1] * 8
                self.temp_reg_aval = [1] * 8
                self.bridge_reg_aval = [1] * 3
                self.mem_aval = [1] * 50
                self.mem_aval[0] = 0
                self.mem_aval[1] = 0

                # pointing to the first available saved_reg
                self.crt_saved_pt = 0
                self.crt_temp_pt = 0
                self.crt_bridge_pt = 0
                self.crt_mem_pt = 2

        def update_ptr(self, pt, ls):
                ls[pt] = 0
                for i in range(pt + 1, len(ls)):
                        if ls[i] == 1:
                                pt = i
                                if ls == self.saved_reg_aval:
                                        self.crt_saved_pt = pt
                                elif ls == self.temp_reg_aval:
                                        self.crt_temp_pt = pt
                                elif ls == self.bridge_reg_aval:
                                        self.crt_bridge_pt = pt
                                elif ls == self.mem_aval:
                                        self.crt_mem_pt = pt

                                return   
                
        def release_storage(self, reg):
                if reg[-5:] == '($sp)':
                        pos = int(reg[:-4])
                        self.mem_aval[pos] = 1
                        if pos < self.crt_mem_pt:
                                self.crt_mem_pt = pos

                else:
                        pos = int(reg[2:])
                        if reg[1] == 't':
                                self.temp_reg_aval[pos] = 1
                                if pos < self.crt_temp_pt:
                                        self.crt_temp_pt = pos
                        elif reg[1] == 's':
                                self.saved_reg_aval[pos] = 1
                                if pos < self.crt_saved_pt:
                                        self.crt_saved_pt = pos


        def load_from_mem(self, c):
                addr = "$s" + str(self.crt_saved_pt)
                self.update_ptr(self.crt_saved_pt, self.saved_reg_aval)
                self.codes.append("lw " + addr + ',' + c)
                return addr
        
        def r1(self):
                return
        def r2(self):
                # var_declas: var_declas var_decla
                return
        
        def r3(self):
                # var_declas: sigma
                return
        
        def r4(self):
                # var_decla : INT declas SEMI
                return
        
        def r6(self):
                # declas : decla
                return
        def r7(self, c, num):
                # decla: id = num
                self.codes.append('li $s' + str(self.crt_saved_pt) + ',' + str(num))
                self.codes.append('sw $s' + str(self.crt_saved_pt) + ',' + self.r34(c))

        def r9(self, c):
                self.r34(c)
        def r12(self):
                return
        def r13(self):
                return
        
        def r14(self):
                return
        def r16(self):
                return
        def r23(self):
                return
        def r25(self, c, exp):
                # ass_stat: id = exp
                if type(exp) == int:
                        reg = '$s' + str(self.crt_saved_pt)
                        self.codes.append('li ' + reg + ',' + str(exp))
                elif exp[-5:] == '($sp)':
                        reg = self.load_from_mem(exp)
                else:
                        reg = exp

                self.codes.append('sw ' + reg + ',' + str(self.sym_table[c]) + '($sp)')
                self.release_storage(reg)

        def r32(self, exp):
                # print(exp)
                self.codes.append('addi $v0, $zero, 1')
                if type(exp) == int:
                        self.codes.append('addi $a0, $zero, ' + str(exp))
                elif exp[-5:] == '($sp)':
                        self.codes.append('add $a0, $zero, ' + self.load_from_mem(exp))
                else:
                        self.codes.append('add $a0, $zero, ' + exp)
                self.codes.append('syscall')

        def r33(self, c):
                # exp: INT_NUM
                # c is the one popped from stack
                return int(c)

        def r34(self, c):
                # exp: id
                try:
                        return str(self.sym_table[c]) + '($sp)'
                except:
                        addr = self.crt_mem_pt * 4
                        self.sym_table[c] = addr
                        self.update_ptr(self.crt_mem_pt, self.mem_aval)
                        return str(addr) + '($sp)'

        def r35(self, id, i):
                # exp: id[i]
                return str(self.sym_table[id] + int(i) * 4) + '($sp)'
        
        def r36(self, c):
                # exp: !c
                if type(c) == int:
                        if c != 0:
                                return '$zero'
                        else:
                                return c
                elif type(c) == str:
                        c = self.load_from_mem(c)
                        
                        self.codes.append("sltu " + c + "," + c + ",1")
                        self.codes.append("andi " + c + "," + c + ",0x00ff")
                        return c
                
        def EopE(self, c1, c2, op):
                if type(c1) == str and c1[-5:] == '($sp)':
                        c1 = self.load_from_mem(c1)
                if type(c2) == str and c2[-5:] == '($sp)':
                        c2 = self.load_from_mem(c2)

                if type(c1) == int and type(c2) == int:
                        rd = "$t" + str(self.crt_temp_pt)
                        self.update_ptr(self.crt_temp_pt, self.temp_reg_aval)
                        self.codes.append("li " + rd + ',' + str(c1))    

                        self.codes.append(op + "i " + rd + ',' + rd + ',' + str(c2))   
                elif type(c1) == int:
                        self.codes.append(op + "i " + c2 + ',' + c2 + ',' + str(c1)) 
                        rd = c2
                elif type(c2) == int:
                        self.codes.append(op + "i " + c1 + ',' + c1 + ',' + str(c2))
                        rd = c1
                else:
                        rd = [c1, c2][c1[2:] > c2[2:]]
                        self.codes.append(op + " " + rd + ',' + c1 + ',' + c2)
                        self.release_storage([c1, c2][rd == c1])
                return rd

        def r37(self, c1, c2):
                return self.EopE(c1, c2, 'and')

        def r38(self, c1, c2):
                return self.EopE(c1, c2, 'or')

        def r39(self, c1, c2):
                return self.EopE(c1, c2, 'add')
        
        def r40(self, c1, c2):
                return self.EopE(c1, c2, 'sub')

        def print_codes(self):
                for cc in self.codes:
                        print(cc)