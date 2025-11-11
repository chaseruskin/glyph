library stl;
context stl.prelude;

-- Checks the incoming `data` for parity to ensure the total number of 
-- 1-bits in the `data` are even or odd.
-- 
-- An even parity (EVEN_PARITY = TRUE) seeks to obtain an even amount of 
-- '1's in the data. If the count is odd, then `check_bit` is set to '1'.
-- 
-- An odd parity (EVEN_PARITY = FALSE) seeks to obtain an odd amount of
-- '1's in the data. If the count is even, then `check_bit` is set to '1'.
entity parity is 
  generic(
    -- Data width
    W: pint;
    -- Determine to perform even or odd parity
    EVEN: bool
  );
  port(
    -- Data to perform parity on
    data: in logics(W-1 downto 0);
    -- Additional bit to make the parity valid
    check: out logic
  );
end entity;

-- General-purpose implementation using combinational logic.
architecture gp of parity is
begin  

  p_comb: process(all)
    variable check_i: logic;
  begin
    -- Read each bit in data and flip based on counting '1's
    check_i := data(0);
    for ii in 1 to W-1 loop
      check_i := check_i xor data(ii);
    end loop;

    -- Drive output port with result
    if EVEN = true then 
      check <= check_i;
    else
      check <= not check_i;
    end if;
  end process;

end architecture;
