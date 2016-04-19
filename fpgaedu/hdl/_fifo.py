from myhdl import now, Signal, intbv, always_seq, always_comb, always
#from math import log2, ceil
from fpgaedu.hdl import Ram

def Fifo(clk, reset, din, enqueue, dout, dequeue, empty, full, 
        data_width=8, depth=16):
    '''
    clk
        Input clock signal
    reset
        Input reset signal
    din
        Data in input signal
    enqueue
        Input signal that adds the data on din to the buffer
    dout
        Data out output signal. if empty, dout = 0. If not empty, dout is 
        always set to the value of the oldest item in the buffer
    dequeue
        Removes the oldest item from the buffer and sets dout to be the next-
        oldest value
    empty
        Output signal indicating that the fifo is empty
    full
        Output signal indicating that the fifo is full

    '''
    
    #addr_width = int(ceil(log2(depth)))

    oldest_addr_reg = Signal(intbv(0, min=0, max=depth))
    oldest_addr_next = Signal(intbv(0, min=0, max=depth))
    count_reg = Signal(intbv(0, min=0, max=depth+1))
    count_next = Signal(intbv(0, min=0, max=depth+1))

    #ram_addr = Signal(intbv(0)[addr_width:0])
    #ram = Ram(clk=clk, dout=dout, din=din, addr=ram_addr, wen=wen, 
    #        data_width=data_width, depth=depth)

    mem = [Signal(intbv(0)[data_width:]) for i in range(depth)]

    @always_seq(clk.posedge, reset)
    def register_logic():
        oldest_addr_reg.next = oldest_addr_next
        count_reg.next = count_next

    @always_comb
    def next_state_logic():
        if dequeue:
            oldest_addr_next.next = (oldest_addr_reg + 1) % depth
        else:
            oldest_addr_next.next = oldest_addr_reg


        if enqueue and not dequeue:
            if not(count_reg == depth):
                count_next.next = count_reg + 1
                mem[(oldest_addr_reg + count_reg) % depth].next = din
        elif not enqueue and dequeue:
            if count_reg == 0:
                count_next.next = count_reg
            else:
                count_next.next = count_reg - 1
        else:
            count_next.next = count_reg

    @always_comb
    def output_logic():
        empty.next = False
        full.next = False
        if count_reg == 0:
            dout.next = 0
        else:
            dout.next = mem[oldest_addr_reg]
        
        if count_reg == 0:
            empty.next = True
        elif count_reg == depth:
            full.next = True

    return register_logic, next_state_logic, output_logic
