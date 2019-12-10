#!/bin/python

from os.path import splitext, basename
import pickle
import bz2
import argparse

from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser as parser
from ryu.ofproto.ofproto_v1_3_parser import (
    OFPFlowStats, OFPMatch, OFPInstructionGotoTable, OFPActionOutput,
    OFPActionSetField, OFPInstructionActions
)
parser = argparse.ArgumentParser(description='Build a rules with a given'
                                             'number of switching rules.')
parser.add_argument('rules', type=int)
args = parser.parse_args()

NUMBER_MACS = args.rules


"""
Make the rules for a simple L2 L3 pipeline, based on OF-DPA

                            ETH_DST 1&2

                           +--------------+
                           |              |
                           | 1 Routing    |
                           |              |
                           | IP_DST       +-------+
    +--------------+ +----->    OUTPUT    |       |                       ETH_SRC 10+ [VAR]
    |              | |     |    SET MAC   |       |    +-------------+  +---------------+
    | 0 MAC TERM   | |     |              |       |    | Filtering   |  |               |
    | ETH_DST +>   | |     |              |       |    | 3 TCP ACL   |  |  4 L2 SRC     |
    |   goto : 1   | |     +--------------+       |    | (TCP_DST)   |  |  IN_PORT      |
    |              +-+                            +---->  Clear      +-->  ETH_SRC      |
    | else         |                              |    |             |  |     GOTO      |
    | goto: 2      |                              |    |             |  |               |
    |              +-+       ETH_DST 10+ [VAR]    |    |             |  |  Miss:        |
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


def next_mac():
    mac = 10
    while True:
        yield mac
        mac += 1

def next_port():
    PORT_RANGE = range(10,20)
    while True:
        for port in PORT_RANGE:
            yield port

FW = []
LEARN = []
m = next_mac()
p = next_port()
for x in range(NUMBER_MACS):
    mac = m.next()
    port = p.next()
    FW.append(
        OFPFlowStats(table_id=2, priority=1000,
                     match=OFPMatch(eth_dst=mac),
                     instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_WRITE_ACTIONS,
                                   [OFPActionOutput(port)]), OFPInstructionGotoTable(3)]
                    )
            )
    LEARN.append(
        OFPFlowStats(table_id=4, priority=1000,
             match=OFPMatch(in_port=port, eth_src=mac),
             instructions=[]
            )
    )



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
] + FW + [
# Table 2
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
] + LEARN + [
# Table 4
OFPFlowStats(table_id=4, priority=0,
             match=OFPMatch(),
             instructions=[OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                                                 [OFPActionOutput(ofproto_v1_3.OFPP_CONTROLLER)]),
                          ]),


]


new_name = "../" + splitext(basename(__file__))[0] + "_" +  str(NUMBER_MACS) + ".pickle.bz2"
with bz2.BZ2File(new_name, 'wb') as f:
    pickle.dump(flows, f)
