from myhdl import always_comb

def Rom(dout, addr, content):
    '''
    http://docs.myhdl.org/en/stable/manual/conversion_examples.html#rom-inference
    '''
    @always_comb
    def read():
        dout.next = content[int(addr)]

    return read
