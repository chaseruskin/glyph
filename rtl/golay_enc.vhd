library stl;
context stl.prelude;

-- Golay code encoder that takes a message `data` and produces the corresponding
-- check bits and extended parity bit to make the extended binary Golay 
-- [24, 12, 8] code.
entity golay_enc is 
  port(
    -- Message
    data: in logics(11 downto 0);
    -- Golay check bits
    check: out logics(10 downto 0);
    -- Extended parity bit
    parity: out logic
  );
end entity;


architecture gp of golay_enc is

begin


end architecture;