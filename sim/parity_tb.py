import cocotb
import verb as vb
from verb import Model, Signal, Constant


def check_parity(arr: list, make_even=True) -> bool:
    '''
    Checks if the `arr` has an odd amount of 0's in which case the parity bit
    must be set to '1' to achieve an even parity.

    If `make_even` is set to `False`, then odd parity will be computed and will
    seek to achieve an odd amount of '1's (including parity bit).
    '''
    # count the number of 1's in the list
    return (arr.count(1) % 2) ^ (make_even == False)


class Parity(Model):

    def __init__(self):
        self.W = Constant()
        self.EVEN = Constant()

        self.data = Signal()
        self.check = Signal()
        super().mirror()

    def define_coverage(self):
        from verb.coverage import CoverRange

        CoverRange(
            name="data range",
            span=self.data.span(),
            goal=5,
            target=self.data
        )

        CoverRange(
            name="check bit",
            span=self.check.span(),
            goal=1,
            target=self.check
        )

        super().cover()

    async def setup(self):
        while vb.running():
            self.randomize()
            await vb.falling_edge()

    async def model(self):
        while vb.running():
            await vb.rising_edge()
            self.check.value = check_parity([int(i) for i in bin(self.data.value)[2:]], use_even=self.EVEN.value)
            vb.assert_eq(self.check.get_handle(), self.check)


@cocotb.test()
async def test(top):
    '''
    Tests parity logic.
    '''
    vb.initialize(top)

    mdl = Parity()
    mdl.define_coverage()

    await vb.combine(
        cocotb.start_soon(mdl.setup()),
        cocotb.start_soon(mdl.model()),
    )

    vb.complete()
