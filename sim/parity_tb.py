import cocotb
import verb as vb
from verb import Model, Signal, Constant
import glyph as gl


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
            self.check.value = gl.get_parity(gl.pack(int(self.data.value)), even=self.EVEN.value)
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
