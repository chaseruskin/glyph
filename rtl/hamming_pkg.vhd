library stl;
context stl.prelude;

-- Hamming code package for computing necessary data and block widths
package hamming_pkg is

  -- Computes the number of bits required for the Hamming block based on the
  -- number of data bits `k`.
  function block_width(k: pint) return pint;

  -- Computes the number of parity bits required to use the Hamming code based
  -- on the number of data bits `k`.
  function parity_count(k: pint) return pint;

end package;


package body hamming_pkg is 

  function block_width(k: pint) return pint is
  begin
    return k+parity_count(k)+1;
  end function;

  function parity_count(k: pint) return pint is
    variable p: pint := 2;
    variable d: pint := k + 1;
  begin
    while true loop
      if d <= (2**p) - p then
        exit;
      end if;
      p := p + 1;
    end loop;
    return p;
  end function;

end package body;
