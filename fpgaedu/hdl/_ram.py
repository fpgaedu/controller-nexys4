from myhdl import Signal, intbv, always, always_comb

def Ram(clk, dout, din, addr, wen, data_width=8, depth=128):
    """  
    Ram model 
    http://docs.myhdl.org/en/stable/manual/conversion_examples.html#ram-inference
    """

    mem = [Signal(intbv(0)[data_width:]) for i in range(depth)]

    @always(clk.posedge)
    def write():
        if we:
            mem[addr].next = din

    @always_comb
    def read():
        dout.next = mem[addr]

    return write, read
