from myhdl import delay, always

def ClockGen(clk, half_period):
    
    interval = delay(half_period)

    @always(interval)
    def logic():
        clk.next = not clk

    return logic
