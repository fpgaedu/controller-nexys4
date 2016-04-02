from myhdl import always_seq, always_comb, Signal, intbv
from math import ceil

from fpgaedu.hdl import Rom

def BaudGen(clk, reset, rx_tick, tx_tick, clk_freq=100000000, baudrate=9600, rx_div=16):
    """
    rss232 standard baud rates
    300
    1200
    2400
    4800
    9600
    14400
    19200
    28800
    38400
    57600
    115200
    230400
    """
   
    tx_tick_max = int(round(clk_freq/baudrate))

    tick_count_reg = Signal(intbv(0, min=0, max=tx_tick_max))
    tick_count_next = Signal(intbv(0, min=0, max=tx_tick_max))
    rx_div_count_reg = Signal(intbv(0, min=0, max=rx_div))
    rx_div_count_next = Signal(intbv(0, min=0, max=rx_div))


    def calculate_rx_lookup_table():
        '''
        A lookup table is used to allow for synchronization between
        rx_tick and tx_tick
        '''
        rx_tick_div = float(tx_tick_max)/float(rx_div)
        rx_tick_tbl = [0 for i in range(rx_div)]
        for i in range(rx_div):
            rx_tick_tbl[i] = int(round(float(i+1)*rx_tick_div)) - 1
        return tuple(rx_tick_tbl)

    rx_tick_lookup_rom_dout = Signal(intbv(0, min=0, max=tx_tick_max))
    rx_tick_lookup = calculate_rx_lookup_table()
    # myhdl requires the rom to be a separate instance in order to support 
    # export to vhdl
    rx_tick_lookup_rom = Rom(dout=rx_tick_lookup_rom_dout, 
            addr=rx_div_count_reg, content=rx_tick_lookup)

    # Register logic
    @always_seq(clk.posedge, reset)
    def reg_logic():
        tick_count_reg.next = tick_count_next
        rx_div_count_reg.next = rx_div_count_next

    # Next state logic
    @always_comb
    def next_state_logic():
        tick_count_next.next = (tick_count_reg + 1) % tx_tick_max
        
        if tick_count_reg == rx_tick_lookup_rom_dout:
            rx_div_count_next.next = (rx_div_count_reg + 1) % rx_div
        else:
            rx_div_count_next.next = rx_div_count_reg

    # Output logic
    @always_comb
    def output_logic():
        if tick_count_reg == rx_tick_lookup_rom_dout:
            rx_tick.next = True
        else:
            rx_tick.next = False

        if tick_count_reg == (tx_tick_max - 1):
            tx_tick.next = True
        else:
            tx_tick.next = False

    return reg_logic, next_state_logic, output_logic, rx_tick_lookup_rom 

