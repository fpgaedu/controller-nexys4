from myhdl import *

def UartTx(clk, reset, tx, tx_data, tx_start, tx_busy, baud_tick, data_bits=8, 
        stop_bits=1):
    """
    clk
        input
        Clock signal
    reset
        input
        Reset signal
    tx
        output
        Tx line
    tx_data
        input
        data to transmit
    tx_start
        input
    tx_busy
        output
    baud_tick
        input
    """
    
    state_t = enum('READY', 'WAIT_START', 'SEND_START', 'SEND_DATA', 'SEND_STOP')

    state_reg = Signal(state_t.READY)
    state_next = Signal(state_t.READY)
    data_reg = Signal(intbv(0)[data_bits:0])
    data_next = Signal(intbv(0)[data_bits:0])
    count_reg = Signal(intbv(0, min=0, max=data_bits))
    count_next = Signal(intbv(0, min=0, max=8))

    HIGH = True
    LOW = False
    START = LOW
    STOP = HIGH
    IDLE = HIGH

    @always_seq(clk.posedge, reset=reset)
    def reg_logic():
        state_reg.next = state_next
        data_reg.next = data_next
        count_reg.next = count_next

    @always_comb
    def next_state_logic():

        state_next.next = state_reg
        data_next.next = data_reg
        count_next.next = 0

        if state_reg == state_t.READY:
            if tx_start:
                state_next.next = state_t.WAIT_START
                data_next.next = tx_data
            elif tx_start and baud_tick:
                state_next.next = state_t.SEND_START
                data_next.next = tx_data
        elif state_reg == state_t.WAIT_START:
            if baud_tick:
                state_next.next = state_t.SEND_START
        elif state_reg == state_t.SEND_START:
            if baud_tick:
                state_next.next = state_t.SEND_DATA
        elif state_reg == state_t.SEND_DATA:
            if baud_tick:
                count_next.next = (count_reg + 1) % data_bits
                if count_reg == data_bits - 1:
                    state_next.next = state_t.SEND_STOP
            else:
                count_next.next = count_reg
        elif state_reg == state_t.SEND_STOP:
            if baud_tick:
                count_next.next = (count_reg + 1) % stop_bits
                state_next.next = state_t.READY

    @always_comb
    def output_logic():
        tx.next = IDLE
        tx_busy.next = True

        if state_reg == state_t.READY:
            tx_busy.next = False
        elif state_reg == state_t.WAIT_START:
            pass
        elif state_reg == state_t.SEND_START:
            tx.next = START
        elif state_reg == state_t.SEND_DATA:
            tx.next = data_reg(count_reg)
        elif state_reg == state_t.SEND_STOP:
            tx.next = STOP

    return reg_logic, next_state_logic, output_logic



