This directory contains a ruleset capture of [redcables](https://monitoring.redcables.wand.nz/) on the 4th July 2017 as programmed by the [Faucet](https://github.com/faucetsdn/faucet) controller. 

I used these rulesets as real-world examples in my thesis. The rulesets are not identical to those used in my experiments as I have anonymised them for public release. I have anonymised the Ethernet addresses and each corresponding autoconfigured IPv6 address. I replaced the last 24-bits of the Ethernet address with a unique number counting from 1 for all non-local and non-multicast Ethernet addresses. As such, the canonical BDD representation of these rulesets will differ in size by a small amount from those published.

### Files and network configuration
The configuration for the redcables network can be found [here](https://github.com/wandsdn/redcables-ansible/tree/f44331c613a471301c4788cedc2a22d468564f7b). All captures are provided as bz2 Ryu pickles of the ruleset.

_ovs-redcables_ was configured for routing & forwarding & security
_at-x930, x510, x210_ were configured for forwarding & security
_cisco-3850_ was configured for forwarding but had security ACLs disabled
_aruba-2930_ was configured for forwarding but had security ACLs disabled

In my thesis and related publications, Faucet Router refers to the _ovs-redcables_ ruleset and  Faucet Access the _at-x510-1_ ruleset.
