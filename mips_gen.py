
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

                self.b_num = 1
                self.b_stack = []

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
                self.codes.append('sw $s' + str(self.crt_saved_pt) + ',' + self.r36(c))
        def r8(self, id, i):
                # declaration -> ID LSQUARE INT_NUM RSQUARE
                addr = self.r36(id)
                addr = int(addr[:-5])
                for a in range(addr, addr + int(i) * 4, 4):
                        self.update_ptr(int(a/4), self.mem_aval)

        def r9(self, c):
                # decla -> ID
                self.r36(c)
        def r11(self):
                return
        def r12(self):
                return
        def r13(self):
                return
        def r14(self):
                return
        def r15(self):
                return
        def r16(self):
                return
        def r18(self):
                # ctrl_stat -> if_stat
                return
        def r19(self):
                return
        def r21(self):
                return
        def r22(self):
                return
        def r23(self):
                return
        
        def reg_of_exp(self, exp):
                if type(exp) == int:
                        reg = '$s' + str(self.crt_saved_pt)
                        self.codes.append('li ' + reg + ',' + str(exp))
                elif exp[-5:] == '($sp)':
                        reg = self.load_from_mem(exp)
                else:
                        reg = exp
                return reg
                        
        def r24(self, id, i, exp):
                # ass_stat: id[i] = exp
                reg = self.reg_of_exp(exp)

                self.codes.append('sw ' + reg + ',' + self.r37(id, i))
                self.release_storage(reg)

        def r25(self, c, exp):
                # ass_stat: id = exp
                self.r24(c, 0, exp)

        def r26(self):
                # if_stat: if_stmt
                self.codes.append('$L' + self.b_stack.pop() + ':')

        def r27(self):
                # else_head: if_stmt ELSE
                self.codes.append('b $L' + str(self.b_num + 1))
                self.codes.append('$L' + self.b_stack.pop() + ':')
                self.b_num += 1
                self.b_stack.append(str(self.b_num))

        def r28(self):
                # if_stat -> else_head code_block
                self.codes.append('$L' + self.b_stack.pop() + ':')

        def r29(self, exp):
                # if_head -> IF LPAR exp RPAR
                reg = self.reg_of_exp(exp)
                self.b_num += 1
                self.codes.append('beq ' + reg + ', $zero, $L' + str(self.b_num))
                self.b_stack.append(str(self.b_num))

        def r30(self):
                # if_stmt -> if_head code_block
                return
        
        def r33(self, c):
                # read_statement -> READ LPAR ID RPAR
                self.codes.append('addi $v0, $zero, 5')
                self.codes.append('syscall')
                self.codes.append('add $s' + str(self.crt_saved_pt) + ', $v0, $zero')
                self.codes.append('sw $s' + str(self.crt_saved_pt) + ',' + str(self.sym_table[c]) + '($sp)')

        def r34(self, exp):
                # print(exp)
                self.codes.append('addi $v0, $zero, 1')
                if type(exp) == int:
                        self.codes.append('addi $a0, $zero, ' + str(exp))
                elif exp[-5:] == '($sp)':
                        self.codes.append('add $a0, $zero, ' + self.load_from_mem(exp))
                else:
                        self.codes.append('add $a0, $zero, ' + exp)
                self.codes.append('syscall')

        def r35(self, c):
                # exp: INT_NUM
                # c is the one popped from stack
                return int(c)

        def r36(self, c):
                # exp: id
                try:
                        return str(self.sym_table[c]) + '($sp)'
                except:
                        addr = self.crt_mem_pt * 4
                        self.sym_table[c] = addr
                        self.update_ptr(self.crt_mem_pt, self.mem_aval)
                        return str(addr) + '($sp)'

        def r37(self, id, i):
                # exp: id[i]
                return str(self.sym_table[id] + int(i) * 4) + '($sp)'
        
        def r38(self, c):
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

                if type(c1) == int:
                        rd = "$t" + str(self.crt_temp_pt)
                        self.update_ptr(self.crt_temp_pt, self.temp_reg_aval)
                        self.codes.append("li " + rd + ',' + str(c1))   
                        c1 = rd 
                if type(c2) == int:
                        if op != 'sra' and op != 'sll':
                                self.codes.append(op + "i " + c1 + ',' + c1 + ',' + str(c2))
                        else:
                                self.codes.append(op + " " + c1 + ',' + c1 + ',' + str(c2))
                        rd = c1
                else:
                        rd = [c1, c2][c1[2:] > c2[2:]]
                        self.codes.append(op + " " + rd + ',' + c1 + ',' + c2)
                        self.release_storage([c1, c2][rd == c1])
                return rd

        def r39(self, c1, c2):
                return self.EopE(c1, c2, 'and')

        def r40(self, c1, c2):
                return self.EopE(c1, c2, 'or')

        def r41(self, c1, c2):
                return self.EopE(c1, c2, 'add')
        
        def r42(self, c1, c2):
                return self.EopE(c1, c2, 'sub')
        
        def r45(self, c1, c2):
                # <
                result = self.EopE(c1, c2, 'slt')
                self.codes.append('andi ' + result + ',' + result + ',0x00ff')
                return result
        
        def r46(self, c1, c2):
                # >
                return self.r45(c2, c1)

        def r51(self, c1, c2):
                # <<
                return self.EopE(c1, c2, 'sll')
        def r52(self, c1, c2):
                # >>
                return self.EopE(c1, c2, 'sra')
        
        def print_codes(self):
                for cc in self.codes:
                        print(cc)