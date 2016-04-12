from myhdl import always_seq, always_comb, enum, Signal, intbv

def ControllerCycleControl(spec, clk, reset, start, pause, step, autonomous, 
        cycle_count, exp_clk_en):
    '''
    spec:
        Controller spec
    clk:
        Input
    reset:
        Input
    start:
        Input
    pause:
        Input
    step:
        Input
    autonomous:
        Output
    cycle_count:
        Output
    exp_clk_en:
        Output
    '''
    state_t = enum('MANUAL', 'AUTONOMOUS')

    state_reg = Signal(state_t.MANUAL)
    state_next = Signal(state_t.MANUAL)
    cycle_count_reg = Signal(intbv(0)[spec.width_value:0])
    cycle_count_next = Signal(intbv(0)[spec.width_value:0])
    exp_clk_en_reg = Signal(False)
    exp_clk_en_next = Signal(False)

    @always_seq(clk.negedge, reset)
    def register_logic():
        state_reg.next = state_next
        cycle_count_reg.next = cycle_count_next
        exp_clk_en_reg.next = exp_clk_en_next

    @always_comb
    def next_state_logic():
        state_next.next = state_reg
        cycle_count_next.next = cycle_count_reg
        exp_clk_en_next.next = False

        if state_reg == state_t.MANUAL:
            if step:
                cycle_count_next.next = cycle_count_reg + 1
                exp_clk_en_next.next = True
            elif start:
                cycle_count_next.next = cycle_count_reg + 1
                state_next.next = state_t.AUTONOMOUS
                exp_clk_en_next.next = True
        elif state_reg == state_t.AUTONOMOUS:
            if pause:
                exp_clk_en_next.next = False
                state_next.next = state_t.MANUAL
            else:
                exp_clk_en_next.next = True
                cycle_count_next.next = cycle_count_reg + 1
                
    
    @always_comb
    def output_logic():
        autonomous.next = (state_reg == state_t.AUTONOMOUS)
        cycle_count.next = cycle_count_reg
        exp_clk_en.next = exp_clk_en_reg


    return register_logic, next_state_logic, output_logic
