from myhdl import always_comb


def TestExperiment(clk, reset, addr, din, dout, wen):
    '''
    input signals:
        clk
        reset
        addr
        din
        wen
    output signals:
        dout
    '''

    @always_comb
    def logic():
        dout.next = (addr +1)% (256)

    clk.read = True
    reset.read = True
    din.read = True
    wen.read = True

    return logic 
