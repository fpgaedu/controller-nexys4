from myhdl import always_comb

def ClockEnableBuffer(clk_in, clk_out, clk_en):

    @always_comb
    def logic():
        if clk_en:
            clk_out.next = clk_in
        else:
            clk_out.next = False

    clk_in.read = True
    clk_en.read = True
    clk_out.driven = True

    return logic

ClockEnableBuffer.vhdl_code = \
'''
-- BUFGCE: Global Clock Buffer with Clock Enable
-- 7 Series
-- Xilinx HDL Libraries Guide, version 14.7
BUFGCE_inst : BUFGCE
port map (
        O => $clk_out,   -- 1-bit output: Clock output
        CE => $clk_en, -- 1-bit input: Clock enable input for I0
        I => $clk_in    -- 1-bit input: Primary clock
        );
-- End of BUFGCE_inst instantiation
'''

ClockEnableBuffer.verilog_code = \
'''
// BUFGCE: Global Clock Buffer with Clock Enable
// 7 Series
// Xilinx HDL Libraries Guide, version 14.7
BUFGCE BUFGCE_inst (
        .O(O), // 1-bit output: Clock output
        .CE(CE), // 1-bit input: Clock enable input for I0
        .I(I) // 1-bit input: Primary clock
        );
// End of BUFGCE_inst instantiation
'''
