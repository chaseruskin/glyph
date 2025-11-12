library stl;
context stl.prelude;

library work;
use work.hamming_pkg.all;

-- Generic Hamming code encoder that takes a message `data` and packages
-- it with corresponding parity bits into an `encoding` for extended 
-- Hamming code (SECDED).
--
-- Implemented in purely combinational logic. Parity bits are set in the
-- indices corresponding to powers of 2 (0, 1, 2, 4, 8, ...).
entity hamming_enc is 
  generic(
    -- Number of data bits
    K: pint
  );
  port(
    -- Message
    data: in logics(K-1 downto 0);
    -- Hamming block
    code: out logics(block_width(K)-1 downto 0)
  );
end entity;

-- General-purpose implementation in combinational logic.
architecture gp of hamming_enc is

  constant PARITY_BITS: pint := parity_count(K);

  constant EVEN: bool := true;

  constant TOTAL_BITS_SIZE: pint := block_width(K);
  constant PARITY_LINE_SIZE: pint := TOTAL_BITS_SIZE/2;

  type hamm_block is array (0 to PARITY_BITS-1) of logics(PARITY_LINE_SIZE-1 downto 0);

  signal enc_block: hamm_block;

  -- +1 parity for the zero-th check bit
  signal check_bits: logics(PARITY_BITS-1+1 downto 0);

  signal empty_block: logics(TOTAL_BITS_SIZE-1 downto 0);
  signal full_block: logics(TOTAL_BITS_SIZE-1 downto 0);

begin

  -- Formats the incoming message into a clean Hamming block with parity
  -- bits cleared.
  p_fmt_hblock: process(all)
    variable ctr: uint;
  begin
    empty_block <= (others => '0');
    ctr := 0;
    for ii in 1 to TOTAL_BITS_SIZE-1 loop
      -- Use information bit otherwise reserve for parity bit
      if is_pow2(ii) = false then
        empty_block(ii) <= data(ctr);
        ctr := ctr + 1;
      end if;
    end loop;
  end process;

  -- Divide the entire Hamming block into parity subset groups
  p_split_hblock: process(all)
    variable temp_line: logics(PARITY_LINE_SIZE-1 downto 0);
    variable index: logics(PARITY_BITS-1 downto 0);
  begin
    for ii in PARITY_BITS-1 downto 0 loop
      temp_line := (others => '0');
      for jj in TOTAL_BITS_SIZE-1 downto 0 loop 
        -- Decode the parity bit index
        index := (others => '0');
        index := logics(to_usign(jj, PARITY_BITS));

        if index(ii) = '1' then 
          -- Insert new bit
          temp_line := temp_line(PARITY_LINE_SIZE-2 downto 0) & empty_block(jj);
        end if;
      end loop;
      -- drive the ii'th vector in the block as this parity's subset of bits
      enc_block(ii) <= temp_line;
    end loop;
  end process;

  -- Instantiate parity checkers for the subset of bits to evaluate
  g_check_bits: for ii in 0 to PARITY_BITS-1 generate
    u_par : entity work.parity
    generic map (
      W    => TOTAL_BITS_SIZE/2,
      EVEN => EVEN
    ) port map (
      data  => enc_block(ii),
      check => check_bits(ii)
    );
  end generate;

  -- Fill the hamming-code block with computed parity bits
  p_fill_hblock: process(all)
    variable ctr: uint;
  begin
    full_block <= empty_block;
    ctr := 0;

    for ii in 1 to TOTAL_BITS_SIZE-1 loop
      -- Use information bit otherwise reserve for parity bit
      if is_pow2(ii) = true then
        full_block(ii) <= check_bits(ctr);
        ctr := ctr + 1;
      end if;
    end loop;
  end process;

  -- Computes the extra parity bit (0th bit) for double-error detection
  u_ded : entity work.parity
  generic map (
    W    => TOTAL_BITS_SIZE-1,
    EVEN => EVEN
  ) port map (
    data  => full_block(TOTAL_BITS_SIZE-1 downto 1),
    check => check_bits(PARITY_BITS)
  );

  -- Drive the output with the hamming-code block and the 0th parity bit 
  code <= full_block(TOTAL_BITS_SIZE-1 downto 1) & check_bits(PARITY_BITS);

end architecture;
