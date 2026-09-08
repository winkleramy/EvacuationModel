import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RNG = np.random.default_rng(42)

SECONDS_PER_MINUTE = 60

MEAN_TICKET_MIN = 45
SIGMA_TICKET_MIN = 15

# Vehicles per source

import pandas as pd

communities = pd.DataFrame({
    "source": [
        "MtBache",
        "Highland",
        "MarVista",
        "SpanishRanch",
        "Radonich",
        "Skyland1",
        "Skyland2",
        "SummitWoods",
    ],
    "dwellings": [
        65,
        20,
        11,
        18,
        28,
        80,
        80,
        49,
    ]
})

VEHICLES_PER_DWELLING = 2.3

communities["vehicles"] = (
    communities["dwellings"] * VEHICLES_PER_DWELLING
).round().astype(int)

print(communities)

nodes = pd.DataFrame([
    # id    name                     type   process_time 
    ["N1",  "Washout",                  "node",   8.  , (37.104740, -121.898612)],
    ["N2",  "MtBache_Highland_Merge",   "node",   5   , (37.1060157, -121.9001665)],
    ["N3",  "MarVista_Merge",           "node",   6.25, (37.102582, -121.896839)],
    ["N4",  "SpanishRanch_Merge",       "node",   6.25, (37.105577, -121.900078)],
    ["N5",  "Radonich_Merge",           "node",   6.25, (37.108186, -121.904559)],
    ["N6",  "Skyland_Merge",            "node",   6.25, (37.116451, -121.921693)],
    ["N7",  "Summit_SSJ_Merge",         "node",   6.25, (37.118710, -121.925394)],
    ["N8",  "LomaPrieta_Merge",         "node",   6.25, (37.121319, -121.931327)],
    ["N9",  "SummitWoods_Merge",        "node",   6.25, (37.112855, -121.947596)],
    ["N10", "MillerCutoff_Merge",       "node",   6.25, (37.116080, -121.933509)]
], columns=[
    "id",
    "name",
    "type",
    "process_time_sec",
    "location"
])

nodes["queue_length"] = 0
nodes["next_available_time"] = 0
nodes = nodes.set_index("id")

print(nodes)

routes = {
    "MtBache":          ["N1", "L1", "N2", "L2", "N5", "L5", "N6", "L6", "N7", "L7", "N8"],
    "Highland":         ["N3", "L3", "N4", "L4", "N2", "L2", "N5", "L5", "N6", "L6", "N7", "L7", "N8"],
    "MarVista":         ["N3", "L3", "N4", "L4", "N2", "L2", "N5", "L5", "N6", "L6", "N7", "L7", "N8"],
    "SpanishRanch":     ["N4", "L4", "N2", "L2", "N5", "L5", "N6", "L6", "N7", "L7", "N8"],
    "Radonich":         ["N5", "L5", "N6", "L6", "N7", "L7", "N8"],
    "Skyland1":         ["N6", "L6", "N7", "L7", "N8"],
    "Skyland2":         ["N10", "L9", "N7", "L7", "N8"],
    "SummitWoods":      ["N9", "L8", "N10", "L9", "N7", "L7", "N8"],
}

print(routes)

links = pd.DataFrame([
    # id     from   to     road_name       length_mi  speed_mph
    ["L1",  "N1",  "N2",  "Mt Bache Rd",        0.1,       25],
    ["L2",  "N2",  "N5",  "Highland Way",       0.3,       25],
    ["L3",  "N3",  "N4",  "Highland Way",       0.4,       25],
    ["L4",  "N4",  "N2",  "Highland Way",       154./5280,       25],
    ["L5",  "N5",  "N6",  "Highland Way",       1.1,       25],
    ["L6",  "N6",  "N7",  "Highland Way",       0.3,       25],
    ["L7",  "N7",  "N8",  "Summit Rd",          0.4,       25],
    ["L8",  "N9",  "N10",   "Soquel San Jose Rd",   0.9,   25],
    ["L9",  "N10",  "N7",   "Soquel San Jose Rd",   0.5,   25],
], columns=[
    "id",
    "from_node",
    "to_node",
    "road_name",
    "length_miles",
    "speed_mph",
])

links["process_time_sec"] = (
    links["length_miles"] / links["speed_mph"] * 3600
)

links = links.set_index("id")

print(links)

vehicle_rows = []

vehicle_id = 0

for _, community in communities.iterrows():

    tickets = RNG.normal(
        loc=MEAN_TICKET_MIN * 60,
        scale=SIGMA_TICKET_MIN * 60,
        size=community["vehicles"],
    )

    tickets = np.clip(tickets, 0, None).astype(int)

    for ticket in tickets:

        vehicle_rows.append({
            "vehicle_id": vehicle_id,
            "source": community["source"],
            "ticket_time": ticket,
            "state": "not_departed",
            "current_node": "N0",
            "current_link": "L0",
            "route_index" : 0,
        })

        vehicle_id += 1

vehicles = pd.DataFrame(vehicle_rows)

def display_current_state(vehicles, routes):

    counts = {}

    for source, route in routes.items():

        counts[source] = []

        for step in route:

            if step.startswith("N"):
                n = (
                    (vehicles["source"] == source) &
                    (vehicles["current_node"] == step)
                ).sum()

            else:
                n = (
                    (vehicles["source"] == source) &
                    (vehicles["current_link"] == step)
                ).sum()

            counts[source].append(n)

    # Make all rows the same length
    max_steps = max(len(values) for values in counts.values())

    data = np.array([
        values + [0] * (max_steps - len(values))
        for values in counts.values()
    ])

    # Plot
    fig, ax = plt.subplots(figsize=(14, 6))

    im = ax.imshow(
        data,
        aspect="auto",
        interpolation="nearest"
    )

    plt.colorbar(im, ax=ax, label="Vehicles")

    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.keys())

    ax.set_xticks(range(max_steps))
    ax.set_xticklabels(range(max_steps))

    ax.set_xlabel("Route Step")
    ax.set_ylabel("Community")
    ax.set_title("Current Evacuation State")

    plt.tight_layout()
    #plt.show()
    plt.pause(0.01)


def move_vehicle(vehicles, routes, nodes, i, current_time):

    source = vehicles.at[i, "source"]
    route  = routes[source]

    if vehicles.at[i, "route_index"] >= len(route):
        vehicles.at[i, "state"] = "finished"
        vehicles.at[i, "ticket_time"] = current_time
        return

    next_step = route[vehicles.at[i, "route_index"]]

    # move to link
    if next_step[0]=="L":
        vehicles.at[i,"current_link"] = next_step
        vehicles.at[i,"ticket_time"] = current_time+links.at[next_step, "process_time_sec"]
        vehicles.at[i, "state"] = "driving"

    # move to resource/node
    if next_step[0]=="N":
        vehicles.at[i,"current_node"] = next_step
        vehicles.at[i,"ticket_time"] = current_time+nodes.at[next_step,"process_time_sec"]
        vehicles.at[i, "state"] = "queued"
        nodes.at[next_step, "queue_length"] += 1

    vehicles.at[i, "route_index"] +=1


# simulation_length = 2*60*60
#for current_time in range(min(vehicles["ticket_time"]),simulation_length):
plt.ion()
current_time = vehicles["ticket_time"].min()
while True:

    # -----------------------------
    # Process all vehicle events
    # -----------------------------
    ready = vehicles[
        (vehicles["ticket_time"] <= current_time) &
        (vehicles["state"] != "queued")
    ]

    for i in ready.index:
        move_vehicle(vehicles, routes, nodes, i, current_time)

    # -----------------------------
    # Process all node releases
    # -----------------------------
    ready = nodes[
        (nodes["queue_length"] > 0) &
        (nodes["next_available_time"] <= current_time)
    ]

    for node_id in ready.index:

        queued = vehicles[
            (vehicles["state"] == "queued") &
            (vehicles["current_node"] == node_id) &
            (vehicles["ticket_time"] <= current_time)
        ]

        if queued.empty:
            continue

        # Oldest vehicle in the queue
        i = queued["ticket_time"].idxmin()

        # Move vehicle to the next link
        move_vehicle(vehicles, routes, nodes, i, current_time)

        # Reserve the node for another process_time seconds
        nodes.at[node_id, "next_available_time"] = (
            current_time + nodes.at[node_id, "process_time_sec"]
        )
        nodes.at[node_id, "queue_length"] -= 1

    # -----------------------------
    # Find next event
    # -----------------------------

    vehicle_events = vehicles.loc[
        vehicles["state"] != "finished",
        "ticket_time"
    ]

    node_events = nodes.loc[
        (nodes["queue_length"] > 0) &
        (nodes["next_available_time"] > current_time),
        "next_available_time"
    ]

    if vehicle_events.empty and node_events.empty:
        break

    candidates = []

    if not vehicle_events.empty:
        candidates.append(vehicle_events.min())

    if not node_events.empty:
        candidates.append(node_events.min())

    current_time = min(candidates)

    # collect_statistics(second)
    display_current_state(vehicles, routes)

