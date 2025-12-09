 library stl;
context stl.prelude;

library work;
use work.hamming_pkg.all;

-- Generic Hamming code decoder that takes a block `code` and decodes
-- it with corresponding parity bits into a `message` from extended 
-- Hamming code (SECDED).
--  
-- The output port `sec` is set when the incoming `code` was decoded with a
-- single-bit error correction. The output port `ded` is set when the incoming
-- `code` was decoded with a double-bit error detected.
entity hamming_dec is 
  generic (
    -- Number of data bits
    K: pint
  );
  port (
    -- Hamming block
    code: in logics(block_width(K)-1 downto 0);
    -- Message
    data: out logics(K-1 downto 0);
    -- Indicate single-bit error correction
    sec: out logic;
    -- Indicate double-bit error detection
    ded: out logic
  );
end entity;

-- General-purpose implementation in combinational logic.
architecture rtl of hamming_dec is

  constant PARITY_BITS: pint := parity_count(K);

  constant EVEN: bool := true;

  constant TOTAL_BITS_SIZE: pint := block_width(K);
  constant PARITY_LINE_SIZE: pint := TOTAL_BITS_SIZE/2;

  -- compare against the `err_address`
  constant ZEROS: logics(PARITY_BITS-1 downto 0) := (others => '0');

  type hamm_block is array (0 to PARITY_BITS-1) of logics(PARITY_LINE_SIZE-1 downto 0);

  signal dec_block: hamm_block;

  -- flag for detecting an error in the entire hamming-code block
  signal err_detected: logic;
  -- address pinpointing the erroneous bit in the hamming-code block
  signal err_address: logics(PARITY_BITS-1 downto 0);

  -- the encoding after any bit manipulation/correction
  signal code_mod: logics(2**PARITY_BITS-1 downto 0);
  signal code_ext: logics(2**PARITY_BITS-1 downto 0);

begin

  -- Divide the entire hamming-code block into parity subset groups
  p_split_hblock: process(all)
    variable temp_line: logics(PARITY_LINE_SIZE-1 downto 0);
    variable index: logics(PARITY_BITS-1 downto 0);
  begin
    for ii in PARITY_BITS-1 downto 0 loop
      temp_line := (others => '0');
      for jj in TOTAL_BITS_SIZE-1 downto 0 loop 
        -- Decode the parity bit index
        index := (others => '0');
        index := logics(to_unsigned(jj, PARITY_BITS));

        if index(ii) = '1' then 
          -- Insert new bit
          temp_line := temp_line(PARITY_LINE_SIZE-2 downto 0) & code(jj);
        end if;
      end loop;
      -- Drive the ii'th vector in the block as this parity's subset of bits
      dec_block(ii) <= temp_line;
    end loop;
  end process;

  -- Instantiate parity checkers for the subset of bits to evaluate
  g_check_bits: for ii in 0 to PARITY_BITS-1 generate
    u_par : entity work.parity
    generic map (
      W    => TOTAL_BITS_SIZE/2,
      EVEN => EVEN
    ) port map (
      data  => dec_block(ii),
      check => err_address(ii)
    );
  end generate;

  -- Computes the extra parity bit (0th bit) for double-error detection
  u_ded : entity work.parity
  generic map (
    W    => TOTAL_BITS_SIZE,
    EVEN => EVEN
  ) port map (
    data  => code(TOTAL_BITS_SIZE-1 downto 0),
    check => err_detected
  );

  code_ext(2**PARITY_BITS-1 downto TOTAL_BITS_SIZE) <= (others => '0');
  code_ext(TOTAL_BITS_SIZE-1 downto 0) <= code;

  -- Perform bit-error correction
  p_fix_data: process(all)
  begin
    -- By default, perform no manipulation on the received encoding
    code_mod(2**PARITY_BITS-1 downto TOTAL_BITS_SIZE) <= (others => '0');
    code_mod(TOTAL_BITS_SIZE-1 downto 0) <= code;
    -- Flip the bit at detected address
    if err_detected = '1' then
      code_mod(to_int(usign(err_address))) <= not code_ext(to_int(usign(err_address)));
    end if;
  end process;

  -- Remove the parity bits to reveal the information bits
  p_extract_data: process(all)
    variable ctr: uint;
  begin
    data <= (others => '0');
    ctr := 0;
    for ii in 1 to TOTAL_BITS_SIZE-1 loop
      -- Take only information bits (non-powers of 2) from encoding
      if is_pow2(ii) = false then
        data(ctr) <= code_mod(ii);
        ctr := ctr + 1;
      end if;
    end loop;
  end process;

  -- Logic for determining when a single-bit error occurred
  sec <= err_detected;

  -- Logic for determining when a double-bit error occurred
  ded <= '1' when (err_address /= ZEROS and err_detected = '0') else
    '0';

end architecture;
