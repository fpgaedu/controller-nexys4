from myhdl import (always_comb, always_seq, Signal, enum, intbv, now)

def UartRx(clk, reset, rx, rx_data, rx_finish, rx_busy, rx_baud_tick, 
        data_bits=8, stop_bits=1, rx_div=16):
    '''
    clk
        input
        Clock Signal
    reset
        Input
        Reset Signal
    rx
        Input
        Uart Rx
    rx_data
        Output
        Reveived data
    rx_finish
        Output
        Pulse signal indicating that rx_data is ready
    rx_busy
        Output
        Indicating that the uart is receiving data
    rx_baud_tick
        Input
        Buadgen input
    rx_div
        Parameter
        Specifying the number of subsamples per tx_tick
    '''

    state_t = enum('WAIT_START', 'RECV_START', 'RECV_DATA', 'RECV_STOP')

    state_reg = Signal(state_t.WAIT_START)
    state_next = Signal(state_t.WAIT_START)
    baud_count_reg = Signal(intbv(0, min=0, max=rx_div))
    baud_count_next = Signal(intbv(0, min=0, max=rx_div))
    data_reg = Signal(intbv(0)[data_bits:0])
    data_next = Signal(intbv(0)[data_bits:0])
    data_count_reg = Signal(intbv(0, min=0, max=data_bits))
    data_count_next = Signal(intbv(0, min=0, max=data_bits))

    HIGH = True
    LOW = False
    START = LOW
    STOP = HIGH
    IDLE = HIGH

    @always_seq(clk.posedge, reset)
    def register_logic():
        state_reg.next = state_next
        baud_count_reg.next = baud_count_next
        data_count_reg.next = data_count_next
        data_reg.next = data_next
        
    @always_comb
    def next_state_logic():
        '''
        Determine next state levels for registers state_reg, baud_count_reg,
        data_count_reg and data_reg based on current state and input signals
        '''
        state_next.next = state_reg
        baud_count_next.next = baud_count_reg
        data_next.next = data_reg
        data_count_next.next = data_count_reg

        if state_reg == state_t.WAIT_START:
            data_next.next = 0

            if rx == START and rx_baud_tick == True:
                state_next.next = state_t.RECV_START

        elif state_reg == state_t.RECV_START:
            if rx_baud_tick == True:
                baud_count_next.next = (baud_count_reg + 1) \
                        % int(rx_div/2)

                if baud_count_reg == int(rx_div/2) - 1:
                    state_next.next = state_t.RECV_DATA

        elif state_reg == state_t.RECV_DATA:
            if rx_baud_tick == 1:
                baud_count_next.next = (baud_count_reg + 1) % rx_div

                if baud_count_reg == rx_div - 1:
                    data_count_next.next = (data_count_reg + 1) % data_bits
                    data_next.next[data_count_reg] = rx
                    
                    if data_count_reg == data_bits - 1:
                        state_next.next = state_t.RECV_STOP

        elif state_reg == state_t.RECV_STOP:
            if rx_baud_tick == 1:
                baud_count_next.next = (baud_count_reg + 1) % rx_div

                if baud_count_reg == rx_div - 1:
                    state_next.next = state_t.WAIT_START

    @always_comb
    def output_logic():
        """
        Determine levels for output signals rx_data, rx_finish, rx_busy based
        on input signals and current register states 
        """

        rx_finish.next = False
        rx_data.next = 0

        if state_reg == state_t.WAIT_START:
            rx_busy.next = False
        else:
            rx_busy.next = True

        if state_reg == state_t.RECV_STOP and baud_count_reg == rx_div-1 \
                and rx == STOP:
            rx_finish.next = True
            rx_data.next = data_reg

    return register_logic, next_state_logic, output_logic

