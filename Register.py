from pymtl import *

class Register(Component):

  def __init__( s, typ ):

    s.in_   = InPort ( typ )
    s.out   = OutPort( typ )
    s.state = typ()

    @s.update
    def update_reg_in_to_state():
      s.state = s.in_.rd()

    @s.update
    def update_reg_state_to_out():
      s.out.wr( s.state )

  def line_trace( s ):
    return "" + s.state
