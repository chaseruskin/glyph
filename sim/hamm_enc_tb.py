from hamming import HammingCode

from verb.model import *
from verb import context

class HammEnc:

    def __init__(self, parity_bits: int):
        self.parity_bits = parity_bits
        self._code = HammingCode(parity_bits=parity_bits)

        self.message = Signal(self._code.get_data_bits_len())
        self.encoding = Signal(self._code.get_total_bits_len())

    def setup(self):
        self.message.sample()

    def eval(self):
        bits = self._code.encode(self.message.get(list)[::-1])
        self.encoding.set(bits[::-1])

def main():
    mdl = HammEnc(context.generic('PARITY_BITS', int))

    with vectors('inputs.txt', 'i') as inputs, vectors('outputs.txt', 'o') as outputs:
        for _ in range(1000):
            mdl.setup()
            inputs.push(mdl)
            mdl.eval()
            outputs.push(mdl)


if __name__ == '__main__':
    main()