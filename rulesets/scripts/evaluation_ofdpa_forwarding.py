#!/bin/python

from os.path import splitext, basename
import pickle

from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser as parser
from ryu.ofproto.ofproto_v1_3_parser import (
    OFPFlowStats, OFPMatch, OFPInstructionGotoTable, OFPActionOutput,
    OFPActionSetField, OFPInstructionActions
)


"""
Make the rules for a simple L2 L3 pipeline, based on OF-DPA

                            ETH_DST 1&2

                           +--------------+
                           |              |
                           | 1 Routing    |
                           |              |
                           | IP_DST       +-------+
    +--------------+ +----->    OUTPUT    |       |                       ETH_SRC 10&11&12
    |              | |     |    SET MAC   |       |    +-------------+  +---------------+
    | 0 MAC TERM   | |     |              |       |    | Filtering   |  |               |
    | ETH_DST +>   | |     |              |       |    | 3 TCP ACL   |  |  4 L2 SRC     |
    |   goto : 1   | |     +--------------+       |    | (TCP_DST)   |  |  IN_PORT      |
    |              +-+                            +---->  Clear      +-->  ETH_SRC      |
    | else         |                              |    |             |  |     GOTO      |
    | goto: 2      |                              |    |             |  |               |
    |              +-+       ETH_DST 10&11&12     |    |             |  |  Miss:        |
    +--------------+ |     +---------------+      |    |             |  |  SND_CTR      |
                     |     |               |      |    +-------------+  |               |
                     |     |  2 L2 DST     |      |                     +---------------+
                     |     |               |      |
                     +----->  ETH_DST      +------+
                           |     OUTPUT    |
                           |               |
                           |  Miss:        |
                           |  FLOOD        |
                           |               |
                           +---------------+

"""

flows = [
# Table 0 Mac Term
OFPFlowStats(table_id=0, priority=1000,
             match=OFPMatch(eth_dst=1),
             instructions=[OFPInstructionGotoTable(1)]),
OFPFlowStats(table_id=0, priority=1000,
             match=OFPMatch(eth_dst=2),
             instructions=[OFPInstructionGotoTable(1)]),
OFPFlowStats(table_id=0, priority=0,
             match=OFPMatch(),
             instructions=[OFPInstructionGotoTable(2)]),

# Table 1 Routing
OFPFlowStats(table_id=1, priority=1008,
             match=OFPMatch(ipv4_dst=("1.0.0.0", "255.0.0.0")),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_WRITE_ACTIONS,
                            [OFPActionSetField(eth_src=100), OFPActionSetField(eth_dst=20), OFPActionOutput(20)]),
                           OFPInstructionGotoTable(3)]
            ),
OFPFlowStats(table_id=1, priority=1008,
             match=OFPMatch(ipv4_dst=("10.0.0.0", "255.0.0.0")),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_WRITE_ACTIONS,
                            [OFPActionSetField(eth_src=100), OFPActionSetField(eth_dst=20), OFPActionOutput(20)]),
                           OFPInstructionGotoTable(3)]
             ),
OFPFlowStats(table_id=1, priority=1000,
             match=OFPMatch(ipv4_dst=("0.0.0.0", "0.0.0.0")),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_WRITE_ACTIONS,
                            [OFPActionSetField(eth_src=101), OFPActionSetField(eth_dst=21), OFPActionOutput(21)]),
                           OFPInstructionGotoTable(3)]
             ),
OFPFlowStats(table_id=1, priority=0,
             match=OFPMatch(),
             instructions=[OFPInstructionGotoTable(3)]),

# Table 2
OFPFlowStats(table_id=2, priority=1000,
             match=OFPMatch(eth_dst=10),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_WRITE_ACTIONS,
                           [OFPActionOutput(10)]), OFPInstructionGotoTable(3)]
            ),
OFPFlowStats(table_id=2, priority=1000,
             match=OFPMatch(eth_dst=11),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_WRITE_ACTIONS,
                           [OFPActionOutput(11)]), OFPInstructionGotoTable(3)]
             ),
OFPFlowStats(table_id=2, priority=1000,
             match=OFPMatch(eth_dst=12),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_WRITE_ACTIONS,
                           [OFPActionOutput(12)]), OFPInstructionGotoTable(3)]
             ),
OFPFlowStats(table_id=2, priority=0,
             match=OFPMatch(),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_WRITE_ACTIONS,
                           [OFPActionOutput(ofproto_v1_3.OFPP_FLOOD)]), OFPInstructionGotoTable(3)]),


OFPFlowStats(table_id=3, priority=1000,
             match=OFPMatch(tcp_dst=80),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_CLEAR_ACTIONS, [])]),
OFPFlowStats(table_id=3, priority=1000,
             match=OFPMatch(tcp_dst=443),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_CLEAR_ACTIONS, [])]),
OFPFlowStats(table_id=3, priority=900,
             match=OFPMatch(eth_dst=1),
             instructions=[]),
OFPFlowStats(table_id=3, priority=900,
             match=OFPMatch(eth_dst=2),
             instructions=[]),
OFPFlowStats(table_id=3, priority=0,
             match=OFPMatch(),
             instructions=[OFPInstructionGotoTable(4)]),

# Table 4
OFPFlowStats(table_id=4, priority=1000,
             match=OFPMatch(in_port=10, eth_src=10),
             instructions=[]
            ),
OFPFlowStats(table_id=4, priority=1000,
             match=OFPMatch(in_port=11, eth_src=11),
             instructions=[]
            ),
OFPFlowStats(table_id=4, priority=1000,
             match=OFPMatch(in_port=12, eth_src=12),
             instructions=[]
            ),
OFPFlowStats(table_id=4, priority=0,
             match=OFPMatch(),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                                                 [OFPActionOutput(ofproto_v1_3.OFPP_CONTROLLER)]),
                          ]),


]


new_name = "../" + splitext(basename(__file__))[0] + ".pickle"
with open(new_name, 'wb') as f:
    pickle.dump(flows, f)
