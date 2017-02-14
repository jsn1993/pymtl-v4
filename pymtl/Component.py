import re, inspect, ast
p = re.compile('( *(@|def))')
from collections import defaultdict, deque

from Ports import *

class Component(object):

  # ``super( Model, self ).__init__()`` is too ugly

  def __new__( cls, *args, **kwargs ):
    inst = object.__new__( cls, *args, **kwargs )
    inst._funcid_methods = defaultdict(set)
    inst._id_upblk  = {}
    inst._rd_of_upblk = defaultdict(set)
    inst._wr_of_upblk = defaultdict(set)
    inst._connections = []    
    inst._schedule_list = []
    return inst

  def update( s, func ):
    func_id = id( func )
    s._id_upblk[ func_id ] = func

    src = p.sub( r'\2', inspect.getsource( func ) )
    tree = ast.parse( src )

    for node in ast.walk(tree):
      # Check if the node is a function call and the function name is not
      # not min,max,etc; it should at least have some dots: s.xx.xx

      if     isinstance( node, ast.Call ) and \
         not isinstance( node.func, ast.Name ):

        method_name = node.func.attr
        if method_name in [ "rd", "wr" ]:
          wire_name = node.func.value.attr
          s._funcid_methods[ func_id ].add( (wire_name, method_name) )

  def connect( s, a, b ):
    s._connections.append( (a, b) )

  def connect_dict( s, dic ):
    for x,y in dic.iteritems():
      s.connect( x, y )

  def _elaborate( s, model ):

    # Turn wire names into actual objects, and check if each name matches
    # the type of the wire

    for func, methods in model._funcid_methods.iteritems():
      for wire_name, method_name in methods:
        port   = model.__dict__[ wire_name ]
        method = getattr( port, method_name )

        # Only allow out.wr() and in.rd()

        if   isinstance( port, OutPort ):
          assert method_name == "wr"
          s._wr_of_upblk[func].add( port )

        elif isinstance( port, InPort ):
          assert method_name == "rd"
          s._rd_of_upblk[func].add( port )

    for name, obj in model.__dict__.iteritems():
      if   isinstance( obj, Component ):
        s._elaborate( obj ) # Do the recursion

        model._rd_of_upblk.update( obj._rd_of_upblk )
        model._wr_of_upblk.update( obj._wr_of_upblk )
        model._id_upblk.update( obj._id_upblk )
        model._connections.extend( obj._connections )

      elif isinstance( obj, InPort ) or isinstance( obj, OutPort ):
        obj.root = obj

  def _connectall( s ):

    # Flood-fill-like algorithm to handle all in/outports
    # TODO: add wires
    
    # first pass: connect all output-input pair
    # x(out) -> y(in) means y calls x.rd

    orphans = []

    in_connected  = set()
    out_connected = set()

    for a, b in s._connections:
      if isinstance( b, OutPort ):
        a, b = b, a

      if isinstance( a, OutPort ) and isinstance( b, InPort ):
        b.rd   = a.rd
        b.root = a.root # disjoint set, two connected ports have the same root
        in_connected.add( b )
        out_connected.add( a )
      else:
        orphans.append( (a, b) )

    # second pass: iteratively expand edges
    # x(in)  <-> y(in) : x is connected previously means y calls x.rd
    # x(out) <-> y(out): x is connected previously means
    # 1) y calls x.rd, and 2) y calls x.wr
    # TODO: use disjoint set instead of iterative expanding

    T = len(orphans)
    while orphans and T>=0:
      # We expect to stop before at most |orphan| iterations
      T -= 1

      ooorphans = []
      for (a, b) in orphans:
        if   isinstance( a, InPort ) and isinstance( b, InPort ):
          # FIXME
          assert not (a in in_connected and b in in_connected)
          assert not (a in out_connected and b in out_connected)

          if   a in in_connected:
            b.rd, b.root = a.rd, a.root
            in_connected.add( b )
          elif b in in_connected:
            a.rd, a.root = b.rd, b.root
            in_connected.add( a )
          else:
            ooorphans.append( (a, b) )
          
        elif isinstance( a, OutPort ) and isinstance( b, OutPort ):
          if   a in out_connected:
            b.rd, b.wr, b.root = a.rd, a.wr, a.root
            out_connected.add( b )
          elif b in out_connected:
            a.rd, a.wr, a.root = b.rd, b.wr, b.root
            out_connected.add( a )
          else:
            ooorphans.append( (a, b) )

        else: assert False, "Connection type mismatch"
      orphans = ooorphans

    assert T>=0

  def _schedule( s ):

    # Currently connecting two update blocks is done in O(n^2)
    # TODO: optimize to O(nlogn) or O(n)

    edges = defaultdict(set)
    # wr --> rd
    for x1, y1 in s._wr_of_upblk.iteritems():
      for x2, y2 in s._rd_of_upblk.iteritems():
        if x1 != x2:
          for z1 in y1:
            for z2 in y2:
              if z1.root == z2.root:
                edges[x1].add( x2 )

    # topo sort
    # FIFO makes more sense because all "seq" update blocks are scheduled
    # first

    InDeg = dict( (x, 0) for x in s._id_upblk )
    queue = deque()

    for v, es in edges.iteritems():
      for y in es:
        InDeg[y] += 1

    for (x, y) in InDeg.iteritems():
      if y == 0:
        queue.append( x )

    while queue:
      v = queue.popleft()
      s._schedule_list.append( s._id_upblk[v] )
      for y in edges[v]:
        InDeg[y] -= 1
        if InDeg[y] == 0:
          queue.append( y )
    
  def elaborate( s ):
    assert not s._schedule_list, "Already elaborated!"
    s._elaborate( s )
    s._connectall()
    s._schedule()
    assert len(s._schedule_list) == len(s._id_upblk), "Elaborated failed!"

  def cycle( s ):
    for x in s._schedule_list:
      x()

  def print_schedule( s ):
    for x in s._schedule_list:
      print x.__name__
