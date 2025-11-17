	.file	"let.c"
	.option nopic
	.attribute arch, "rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_zicsr2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
 #APP
	variavel_16k:
 .space 16384
 #NO_APP
	.align	1
	.globl	_start
	.type	_start, @function
_start:
	addi	sp,sp,-16
	sd	s0,8(sp)
	addi	s0,sp,16
	li	a5,0
	mv	a0,a5
	ld	s0,8(sp)
	addi	sp,sp,16
	jr	ra
	.size	_start, .-_start
	.ident	"GCC: (13.2.0-11ubuntu1+12) 13.2.0"
