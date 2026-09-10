import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from display import *
fig, ax = plt.subplots(figsize=(14, 6))

RNG = np.random.default_rng(42)

# Time to depart home in number of vehicles
MEAN_TICKET = 0 * 60
SIGMA_TICKET = 0 * 60
VEHICLES_PER_DWELLING = 2.3

# Vehicles per source
communities = pd.DataFrame({
    "source": [
        "MtBache", "Highland", "MarVista", "SpanishRanch", "Radonich", "Skyland1", "Skyland2", "SummitWoods",
    ],
    "dwellings": [
        65, 20, 11, 18, 28, 80, 80, 49,
    ]
})

communities["vehicles"] = (
    communities["dwellings"] * VEHICLES_PER_DWELLING
).round().astype(int)

print(communities)

vehicle_rows = []
vehicle_id = 0
for _, community in communities.iterrows():

    tickets = RNG.normal(
        loc=MEAN_TICKET,
        scale=SIGMA_TICKET,
        size=community["vehicles"],
    )

    tickets = np.clip(tickets, 0, None).astype(int)

    for ticket in tickets:

        vehicle_rows.append({
            "vehicle_id": vehicle_id,
            "source": community["source"],
            "ticket_time": ticket,
            "state": "home",
            "current_node": "N0",
            "current_link": "L0",
            "incoming_link": None,
            "route_index" : 0,
        })

        vehicle_id += 1

vehicles = pd.DataFrame(vehicle_rows)

nodes = pd.DataFrame([
    # id    name               incoming_link    priority   process_time 
    ["N1",  "Washout",                  "L0",   1,          8., (37.104740, -121.898612)],
    ["N2",  "MtBache_Highland_Merge",   "L1",   1,          5., (37.1060157, -121.9001665)],
    ["N2",  "MtBache_Highland_Merge",   "L4",   1,          5., (37.1060157, -121.9001665)],
    ["N3",  "MarVista_Merge",           "L0",   2,          5., (37.102582, -121.896839)],
    ["N3",  "MarVista_Merge",           "L99",  1,          1., (37.102582, -121.896839)],
    ["N4",  "SpanishRanch_Merge",       "L0",   2,          5., (37.105577, -121.900078)],
    ["N4",  "SpanishRanch_Merge",       "L3",   1,          1., (37.105577, -121.900078)],
    ["N5",  "Radonich_Merge",           "L0",   2,          5., (37.108186, -121.904559)],
    ["N5",  "Radonich_Merge",           "L2",   1,          1., (37.108186, -121.904559)],
    ["N6",  "Skyland_Merge",            "L0",   2,          5., (37.116451, -121.921693)],
    ["N6",  "Skyland_Merge",            "L5",   1,          1., (37.116451, -121.921693)],
    ["N7",  "Summit_SSJ_Merge",         "L9",   2,          5., (37.118710, -121.925394)],
    ["N7",  "Summit_SSJ_Merge",         "L6",   1,          1., (37.118710, -121.925394)],
    ["N8",  "LomaPrieta_Merge",         "L0",   2,          5., (37.121319, -121.931327)],
    ["N8",  "LomaPrieta_Merge",         "L7",   1,          1., (37.121319, -121.931327)],
    ["N9",  "SummitWoods_Merge",        "L0",   1,          5., (37.112855, -121.947596)],
    ["N10", "MillerCutoff_Merge",       "L0",   2,          5., (37.116080, -121.933509)],
    ["N10", "MillerCutoff_Merge",       "L8",   1,          1., (37.116080, -121.933509)],
    ["N99", "Highland",                 "L0",   1,          1., (37.102582, -121.896839)]
], columns=[
    "id",
    "name",
    "incoming_link",
    "priority",
    "process_time_sec",
    "location"
])

nodes["queue_length"] = 0
nodes["state"] = "free"
nodes["next_available_time"] = 0
nodes = nodes.set_index(["id","incoming_link"])

print(nodes)

routes = {
    "MtBache":          ["N1", "L1", "N2", "L2", "N5", "L5", "N6", "L6", "N7", "L7", "N8"],
    "Highland":         ["N99", "L99", "N3", "L3", "N4", "L4", "N2", "L2", "N5", "L5", "N6", "L6", "N7", "L7", "N8"],
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
    ["L4",  "N4",  "N2",  "Highland Way",       154./5280, 25],
    ["L5",  "N5",  "N6",  "Highland Way",       1.1,       25],
    ["L6",  "N6",  "N7",  "Highland Way",       0.3,       25],
    ["L7",  "N7",  "N8",  "Summit Rd",          0.4,       25],
    ["L8",  "N9",  "N10",   "Soquel San Jose Rd",   0.9,   25],
    ["L9",  "N10",  "N7",   "Soquel San Jose Rd",   0.5,   25],
    ["L99",  "N99",  "N3",   "Highland Way",     0.5,       25],
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

def move_vehicle(vehicles, routes, nodes, i, current_time):

    source = vehicles.at[i, "source"]
    route  = routes[source]

    if vehicles.at[i, "route_index"] >= len(route):
        vehicles.at[i, "state"] = "finished"
        vehicles.at[i, "ticket_time"] = current_time
        vehicles.at[i, "incoming_link"] = vehicles.at[i, "current_link"]
        vehicles.at[i, "current_link"] = None
        vehicles.at[i, "current_node"] = None
        return

    next_step = route[vehicles.at[i, "route_index"]]

    # move to link
    if next_step[0]=="L":
        vehicles.at[i, "current_node"]  = None
        vehicles.at[i, "incoming_link"] = vehicles.at[i, "current_link"]
        vehicles.at[i, "current_link"]  = next_step
        vehicles.at[i, "ticket_time"]   = current_time+links.at[next_step, "process_time_sec"]
        vehicles.at[i, "state"]         = "driving"

    # move to resource/node
    if next_step[0]=="N":
        incoming_link = vehicles.at[i, "current_link"]
        nodes.at[(next_step, incoming_link), "queue_length"] += 1
        vehicles.at[i,"current_node"] = next_step
        vehicles.at[i, "incoming_link"] = incoming_link
        vehicles.at[i,"current_link"] = None
        vehicles.at[i,"ticket_time"] = current_time #+nodes.at[(next_step, vehicles.at[i, "incoming_link"]),"process_time_sec"]*nodes.at[(next_step, vehicles.at[i, "incoming_link"]),"queue_length"]
        vehicles.at[i, "state"] = "queued"
        
    vehicles.at[i, "route_index"] +=1

history = []

plt.ion()
current_time = vehicles["ticket_time"].min()
while True:

    # -----------------------------
    # Process all vehicle events
    # -----------------------------
    ready = vehicles[
        (vehicles["ticket_time"] <= current_time) &
        (vehicles["state"] != "queued") &
        (vehicles["state"] != "finished")
    ]

    for i in ready.index:
        move_vehicle(vehicles, routes, nodes, i, current_time)

    # -----------------------------
    # Process all node releases
    # -----------------------------
    nodes.loc[ nodes["next_available_time"] <= current_time, "state" ] = "free"
    ready = nodes[
        (nodes["queue_length"] > 0) &
        (nodes["next_available_time"] <= current_time)
    ]

    for node_id in ready.index.get_level_values("id").unique():

        queued = vehicles[
            (vehicles["state"] == "queued") &
            (vehicles["current_node"] == node_id) &
            (vehicles["ticket_time"] <= current_time)
        ]

        if queued.empty:
            continue

        # FIFO, Oldest vehicle in the queue
        # i = queued["ticket_time"].idxmin()

        # First Vehicle with highest priority
        queued["priority"] = [ nodes.at[(node_id, link), "priority"] for link in queued["incoming_link"] ]
        queued["process_time_sec"] = [ nodes.at[(node_id, link), "process_time_sec"] for link in queued["incoming_link"] ]

        queued = queued.sort_values(["priority", "ticket_time"])
        i = queued.index[0]

        incoming_link = vehicles.at[i, "incoming_link"]
        vehicles.at[i,"ticket_time"] = current_time + nodes.at[(node_id, incoming_link), "process_time_sec"]
        vehicles.at[i, "state"] = "processing"
        nodes.at[(node_id, incoming_link), "queue_length"] -= 1
        nodes.loc[(node_id, slice(None)), "state"] = "processing"
        nodes.loc[(node_id, slice(None)), "next_available_time" ] = current_time + nodes.at[(node_id, incoming_link), "process_time_sec"]

        # # Move vehicle to the next link
        # move_vehicle(vehicles, routes, nodes, i, current_time)

        # # Reserve the node for another process_time seconds
        # incoming_link = queued.at[i, "incoming_link"]
        # nodes.at[(node_id, incoming_link), "queue_length"] -= 1
        # nodes.at[(node_id, incoming_link), "next_available_time" ] = current_time + nodes.at[(node_id, incoming_link), "process_time_sec"]


    # collect_statistics(second)
    history.append({

        "time": current_time,

        "vehicles_home":
            (vehicles["state"] == "home").sum(),

        "vehicles_driving":
            (vehicles["state"] == "driving").sum(),

        "vehicles_queued":
            (vehicles["state"] == "queued").sum(),

        "vehicles_finished":
            (vehicles["state"] == "finished").sum(),

        "washout_queue":
            nodes.loc[("N1","L0"),"queue_length"],

        "spanishranch_queue":
            nodes.loc[("N3","L0"),"queue_length"],

        "mtbachehighland_queue":
            nodes.loc[("N4",slice(None)),"queue_length"].sum(),

        "skyland_queue":
            nodes.loc[("N7","L0"),"queue_length"],

        "ssj_queue":
            nodes.loc[("N8","L8"),"queue_length"],

    })

    #display_current_state(fig, ax, vehicles, routes, current_time)
    display_network_state(fig, ax, vehicles, nodes, links, current_time)

    # -----------------------------
    # Find next event
    # -----------------------------

    vehicle_events = vehicles.loc[
        (vehicles["state"] != "finished") &
        (vehicles["state"] != "queued"),
        "ticket_time"
    ]

    node_events = nodes.loc[
        nodes["queue_length"] > 0,
        "next_available_time"
    ]

    # node_events = vehicles.loc[
    #     vehicles["state"] == "queued",
    #     "ticket_time"
    # ]

    if vehicle_events.empty and node_events.empty:
        break

    candidates = []

    if not vehicle_events.empty:
        candidates.append(vehicle_events.min())

    if not node_events.empty:
        candidates.append(node_events.min())

    current_time = min(candidates)

history = pd.DataFrame(history)

fig1, ax1 = plt.subplots(figsize=(14, 6))
ax1.plot(history["time"]/60, history["vehicles_finished"])

print( vehicles.loc[ vehicles["state"] != "finished" ] )
print("Evacuation Completed in ", str(round(current_time/60,2)), " minutes")
plt.ioff()
plt.show()