from myhdl import always_comb

def UartRx(clk, reset, rx, rx_data, rx_finish, rx_busy, rx_baud_tick):

    @always_comb
    def output_logic():
        rx_finish.next = False
        rx_busy.next = False
        rx_data.next = 0

        if rx:
            rx_data.next = 0

    return output_logic
