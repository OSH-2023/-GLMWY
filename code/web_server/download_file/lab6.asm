.data
led_data: .word 0x400
swt_data: .word 0x404
seg_rdv: .word 0x408
seg_data: .word 0x40C
swx_vld: .word 0x410
swx_data: .word 0x414
cnt_data: .word 0x418

.text
addi s1,zero,1
lw a0,led_data
sw s1,(a0)
loop1:
lw a2,swx_vld
lw s2,(a2)
beq s2,zero,loop1
lw a3,swx_data
lw s3,(a3)

addi s3,s3,1
sw zero,(a0)
loop2:
lw a4,seg_