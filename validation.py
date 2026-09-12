import numpy as np
import pandas as pd
from model import *
from display import *

WASHOUT_TIME    = 8     # seconds crossing a washout
STOP_TIME       = 5     # seconds merging at stop sign or yield
SPEED           = 25    # speed on roadways, mph
CAPACITY        = 1900  # county road capacity, vehicles/hour
GAP_TIME        = 5 #3600/CAPACITY     # gap needed to merge in seconds

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
        ["L0", None, None,      "Home",                         0.5,        SPEED],
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
    MEAN_TICKET = 0 #45 * 60
    SIGMA_TICKET = 0 #15 * 60
    VEHICLES_PER_DWELLING = 2.3

    # Vehicles per source
    communities = pd.DataFrame({
        "source": [ "MtBache", "Highland", "MarVista", "SpanishRanch", "BurrellStation" ],
        "dwellings": [ 65, 20, 11, 18, 0./VEHICLES_PER_DWELLING ]
    })

    communities["vehicles"] = (
        communities["dwellings"] * VEHICLES_PER_DWELLING
    ).round().astype(int)

    nodes = pd.DataFrame([
        # id    name               incoming_link    priority   process_time 
        ["N1",  "Washout",                  "L0",   2,          WASHOUT_TIME, (37.104740, -121.898612)],
        ["N1",  "Washout",                  "L1",   1,          WASHOUT_TIME, (37.104740, -121.898612)],
        ["N2",  "MarVista_Merge",           "L0",   2,          STOP_TIME,  (37.102582, -121.896839)],
        ["N2",  "MarVista_Merge",           "L99",  1,          GAP_TIME,   (37.102582, -121.896839)],
        ["N3",  "SpanishRanch_Merge",       "L0",   2,          STOP_TIME,  (37.105577, -121.900078)],
        ["N3",  "SpanishRanch_Merge",       "L2",   1,          GAP_TIME,   (37.105577, -121.900078)],
        ["N4",  "MtBache_Highland_Merge",   "L1",   2,          STOP_TIME,  (37.1060157, -121.9001665)],
        ["N4",  "MtBache_Highland_Merge",   "L3",   2,          STOP_TIME,  (37.1060157, -121.9001665)],
        ["N4",  "MtBache_Highland_Merge",   "L4",   1,          STOP_TIME,  (37.1060157, -121.9001665)],
        ["N99", "Highland",                 "L0",   1,          GAP_TIME,   (37.102582, -121.896839)],
        ["N5",  "Radonich_Merge",           "L0",   1,          GAP_TIME,   (37.108412, -121.905887)]
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
        ["L0", None, None,      "Home",                         0.5,        SPEED],
        ["L99", "N99", "N2",    "Highland Way (pre Mar Vista)", 0.5,        SPEED],
        ["L1",  "N1",  "N4",    "Mt Bache Rd",  0.1,        SPEED],
        ["L2",  "N2",  "N3",    "Highland Way (post Mar Vista)", 0.4,        SPEED],
        ["L3",  "N3",  "N4",    "Highland Way (post Spanish Ranch)", 154./5280,  SPEED],
        ["L4",  "N4",   "N5",   "Highland Way (post Mt Bache)",  0.3,       SPEED]
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
        "BurrellStation":   ["N5", "L4", "N4", "L1", "N1"],
               }

    expected = 22*60 # nodes.at[("N1", "L0"), "process_time_sec"] * communities["vehicles"].sum() + links.at[("L1"), "process_time_sec"]

    return MEAN_TICKET, SIGMA_TICKET, communities, routes, nodes, links, expected

def test_summit():

    # Time to depart home in number of vehicles
    MEAN_TICKET = 42 * 60   # 50% ready within 42 minutes
    SIGMA_TICKET = 14 * 60  # 90% ready within 60 minutes, 99.99% within 84 minutes
    VEHICLES_PER_DWELLING = 2.3

    # Vehicles per source
    communities = pd.DataFrame({
        "source": [ "MtBache", "Highland", "MarVista", "SpanishRanch", "BurrellStation", "Radonich", "Skyland1", "Skyland2", "SummitWoods", "LomaPrieta" ],
        "dwellings": [ 65, 20, 11, 18, 30./VEHICLES_PER_DWELLING, 28, 80, 80, 49, 18 ]
    })

    communities["vehicles"] = (
        communities["dwellings"] * VEHICLES_PER_DWELLING
    ).round().astype(int)

    nodes = pd.DataFrame([
        # id    name               incoming_link    priority   process_time 
        ["N1",  "Washout",                  "L0",   2,          WASHOUT_TIME, (37.104740, -121.898612)],
        ["N1",  "Washout",                  "L1",   1,          WASHOUT_TIME, (37.104740, -121.898612)],
        ["N2",  "MarVista_Merge",           "L0",   2,          STOP_TIME,  (37.102582, -121.896839)],
        ["N2",  "MarVista_Merge",           "L99",  1,          GAP_TIME,   (37.102582, -121.896839)],
        ["N3",  "SpanishRanch_Merge",       "L0",   2,          STOP_TIME,  (37.105577, -121.900078)],
        ["N3",  "SpanishRanch_Merge",       "L2",   1,          GAP_TIME,   (37.105577, -121.900078)],
        ["N4",  "MtBache_Highland_Merge",   "L1",   2,          STOP_TIME,  (37.1060157, -121.9001665)],
        ["N4",  "MtBache_Highland_Merge",   "L3",   2,          STOP_TIME,  (37.1060157, -121.9001665)],
        ["N4",  "MtBache_Highland_Merge",   "L4",   1,          STOP_TIME,  (37.1060157, -121.9001665)],
        ["N99", "Highland",                 "L0",   1,          GAP_TIME,   (37.102582, -121.896839)],
        ["N5",  "Radonich_Merge",           "L0",   2,          GAP_TIME,   (37.108186, -121.904559)],
        ["N5",  "Radonich_Merge",           "L4",   1,          STOP_TIME,  (37.108186, -121.904559)],
        ["N6",  "BurrellStation",           "L0",   1,          GAP_TIME,   (37.108470, -121.905971)],      
        ["N7",  "Skyland_Merge",            "L0",   2,          STOP_TIME,  (37.116451, -121.921693)],      
        ["N7",  "Skyland_Merge",            "L5",   1,          GAP_TIME,   (37.116451, -121.921693)],
        ["N8",  "Summit_SSJ_Merge",         "L6",   1,          GAP_TIME,   (37.118710, -121.925394)],
        ["N8",  "Summit_SSJ_Merge",         "L8",   2,          STOP_TIME,  (37.118710, -121.925394)],
        ["N9",  "SummitWoods_Merge",        "L0",   2,          STOP_TIME,  (37.112855, -121.947596)],
        ["N10", "MillerCutoff_Merge",       "L0",   2,          STOP_TIME,  (37.116080, -121.933509)],
        ["N10", "MillerCutoff_Merge",       "L7",   1,          GAP_TIME,   (37.116080, -121.933509)],
        ["N11",  "LomaPrieta_Merge",        "L0",   2,          STOP_TIME,  (37.121319, -121.931327)],
        ["N11",  "LomaPrieta_Merge",        "L9",   1,          GAP_TIME,   (37.121319, -121.931327)],
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
        # id     from   to     road_name                        length_mi  speed_mph
        ["L0", None, None,      "Home",                         0.5,        SPEED],
        ["L99", "N99", "N2",    "Highland Way (pre Mar Vista)",   0.5,        SPEED],
        ["L1",  "N1",  "N4",    "Mt Bache Rd",                  0.1,        SPEED],
        ["L2",  "N2",  "N3",    "Highland Way (post Mar Vista)",  0.4,        SPEED],
        ["L3",  "N3",  "N4",    "Highland Way (post Spanish Ranch)", 154./5280,  SPEED],
        ["L4",  "N4",  "N5",   "Highland Way (post Mt Bache)",    0.3,        SPEED],
        ["L5",  "N5",  "N7",   "Highland Way (post Radonich)",    1.1,        SPEED],
        ["L6",  "N7",  "N8",    "Highland Way (post Skyland)",    0.3,        SPEED],
        ["L7",  "N9",  "N10",   "SSJ (post Summit Woods)",             0.9,        SPEED],
        ["L8",  "N10",  "N8",   "SSJ (post Miller Cutoff)",            0.5,        SPEED],
        ["L9",  "N8",  "N11",  "Summit Rd",                     0.4,        SPEED],
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
        "MtBache":          ["N1", "L1", "N4", "L4", "N5", "L5", "N7", "L6", "N8", "L9", "N11"],
        "Highland":         ["N99", "L99", "N2", "L2", "N3", "L3", "N4", "L4", "N5", "L5", "N7", "L6", "N8", "L9", "N11"],
        "MarVista":         ["N2", "L2", "N3", "L3", "N4", "L4", "N5", "L5", "N7", "L6", "N8", "L9", "N11"], 
        "SpanishRanch":     ["N3", "L3", "N4", "L4", "N5", "L5", "N7", "L6", "N8", "L9", "N11"],
        "BurrellStation":   ["N5", "L4", "N4", "L1", "N1"],
        "Radonich":         ["N5", "L5", "N7", "L6", "N8", "L9", "N11"],
        "Skyland1":         ["N7", "L6", "N8", "L9", "N11"],
        "Skyland2":         ["N10", "L8", "N8", "L9", "N11"],
        "SummitWoods":      ["N9", "L7", "N10", "L8", "N8", "L9", "N11"],
        "LomaPrieta":       ["N11"]
               }

    expected = 0 # nodes.at[("N1", "L0"), "process_time_sec"] * communities["vehicles"].sum() + links.at[("L1"), "process_time_sec"]

    return MEAN_TICKET, SIGMA_TICKET, communities, routes, nodes, links, expected

if __name__ == "__main__":

    # MEAN_TICKET, SIGMA_TICKET, communities, routes, nodes, links, expected = test_washout()
    # MEAN_TICKET, SIGMA_TICKET, communities, routes, nodes, links, expected = test_mtbacheloma()
    MEAN_TICKET, SIGMA_TICKET, communities, routes, nodes, links, expected = test_summit()
    vehicles = init(MEAN_TICKET,SIGMA_TICKET,communities)

    fig, axes = plt.subplots( 2, 1, figsize=(14, 8), gridspec_kw={"height_ratios": [2, 1]})
    fig.tight_layout(pad=2.0)
    fig.subplots_adjust(hspace=0.6)
    vehicles, nodes, links, history = evacuate(vehicles, routes, nodes, links) #, fig, axes)

    actual = max(vehicles["end_time"])
    commute = max(vehicles["commute_time"])

    print("Actual - Expected (minutes):")
    print((actual - expected) / 60)

    fig1, ax1 = plt.subplots(figsize=(7, 5))
    for source in vehicles["source"].unique():
        batch = vehicles.loc[vehicles["source"]==source]
        end_times = np.sort(batch["end_time"])
        x_time = np.insert(end_times, 0, 0) / 60          # minutes
        y_count = np.arange(len(end_times) + 1)
        ax1.step( x_time, y_count, where="post", label=source) 
        #ax1.plot(vehicles.loc[vehicles["source"]==source,"commute_time"] / 60, label=source)
    # ax1.plot(history["time"]/60, history["vehicles_finished"], '--', color="gray", label="Total Vehicles Finished")

    if expected > 0:
        # Expected maximum commute time
        ax1.axvline( expected / 60, color="red", linestyle="--", linewidth=2, label=f"Expected = {expected/60:.1f} min" )

        # Actual maximum commute time (optional)
        ax1.axvline( actual / 60, color="green", linestyle="-", linewidth=2, label=f"Actual = {actual/60:.1f} min" )

    ax1.set_xlabel("Elapsed Time since Evacuation Order (minutes)")
    ax1.set_ylabel("Number of vehicles evacuated")
    ax1.set_title("Evacuation vs Time")
    ax1.legend()

    fig2, ax2 = plt.subplots(figsize=(7, 5))
    group = vehicles.sort_values("start_time")
    # ax2.scatter(group["start_time"].values / 60, group["commute_time"].values / 60, label="Total")
    # ax2.hist(vehicles["commute_time"] / 60, bins=20, label="Total")
    for source in vehicles["source"].unique():
        group = vehicles.loc[vehicles["source"]==source].sort_values("start_time")
        ax2.plot(group["start_time"].values / 60, group["commute_time"].values / 60, "-o", label=source)
    
    ax2.set_xlabel("Departure time (minutes)")
    ax2.set_ylabel("Commute time (minutes)")
    ax2.set_title("Distribution of commute times")
    ax2.legend()

    fig3, ax3 = plt.subplots(figsize=(7, 5))
    ax3.hist(vehicles["start_time"] / 60, bins=20, label="Total")
    ax3.set_xlabel("Departure time post evacuation notice (minutes)")
    ax3.set_ylabel("Number of vehicles")
    ax3.set_title("Distribution of departure times")

    # fig4, ax4 = plt.subplots(figsize=(14,6))
    # for node_id, incoming_link in nodes.index:
    #     key = f"{node_id}_{incoming_link}_queue"
    #     label = f"{nodes.at[(node_id,incoming_link),'name']} ← {links.at[incoming_link,'road_name'].split(' (')[0]}"
    #     ax4.plot(history["time"].values / 60, history[key].values, label=label)
    # ax4.set_xlabel("Time (minutes)")
    # ax4.set_ylabel("Number of vehicles")
    # ax4.set_title("Evacuation Queue Lengths")  
    # ax4.legend()

    fig4, axes4, max_queues = plot_node_queues(history, nodes, links)

    plt.show()

    print("end simulation")