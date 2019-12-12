Here is the collection of OpenFlow 1.3 rulesets used for evaluation.
The rulesets are a pickled list of ryu rules and are compressed in some cases.

### Faucet directory

[Faucet](faucet) contains the real-world rulesets captured from a Faucet
deployment.

### Scripts directory
The scripts directory contains the scripts which generate these rulesets.

### Rulesets

#### evaluation_ofdpa_forwarding.pickle
A synthetic ruleset with L2 forwarding, L3 routing, and filtering based on TCP port.
The ruleset fits the [evaluation_ofdpa_forwarding.json](../pipelines/evaluation_ofdpa_forwarding.json) pipeline directly.


#### evaluation_contrast_forwarding.pickle
A synthetic ruleset which has equivalent fowarding to evaluation_ofdpa_forwarding.pickle,
but fits the [evaluation_contrast_forwarding.json](../pipelines/evaluation_contrast_forwarding.json) pipeline.

#### evaluation_ofdpa_gen*.pickle.bz2
Synthetic rulesets based on evaluation_ofdpa_forwarding.pickle, but with a varying number of L2 hosts learnt.

