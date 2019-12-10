Here is the collection of Table Type Pattern pipeline descriptions used for
evaluation.

### Pipelines

#### evaluation_ofdpa_forwarding.json
A 5-table pipeline based on OF-DPA. This ruleset supports L2 forwarding,
L3 routing, and filtering based on TCP port. L2 and L3 forwarding decisions
happen before filtering using apply actions, which filtering can clear to drop
a packet. We have placed learning (a special table in OF-DPA) at the end of
the pipeline as to not learn filtered packets.
```

                           +--------------+
                           |              |
                           | 1 Routing    |
                           |              |
                           | IP_DST       +-------+
    +--------------+ +----->    OUTPUT    |       |
    |              | |     |    SET MAC   |       |    +-------------+  +---------------+
    | 0 MAC TERM   | |     |              |       |    | Filtering   |  |               |
    | ETH_DST +>   | |     |              |       |    | 3 TCP ACL   |  |  4 L2 SRC     |
    |   goto : 1   | |     +--------------+       |    | (TCP_DST)   |  |  IN_PORT      |
    |              +-+                            +---->  Clear      +-->  ETH_SRC      |
    | else         |                              |    |             |  |     GOTO      |
    | goto: 2      |                              |    |             |  |               |
    |              +-+                            |    |             |  |  Miss:        |
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
```


#### evaluation_contrast_forwarding.json
A synthetic 2-table pipeline which contrasts the ofdpa pipeline layout but
supports the same features. Filtering is done in the first table, and all L2
and L3 forwarding in the second table.
```
  +------------+          +----------+
  | TCP filter |  +-->    | ETH, IP  |
  +------------+          |   etc    |
                          +----------+
```

