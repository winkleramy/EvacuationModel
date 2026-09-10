import numpy as np
import pandas as pd
from model import *
from display import *

WASHOUT_TIME    = 1     # seconds crossing a washout
STOP_TIME       = 5     # seconds merging at stop sign or yield
GAP_TIME        = 3     # gap needed to merge in seconds
SPEED           = 25    # speed on roadways, mph

def test_washout():

    # Time to depart home in number of vehicles
    MEAN_TICKET = 0 * 60
    SIGMA_TICKET = 0 * 60
    VEHICLES_PER_DWELLING = 2.3

    # Vehicles per source
    communities = pd.DataFrame({
        "source": [ "MtBache" ],
        "dwellings": [ 65 ]
    })

    communities["vehicles"] = (
        communities["dwellings"] * VEHICLES_PER_DWELLING
    ).round().astype(int)

    nodes = pd.DataFrame([
        # id    name               incoming_link    priority   process_time 
        ["N1",  "Washout",                  "L0",   1,          WASHOUT_TIME, (37.104740, -121.898612)]
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

    routes = { "MtBache": ["N1", "L1"] }


    links = pd.DataFrame([
        # id     from   to     road_name       length_mi  speed_mph
        ["L1",  "N1",  "N2",  "Mt Bache Rd",        0.1,       SPEED],
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

    expected = nodes.at[("N1", "L0"), "process_time_sec"] * communities["vehicles"].sum() + links.at[("L1"), "process_time_sec"]

    return MEAN_TICKET, SIGMA_TICKET, communities, routes, nodes, links, expected

def test_mtbacheloma():

    # Time to depart home in number of vehicles
    MEAN_TICKET = 0 * 60
    SIGMA_TICKET = 0 * 60
    VEHICLES_PER_DWELLING = 2.3

    # Vehicles per source
    communities = pd.DataFrame({
        "source": [ "MtBache", "Highland", "MarVista", "SpanishRanch" ],
        "dwellings": [ 65, 20, 11, 18 ]
    })

    communities["vehicles"] = (
        communities["dwellings"] * VEHICLES_PER_DWELLING
    ).round().astype(int)

    nodes = pd.DataFrame([
        # id    name               incoming_link    priority   process_time 
        ["N1",  "Washout",                  "L0",   1,          WASHOUT_TIME, (37.104740, -121.898612)],
        ["N2",  "MarVista_Merge",           "L0",   2,          STOP_TIME,  (37.102582, -121.896839)],
        ["N2",  "MarVista_Merge",           "L99",  1,          GAP_TIME,   (37.102582, -121.896839)],
        ["N3",  "SpanishRanch_Merge",       "L0",   2,          STOP_TIME,  (37.105577, -121.900078)],
        ["N3",  "SpanishRanch_Merge",       "L2",   1,          GAP_TIME,   (37.105577, -121.900078)],
        ["N4",  "MtBache_Highland_Merge",   "L1",   1,          STOP_TIME,  (37.1060157, -121.9001665)],
        ["N4",  "MtBache_Highland_Merge",   "L3",   1,          STOP_TIME,  (37.1060157, -121.9001665)],
        ["N99", "Highland",                 "L0",   1,          GAP_TIME,   (37.102582, -121.896839)]
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


    links = pd.DataFrame([
        # id     from   to     road_name       length_mi  speed_mph
        ["L1",  "N1",  "N4",    "Mt Bache Rd",  0.1,        SPEED],
        ["L2",  "N2",  "N3",    "Highland Way", 0.4,        SPEED],
        ["L3",  "N3",  "N4",    "Highland Way", 154./5280,  SPEED],
        ["L99", "N99", "N2",    "Highland Way", 0.5,        SPEED],
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

    routes = { 
        "MtBache":          ["N1", "L1", "N4"],
        "Highland":         ["N99", "L99", "N2", "L2", "N3", "L3", "N4"],
        "MarVista":         ["N2", "L2", "N3", "L3", "N4"], 
        "SpanishRanch":     ["N3", "L3", "N4"],
               }

    expected = 0 # nodes.at[("N1", "L0"), "process_time_sec"] * communities["vehicles"].sum() + links.at[("L1"), "process_time_sec"]

    return MEAN_TICKET, SIGMA_TICKET, communities, routes, nodes, links, expected

if __name__ == "__main__":

    # MEAN_TICKET, SIGMA_TICKET, communities, routes, nodes, links, expected = test_washout()
    MEAN_TICKET, SIGMA_TICKET, communities, routes, nodes, links, expected = test_mtbacheloma()
    vehicles = init(MEAN_TICKET,SIGMA_TICKET,communities)

    # fig,ax = plt.subplots(figsize=(14, 6))
    fig, axes = plt.subplots( 2, 1, figsize=(14, 6), gridspec_kw={"height_ratios": [3, 1]})
    fig.tight_layout(pad=2.0)
    fig.subplots_adjust(hspace=0.6)
    vehicles, history = evacuate(vehicles, routes, nodes, links, fig, axes)

    actual = max(vehicles["commute_time"])

    print("Actual - Expected (minutes):")
    print((actual - expected) / 60)

    fig1, ax1 = plt.subplots(figsize=(14, 6))
    ax1.plot(history["time"]/60, history["vehicles_finished"], label="Vehicles Finished")
    for source in vehicles["source"].unique():
        ax1.plot(vehicles.loc[vehicles["source"]==source,"commute_time"] / 60, label=source)

    # Expected maximum commute time
    ax1.axvline(
        expected / 60,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Expected = {expected/60:.1f} min"
    )

    # Actual maximum commute time (optional)
    ax1.axvline(
        actual / 60,
        color="green",
        linestyle="-",
        linewidth=2,
        label=f"Actual = {actual/60:.1f} min"
    )

    ax1.set_xlabel("Time (minutes)")
    ax1.set_ylabel("Number of vehicles evacuated")
    ax1.set_title("Evacuation vs Time")
    ax1.legend()

    fig2, ax2 = plt.subplots(figsize=(14, 6))
    ax2.hist(vehicles["commute_time"] / 60, bins=20)
    for source in vehicles["source"].unique():
        ax2.hist(vehicles.loc[vehicles["source"]==source,"commute_time"] / 60, bins=20)

    # Expected maximum commute time
    ax2.axvline(
        expected / 60,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Expected = {expected/60:.1f} min"
    )

    # Actual maximum commute time (optional)
    ax2.axvline(
        actual / 60,
        color="green",
        linestyle="-",
        linewidth=2,
        label=f"Actual = {actual/60:.1f} min"
    )
    
    ax2.set_xlabel("Commute time (minutes)")
    ax2.set_ylabel("Number of vehicles")
    ax2.set_title("Distribution of commute times")

    plt.show()

    print("end simulation")