from Register import Register
from Test import *
from DumbUnit import *

class Harness(Component):

  def __init__( s ):

    s.src  = Source()
    s.sink = Sink()

    s.r00 = Register( int )
    s.r01 = Register( int )

    s.dmu  = DumbUnit( int )

    s.r10 = Register( int )
    s.r11 = Register( int )

    s.connect_dict({
      s.src.out0: s.r00.in_,
      s.src.out1: s.r01.in_,

      s.r00.out:  s.dmu.in0,
      s.r01.out:  s.dmu.in1,

      s.dmu.out0: s.r10.in_,
      s.dmu.out1: s.r11.in_,

      s.r10.out:  s.sink.in0,
      s.r11.out:  s.sink.in1,
    })

  def line_trace( s ):
    return s.src.line_trace()+" >> "+s.dmu.line_trace()+" >> "+s.sink.line_trace()

model = Harness()
model.elaborate()
model.print_schedule()

for x in xrange(10):
  model.cycle()
  print model.line_trace()
