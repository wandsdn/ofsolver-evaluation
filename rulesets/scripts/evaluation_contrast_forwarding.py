from os.path import splitext, basename
import pickle

from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser as parser
from ryu.ofproto.ofproto_v1_3_parser import (
    OFPFlowStats, OFPMatch, OFPInstructionGotoTable, OFPActionOutput,
    OFPActionSetField, OFPInstructionActions
)

"""
Make the rules for a simple L2 L3 pipeline


  +------------+          +----------+
  | TCP filter |  +-->    | ETH, IP  |
  +------------+          |   etc    |
                          +----------+

The opposite of simple-ofdpa.

"""

flows = [
# Table 0, drop all traffic

OFPFlowStats(table_id=0, priority=1000,
             match=OFPMatch(tcp_dst=80),
             instructions=[]),
OFPFlowStats(table_id=0, priority=1000,
             match=OFPMatch(tcp_dst=443),
             instructions=[]),
OFPFlowStats(table_id=0, priority=0,
             match=OFPMatch(),
             instructions=[OFPInstructionGotoTable(1)]),


# Table 1, ETH, IP etc.

# Routing
OFPFlowStats(table_id=1, priority=1008,
             match=parser.OFPMatch(eth_dst=1, ipv4_dst=("1.0.0.0", "255.0.0.0")),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionSetField(eth_src=100), OFPActionSetField(eth_dst=20), OFPActionOutput(20)])]
            ),
OFPFlowStats(table_id=1, priority=1008,
             match=OFPMatch(eth_dst=2, ipv4_dst=("1.0.0.0", "255.0.0.0")),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionSetField(eth_src=100), OFPActionSetField(eth_dst=20), OFPActionOutput(20)])]
            ),
OFPFlowStats(table_id=1, priority=1008,
             match=OFPMatch(eth_dst=1, ipv4_dst=("10.0.0.0", "255.0.0.0")),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionSetField(eth_src=100), OFPActionSetField(eth_dst=20), OFPActionOutput(20)])]
            ),
OFPFlowStats(table_id=1, priority=1008,
             match=OFPMatch(eth_dst=2, ipv4_dst=("10.0.0.0", "255.0.0.0")),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionSetField(eth_src=100), OFPActionSetField(eth_dst=20), OFPActionOutput(20)])]
            ),
# Routing default
OFPFlowStats(table_id=1, priority=1000,
             match=OFPMatch(eth_dst=1),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionSetField(eth_src=101), OFPActionSetField(eth_dst=21), OFPActionOutput(21)])]
            ),
OFPFlowStats(table_id=1, priority=1000,
             match=OFPMatch(eth_dst=2),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionSetField(eth_src=101), OFPActionSetField(eth_dst=21), OFPActionOutput(21)])]
            ),
# SRC & DST match
OFPFlowStats(table_id=1, priority=100,
             match=OFPMatch(in_port=10, eth_src=10, eth_dst=10),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(10)])]
            ),
OFPFlowStats(table_id=1, priority=100,
             match=OFPMatch(in_port=11, eth_src=11, eth_dst=10),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(10)])]
            ),
OFPFlowStats(table_id=1, priority=100,
             match=OFPMatch(in_port=12, eth_src=12, eth_dst=10),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(10)])]
            ),
OFPFlowStats(table_id=1, priority=100,
             match=OFPMatch(in_port=10, eth_src=10, eth_dst=11),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(11)])]
            ),
OFPFlowStats(table_id=1, priority=100,
             match=OFPMatch(in_port=11, eth_src=11, eth_dst=11),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(11)])]
            ),
OFPFlowStats(table_id=1, priority=100,
             match=OFPMatch(in_port=12, eth_src=12, eth_dst=11),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(11)])]
            ),
OFPFlowStats(table_id=1, priority=100,
             match=OFPMatch(in_port=10, eth_src=10, eth_dst=12),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(12)])]
            ),
OFPFlowStats(table_id=1, priority=100,
             match=OFPMatch(in_port=11, eth_src=11, eth_dst=12),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(12)])]
            ),
OFPFlowStats(table_id=1, priority=100,
             match=OFPMatch(in_port=12, eth_src=12, eth_dst=12),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(12)])]
            ),

# SRC only
OFPFlowStats(table_id=1, priority=95,
             match=OFPMatch(in_port=10, eth_src=10),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(ofproto_v1_3.OFPP_FLOOD)])]
            ),
OFPFlowStats(table_id=1, priority=95,
             match=OFPMatch(in_port=11, eth_src=11),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(ofproto_v1_3.OFPP_FLOOD)])]
            ),
OFPFlowStats(table_id=1, priority=95,
             match=OFPMatch(in_port=12, eth_src=12),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(ofproto_v1_3.OFPP_FLOOD)])]
            ),

# DST only
OFPFlowStats(table_id=1, priority=90,
             match=OFPMatch(eth_dst=10),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(ofproto_v1_3.OFPP_CONTROLLER), OFPActionOutput(10)])]
            ),
OFPFlowStats(table_id=1, priority=90,
             match=OFPMatch(eth_dst=11),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(ofproto_v1_3.OFPP_CONTROLLER), OFPActionOutput(11)])]
            ),
OFPFlowStats(table_id=1, priority=90,
             match=OFPMatch(eth_dst=12),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                              [OFPActionOutput(ofproto_v1_3.OFPP_CONTROLLER), OFPActionOutput(12)])]
            ),

# No SRC, no DST

OFPFlowStats(table_id=1, priority=0,
             match=OFPMatch(),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                             [OFPActionOutput(ofproto_v1_3.OFPP_CONTROLLER), OFPActionOutput(ofproto_v1_3.OFPP_FLOOD)])]),
]

new_name = "../" + splitext(basename(__file__))[0] + ".pickle"
with open(new_name, 'wb') as f:
    pickle.dump(flows, f)
