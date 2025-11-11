 library stl;
context stl.prelude;

library work;
use work.hamming_pkg.all;

-- Generic Hamming code decoder that takes a block `encoding` and decodes
-- it with corresponding parity bits into a `message` from extended 
-- hamming code (SECDED).
--  
-- The output port `corrected` is raised when the incoming `encoding`
-- experienced a single-error correction. The output port `valid` is lowered
-- if the incoming `encoding` detected a double-bit error. 
entity hamming_dec is 
  generic (
    -- Number of parity bits to decode (excluding 0th DED bit)
    PARITY_BITS: pint range 2 to pint'high 
  );
  port (
    encoding: in logics(block_width(PARITY_BITS)-1 downto 0);
    message: out logics(data_width(PARITY_BITS)-1 downto 0);
    -- Indicate single-bit error correction (SEC)
    sec: out logic;
    -- Indicate double-bit error detection (DED)
    ded: out logic
  ); 
end entity;

-- General-purpose implementation in combinational logic.
architecture rtl of hamming_dec is

  constant EVEN: bool := true;

  constant TOTAL_BITS_SIZE: pint := block_width(PARITY_BITS);
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
  signal encoding_mod: logics(TOTAL_BITS_SIZE-1 downto 0);

begin

  --! divide the entire hamming-code block into parity subset groups
  process(all)
    variable temp_line: logics(PARITY_LINE_SIZE-1 downto 0);
    variable index: logics(PARITY_BITS-1 downto 0);
  begin
    for ii in PARITY_BITS-1 downto 0 loop
      temp_line := (others => '0');
      for jj in TOTAL_BITS_SIZE-1 downto 0 loop 
        -- decode the parity bit index
        index := (others => '0');
        index := logics(to_unsigned(jj, PARITY_BITS));

        if index(ii) = '1' then 
          -- insert new bit
          temp_line := temp_line(PARITY_LINE_SIZE-2 downto 0) & encoding(jj);
        end if;
      end loop;
      -- drive the ii'th vector in the block as this parity's subset of bits
      dec_block(ii) <= temp_line;
    end loop;
  end process;

  --! instantiate parity checkers for the subset of bits to evaluate
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

  --! computes the extra parity bit (0th bit) for double-error detection
  u_ded : entity work.parity
  generic map (
    W    => TOTAL_BITS_SIZE,
    EVEN => EVEN
  ) port map (
    data  => encoding(TOTAL_BITS_SIZE-1 downto 0),
    check => err_detected
  );

  --! perform bit-error correction
  process(all)
  begin
    -- by default, perform no manipulation on the received encoding
    encoding_mod <= encoding;
    -- flip the bit at detected address
    if err_detected = '1' then
        encoding_mod(to_int(usign(err_address))) <= not encoding(to_int(usign(err_address)));
    end if;
  end process;

  -- Remove the parity bits to reveal the information bits
  process(all)
    variable ctr: uint;
  begin
    message <= (others => '0');
    ctr := 0;
    for ii in 1 to TOTAL_BITS_SIZE-1 loop
      -- take only information bits (non-powers of 2) from encoding
      if is_pow2(ii) = false then
        message(ctr) <= encoding_mod(ii);
        ctr := ctr + 1;
      end if;
    end loop;
  end process;

  -- logic for determining when a single-bit error occurred
  sec <= err_detected;

  -- logic for determining when a double-bit error occurred
  ded <= '1' when (err_address /= ZEROS and err_detected = '0') else
    '0';

end architecture;
