import hamming

from verb.model import *
from verb import context

class Parity:

    def __init__(self, size: int, even_parity: bool):
        self.size = size
        self.is_even_par = even_parity

        self.data = Signal(size)
        self.check_bit = Signal()

    def setup(self):
        self.data.sample()

    def eval(self):
        result = hamming.set_parity_bit(self.data.get(list), use_even=self.is_even_par)
        self.check_bit.set(int(result))


def main():
    mdl = Parity(
        size=context.generic('SIZE', int),
        even_parity=context.generic('EVEN_PARITY', bool),
    )

    with vectors('inputs.txt', 'i') as inputs, vectors('outputs.txt', 'o') as outputs:
        for _ in range(1000):
            mdl.setup()
            inputs.push(mdl)
            mdl.eval()
            outputs.push(mdl)


if __name__ == '__main__':
    main()
