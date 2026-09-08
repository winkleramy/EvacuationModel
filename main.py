import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import osmnx as ox
import networkx as nx

# Download the local driving network
G = ox.graph_from_place(
    "Santa Cruz County, California",
    network_type="drive"
)

# Geocode approximate intersection anchors
mar_vista_point = ox.geocode(
    "25980 Highland Way, Los Gatos, CA 95033"
)

spanish_ranch_point = ox.geocode(
    "Mar Vista Road and Highland Way, Santa Cruz County, California"
)

print("Mar Vista:", mar_vista_point)
print("Spanish Ranch:", spanish_ranch_point)

# Snap each point to the nearest drivable road node
mar_node = ox.distance.nearest_nodes(
    G,
    X=mar_vista_point[1],
    Y=mar_vista_point[0]
)

spanish_node = ox.distance.nearest_nodes(
    G,
    X=spanish_ranch_point[1],
    Y=spanish_ranch_point[0]
)

# Find shortest drivable path
route = nx.shortest_path(
    G,
    mar_node,
    spanish_node,
    weight="length"
)

# Calculate route length
length_meters = nx.path_weight(
    G,
    route,
    weight="length"
)

length_miles = length_meters / 1609.344

print(f"Distance: {length_miles:.3f} miles")

# Visual check
ox.plot_graph_route(G, route)

RNG = np.random.default_rng(42)

SECONDS_PER_MINUTE = 60

MEAN_TICKET_MIN = 45
SIGMA_TICKET_MIN = 15

# Vehicles per source

import pandas as pd

communities = pd.DataFrame({
    "source": [
        "Mt Bache",
        "Highland",
        "Mar Vista",
        "Spanish Ranch",
        "Radonich",
        "Skyland",
        "Summit Woods",
    ],
    "dwellings": [
        80,
        20,
        11,
        18,
        28,
        80,
        49,
    ]
})

VEHICLES_PER_DWELLING = 2.3

communities["vehicles"] = (
    communities["dwellings"] * VEHICLES_PER_DWELLING
).round().astype(int)

print(communities)

routes = pd.DataFrame([
    # Mt Bache
    ["Mt Bache", 1, "node", "Washout"],
    ["Mt Bache", 2, "road", "Mt Bache Road"],
    ["Mt Bache", 3, "node", "Mt Bache / Highland"],
    ["Mt Bache", 4, "road", "Highland Way"],

    # Highland
    ["Highland", 1, "node", "Mar Vista Merge"],
    ["Highland", 2, "road", "Highland Way"],
    ["Highland", 3, "node", "Spanish Ranch Merge"],
    ["Highland", 4, "road", "Highland Way"],
    ["Highland", 5, "node", "Mt Bache / Highland"],
    ["Highland", 6, "road", "Highland Way"],

    # Mar Vista
    ["Mar Vista", 1, "node", "Mar Vista Merge"],
    ["Mar Vista", 2, "road", "Highland Way"],
    ["Mar Vista", 3, "node", "Spanish Ranch Merge"],
    ["Mar Vista", 4, "road", "Highland Way"],
    ["Mar Vista", 5, "node", "Mt Bache / Highland"],
    ["Mar Vista", 6, "road", "Highland Way"],

    # Spanish Ranch
    ["Spanish Ranch", 1, "node", "Spanish Ranch Merge"],
    ["Spanish Ranch", 2, "road", "Highland Way"],
    ["Spanish Ranch", 3, "node", "Mt Bache / Highland"],
    ["Spanish Ranch", 4, "road", "Highland Way"],
], columns=[
    "source",
    "step",
    "type",
    "location"
])

print(routes)

network = pd.DataFrame([
    # id    name                     type   process_time 
    ["N1",  "Washout",                  "node",   8.  ],
    ["N2",  "MtBache_Highland_Merge",   "node",   5   ],
    ["N3",  "MarVista_Merge",           "node",   6.25],
    ["N4",  "SpanishRanch_Merge",       "node",   6.25],
    ["N5",  "Radonich_Merge",           "node",   6.25],
    ["N6",  "Skyland_Merge",            "node",   6.25],
    ["N7",  "Summit_SSJ_Merge",    "node",   5.  ],

    ["R1",  "MtBache",                  "road",  60.  ],
    ["R2",  "Highland_to_SpanishRanch", "road",  60. ],
    ["R3",  "Highland_to_MtBacheMerge", "road",  20. ],
    ["R4",  "Highland_to_RadonichMerge", "road",  30. ],
    ["R5",  "Highland_to_SkylandMerge", "road",  30. ],
    ["R6",  "Highland_to_SSJ", "road",  60. ],
], columns=[
    "id",
    "name",
    "type",
    "process_time_sec",
])

print(network)

N = 150

tickets = RNG.normal(
    loc=MEAN_TICKET_MIN*60,
    scale=SIGMA_TICKET_MIN*60,
    size=N
)

tickets = np.clip(tickets, 0, None)
tickets = tickets.astype(int)

vehicles = pd.DataFrame({
    "vehicle_id": np.arange(N),
    "source": "Mt Bache",
    "ticket_time": tickets,
    "state": "not_departed",
    "location": "home",
})
