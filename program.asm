DATA:
v_a      10
v_b      0
v_c      0
v_d      0
v_e      0
v_f      0
v_g      0
v_t1     0
v_t2     0
v_t3     0
v_t4     0
v_t5     0
v_result 0
v_error  0

CODE:
    MOV A,(v_b)
    MOV (v_t3),A
    CMP A,0
    JEQ L2
    JMP L1
L2:
    MOV A,1
    MOV (v_error),A
    MOV A,0
    MOV (v_result),A
    JMP end_program
L1:
    MOV A,(v_a)
    MOV (v_t4),A
    MOV A,0
    MOV (v_t5),A
L3:
    MOV A,(v_t4)
    CMP A,(v_t3)
    JGE L4
    JMP L5
L4:
    MOV A,(v_t4)
    SUB A,(v_t3)
    MOV (v_t4),A
    MOV A,(v_t5)
    ADD A,1
    MOV (v_t5),A
    JMP L3
L5:
    MOV A,(v_t5)
    MOV (v_t2),A
    MOV A,(v_t2)
    MOV (v_result),A
end_program:

; Líneas totales: 51
; Accesos a memoria (aprox): 17
