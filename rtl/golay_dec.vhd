library stl;
context stl.prelude;

-- Golay code decoder that takes a [24, 12, 8] codeword `code`, consisting of 
-- parity bit, check bits, and information bits, and decodes it to recover the 
-- original data.
--
-- The `tec` signal is set if 1, 2, or 3 bits are corrected during decoding.
-- The `qed` signal is set if 4 errors are detected during decoding.
entity golay_dec is 
  port(
    -- Golay block
    code: in logics(23 downto 0);
    -- Decoded message
    data: out logics(11 downto 0);
    -- Indicate triple-bit error correction (1, 2, or 3 bits corrected)
    tec: out logic;
    -- Indicate quadruple-bit error detection
    qed: out logic
  );
end entity;


architecture gp of golay_dec is

begin


end architecture;