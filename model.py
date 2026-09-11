import numpy as np
import pandas as pd
from display import *

RNG = np.random.default_rng(42)

def init(MEAN_TICKET,SIGMA_TICKET,communities):

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
                "start_time": ticket,
                "end_time": None,
                "commute_time": None,
                "state": "home",
                "current_node": "N0",
                "current_link": "L0",
                "incoming_link": None,
                "route_index" : 0,
            })

            vehicle_id += 1

    vehicles = pd.DataFrame(vehicle_rows)
    return vehicles

def release(vehicles,i, current_time):
    vehicles.at[i, "state"] = "finished"
    vehicles.at[i, "ticket_time"] = current_time
    vehicles.at[i, "end_time"] = current_time
    vehicles.at[i, "commute_time"] = current_time - vehicles.at[i, "start_time"]
    vehicles.at[i, "incoming_link"] = vehicles.at[i, "current_link"]
    vehicles.at[i, "current_link"] = None
    vehicles.at[i, "current_node"] = None


def move_vehicle(vehicles, routes, nodes, links, i, current_time):

    source = vehicles.at[i, "source"]
    route  = routes[source]

    if vehicles.at[i, "route_index"] >= len(route):
        release(vehicles, i, current_time)
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

def evacuate(vehicles, routes, nodes, links, fig = None, axes = None):

    history = []

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
            move_vehicle(vehicles, routes, nodes, links, i, current_time)

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

        # collect_statistics(second)
        history.append({
    
            "time": current_time,
    
            "vehicles_home":
                (vehicles["state"] == "home").sum(),
    
            "vehicles_driving":
                (vehicles["state"] == "driving").sum(),
    
            "vehicles_queued":
                ( (vehicles["state"] == "queued") | (vehicles["state"] == "processing") ).sum(),
    
            "vehicles_finished":
                (vehicles["state"] == "finished").sum(),

            **{
                f"{node_id}_{incoming_link}_queue":
                    nodes.at[(node_id, incoming_link), "queue_length"]
                for node_id, incoming_link in nodes.index
            }
    
            # "washout_queue":
            #     nodes.loc[("N1","L0"),"queue_length"],
    
            # "spanishranch_queue":
            #     nodes.loc[("N3","L0"),"queue_length"],
    
            # "mtbachehighlandL1_queue":
            #     nodes.loc[("N4","L1"),"queue_length"],
    
            # "mtbachehighlandL3_queue":
            #     nodes.loc[("N4","L3"),"queue_length"],
    
            # "skyland_queue":
            #     nodes.loc[("N7","L0"),"queue_length"],
    
            # "ssj_queue":
            #     nodes.loc[("N8","L8"),"queue_length"],
    
        })

        if fig is not None and axes is not None:
            #display_current_state(fig, ax, vehicles, routes, current_time)
            #display_network_state(fig, ax, vehicles, nodes, links, current_time)
            display_network_state_by_movement( fig, axes, vehicles, nodes, links, current_time )
    
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

    return vehicles, nodes, links, history
