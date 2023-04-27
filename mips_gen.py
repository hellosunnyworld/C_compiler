
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
                self.last_exp = 0

                self.while_htag1 = []
                self.while_htag2 = []

        def update_ptr(self, pt, ls):
                ls[pt] = 0
                for i in range(pt + 1, len(ls)):
                        if ls[i] == 1:
                                if ls == self.saved_reg_aval:
                                        self.crt_saved_pt = i
                                elif ls == self.temp_reg_aval:
                                        self.crt_temp_pt = i
                                elif ls == self.bridge_reg_aval:
                                        self.crt_bridge_pt = i
                                elif ls == self.mem_aval:
                                        self.crt_mem_pt = i

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
        def r5(self):
                # declas : decla COMMA decla
                return        
        def r6(self):
                # declas : decla
                return
        def r7(self, c, num):
                # decla: id = num
                self.codes.append('li $s' + str(self.crt_saved_pt) + ',' + str(num))
                self.codes.append('sw $s' + str(self.crt_saved_pt) + ',' + self.r38(c))
        def r8(self, id, i):
                # declaration -> ID LSQUARE INT_NUM RSQUARE
                addr = self.r38(id)
                addr = int(addr[:-5])
                for a in range(addr, addr + int(i) * 4, 4):
                        self.update_ptr(int(a/4), self.mem_aval)

        def r9(self, c):
                # decla -> ID
                self.r38(c)
        def r10(self, c):
                # code_block -> stat
                return
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
        def r17(self):
                # stat -> SEMI
                return
        def r18(self):
                # ctrl_stat -> if_stat
                return
        def r19(self):
                # ctrl_stat -> while_stat
                return
        def r20(self):
                # ctrl_stat -> do_while_stat
                return
        def r21(self):
                # ctrl_stat: return;
                self.codes.append('b end')
                return
        def r22(self):
                return
        def r23(self):
                return
        
        def reg_of_exp(self, exp):
                if type(exp) == int:
                        reg = '$t' + str(self.crt_temp_pt)
                        self.codes.append('li ' + reg + ',' + str(exp))
                        self.update_ptr(self.crt_temp_pt, self.temp_reg_aval)

                elif exp[-5:] == '($sp)':
                        reg = self.load_from_mem(exp)
                else:
                        reg = exp
                return reg
                        
        def r24(self, id, i, exp):
                # ass_stat: id[i] = exp
                reg = self.reg_of_exp(exp)

                self.codes.append('sw ' + reg + ',' + self.r39(id, i))
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
                self.release_storage(reg)

        def r30(self):
                # if_stmt -> if_head code_block
                return
        
        def r31(self, exp):
                # while_head: 'WHILE', 'LPAR', 'exp', 'RPAR
                self.while_htag2.append(len(self.codes))

                self.b_num += 2
                
                self.b_stack.append(str(self.b_num))
                self.b_stack.append(str(self.b_num - 1))
                return exp

        def r32(self, exp):
                # while_statement: while_head, code_block
                b1 = self.b_stack.pop()
                b2 = self.b_stack.pop()
                self.codes.insert(self.while_htag1.pop(), '$L' + b2 + ':')
                reg = self.reg_of_exp(exp)
                self.codes.insert(self.while_htag2.pop() + 1, 'beq ' + reg + ', $zero, $L' + b1)


                self.codes.append('b $L' + b2)
                self.codes.append('$L' + b1 + ':')
                self.release_storage(reg)

        def r33(self):
                # do_head: DO
                self.b_num += 1
                self.codes.append('$L' + str(self.b_num) + ':')
                self.b_stack.append(str(self.b_num))

        def r34(self, exp):
                # do_while_statement: do_head', 'code_block', while_head
                self.b_stack.pop()
                self.b_stack.pop()
                self.while_htag1.pop()
                self.while_htag2.pop()

                reg = self.reg_of_exp(exp)
                self.codes.append('bne ' + reg + ', $zero, $L' + self.b_stack.pop())
                self.release_storage(reg)
        
        def r35(self, c):
                # read_statement -> READ LPAR ID RPAR
                self.codes.append('addi $v0, $zero, 5')
                self.codes.append('syscall')
                self.codes.append('add $s' + str(self.crt_saved_pt) + ', $v0, $zero')
                self.codes.append('sw $s' + str(self.crt_saved_pt) + ',' + str(self.sym_table[c]) + '($sp)')

        def r36(self, exp):
                # print(exp)
                self.codes.append('addi $v0, $zero, 1')
                if type(exp) == int:
                        self.codes.append('addi $a0, $zero, ' + str(exp))
                elif exp[-5:] == '($sp)':
                        self.codes.append('add $a0, $zero, ' + self.load_from_mem(exp))
                else:
                        self.codes.append('add $a0, $zero, ' + exp)
                self.codes.append('syscall')

        def r37(self, c):
                # exp: INT_NUM
                # c is the one popped from stack
                self.last_exp = len(self.codes)
                return int(c)

        def r38(self, c):
                # exp: id
                self.last_exp = len(self.codes)
                try:
                        return str(self.sym_table[c]) + '($sp)'
                except:
                        addr = self.crt_mem_pt * 4
                        self.sym_table[c] = addr
                        self.update_ptr(self.crt_mem_pt, self.mem_aval)
                        return str(addr) + '($sp)'

        def r39(self, id, i):
                # exp: id[exp]
                self.last_exp = len(self.codes)
                if type(i) == int:
                        return str(self.sym_table[id] + i * 4) + '($sp)'
                else:
                        i_reg = self.reg_of_exp(i)
                        self.codes.append('sll ' + i_reg + ', ' + i_reg + ', 2')
                        self.codes.append('addiu $t' + str(self.crt_temp_pt) + ', $sp, ' + str(self.sym_table[id] - 32)) 
                        self.codes.append('addu ' + i_reg + ', $t' + str(self.crt_temp_pt) + ', ' + i_reg)
                        self.codes.append('lw ' + i_reg + ', 32(' + i_reg + ')')
                        return i_reg


        
        def r40(self, c):
                # exp: !c
                self.last_exp = len(self.codes)
                if type(c) == int:
                        if c != 0:
                                return '$zero'
                        else:
                                return c
                elif type(c) == str:
                        c = self.load_from_mem(c)
                        
                        self.codes.append("sltiu " + c + "," + c + ",1")
                        self.codes.append("andi " + c + "," + c + ",0x00ff")
                        return c
                
        def EopE(self, c1, c2, op):
                self.last_exp = len(self.codes)

                c1 = self.reg_of_exp(c1)

                if op == 'mult' or op == 'div':
                        c2 = self.reg_of_exp(c2)
                        self.codes.append(op + ' ' + c1 + ', ' + c2)
                        rd = [c1, c2][c1[2:] > c2[2:]]
                        self.codes.append('mflo ' + rd)
                        self.release_storage([c1, c2][rd == c1])

                elif type(c2) == int:
                        if op != 'srav' and op != 'sllv':
                                self.codes.append(op + "i " + c1 + ',' + c1 + ',' + str(c2))
                        else:
                                self.codes.append(op[:-1] + " " + c1 + ',' + c1 + ',' + str(c2))
                        rd = c1
                else:
                        c2 = self.reg_of_exp(c2)
                        rd = [c1, c2][c1[2:] > c2[2:]]
                        self.codes.append(op + " " + rd + ',' + c1 + ',' + c2)
                        self.release_storage([c1, c2][rd == c1])
                return rd

        def r41(self, c1, c2):
                return self.EopE(c1, c2, 'and')

        def r42(self, c1, c2):
                return self.EopE(c1, c2, 'or')

        def r43(self, c1, c2):
                return self.EopE(c1, c2, 'add')
        
        def r44(self, c1, c2):
                return self.EopE(c1, c2, 'sub')
        def r45(self, c1, c2):
                return self.EopE(c1, c2, 'mult')
        def r46(self, c1, c2):
                return self.EopE(c1, c2, 'div')
                
        def r47(self, c1, c2):
                # <
                result = self.EopE(c1, c2, 'slt')
                self.codes.append('andi ' + result + ',' + result + ',0x00ff')
                return result
        
        def r48(self, c1, c2):
                # >
                return self.r47(c2, c1)
        
        def r49(self, c1, c2):
                # ==
                result = self.EopE(c1, c2, 'xor')
                self.codes.append('sltiu ' + result + ', ' + result + ', 1')
                self.codes.append('andi ' + result + ', ' + result + ', 0x00ff')
                return result
        def r50(self, c1, c2):
                # !=
                result = self.EopE(c1, c2, 'xor')
                self.codes.append('sltu ' + result + ', $zero, ' + result)
                self.codes.append('andi ' + result + ', ' + result + ', 0x00ff')
                return result                
        def r51(self, c1, c2):
                # <=
                result = self.EopE(c2, c1, 'slt')
                self.codes.append('xori ' + result + ', ' + result + ', 0x1')
                self.codes.append('andi ' + result + ', ' + result + ', 0x00ff')
                return result
        def r52(self, c1, c2):
                # >=
                result = self.EopE(c1, c2, 'slt')
                self.codes.append('xori ' + result + ', ' + result + ', 0x1')
                self.codes.append('andi ' + result + ', ' + result + ', 0x00ff')
                return result
        def r53(self, c1, c2):
                # <<
                return self.EopE(c1, c2, 'sllv')
        def r54(self, c1, c2):
                # >>
                return self.EopE(c1, c2, 'srav')
        
        def and_or(self, c1, c2, op):
                r1 = self.reg_of_exp(c1)
                self.b_num += 1
                if op == 'and':
                        self.codes.append('beq ' + r1 + ', $zero, $L' + str(self.b_num))
                else:
                        self.codes.append('bne ' + r1 + ', $zero, $L' + str(self.b_num))
                self.release_storage(r1)

                r2 = self.reg_of_exp(c2)
                if op == 'and':
                        self.codes.append('beq ' + r2 + ', $zero, $L' + str(self.b_num))    
                else:
                        self.codes.append('beq ' + r2 + ', $zero, $L' + str(self.b_num + 1))
                        self.codes.append('$L' + str(self.b_num) + ':')
                        self.b_num += 1
                self.codes.append('li ' + r2 + ', 1')
                self.codes.append('b $L' + str(self.b_num + 1))
                self.codes.append('$L' + str(self.b_num) + ':')
                self.b_num += 1
                self.codes.append('move ' + r2 + ',$zero')
                self.codes.append('$L' + str(self.b_num) + ':')
                return r2
        
        def r55(self, c1, c2):
                # &&
                return self.and_or(c1, c2, 'and')

        def r56(self, c1, c2):
                # ||
                return self.and_or(c1, c2, 'or')
        
        def r57(self, exp):
                # exp: (exp)
                return exp
        
        def r58(self, c):
                # exp: -exp
                c = self.reg_of_exp(c)
                self.codes.append('sub ' + c + ', $zero, ' + c)
                return c

        def print_codes(self):
                for cc in self.codes:
                        print(cc)