library stl;
context stl.prelude;

-- Hamming code package for computing necessary data and block widths
package hamming_pkg is

    -- Computes the number of data bits for a hamming-code block.
    function data_width(parity_bits: pint range 2 to pint'high) return pint;

    -- Computes the number of bits in the entire hamming-code block.
    function block_width(parity_bits: pint range 2 to pint'high) return pint;

end package;


package body hamming_pkg is 

    function data_width(parity_bits: pint range 2 to pint'high) return pint is
    begin
        return (2**parity_bits)-parity_bits-1;
    end function;

    function block_width(parity_bits: pint range 2 to pint'high) return pint is
    begin
        return 2**parity_bits;
    end function;

end package body;