import numpy as np
import matplotlib.pyplot as plt

def display_current_state(fig, ax, vehicles, routes, current_time):

    total_demand = len(vehicles[ 
        (vehicles["state"]=="driving") |
        (vehicles["state"]=="queued")
        ])

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
    ax.clear()
    im = ax.imshow(
        data,
        aspect="auto",
        interpolation="nearest"
    )

    # plt.colorbar(im, ax=ax, label="Vehicles")

    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.keys())

    ax.set_xticks(range(max_steps))
    ax.set_xticklabels(range(max_steps))

    ax.set_xlabel("Route Step")
    ax.set_ylabel("Community")
    ax.set_title("Current Evacuation State, Minute " + str(round(current_time/60)) + ", Vehicles on Road " + str(total_demand))

    plt.tight_layout()
    fig.canvas.draw_idle()
    plt.pause(0.01)

def display_network_state(fig, ax, vehicles, nodes, links, current_time):

    counts = {}

    # Count vehicles waiting at each node
    for node_id in nodes.index.get_level_values("id").unique():
        counts[node_id] = (
            ( (vehicles["state"] == "queued") | (vehicles["state"] == "processing") ) &
            (vehicles["current_node"] == node_id)
        ).sum()

    # Count vehicles driving on each link
    for link_id in links.index:
        counts[link_id] = (
            (vehicles["state"] == "driving") &
            (vehicles["current_link"] == link_id)
        ).sum()

    # Clear previous frame
    ax.clear()

    labels = list(counts.keys())
    values = list(counts.values())

    ax.barh(labels, values)

    ax.set_xlabel("Number of Vehicles")
    ax.set_ylabel("Network Element")
    ax.set_title(
        f"Evacuation Traffic — {current_time / 60:.1f} minutes"
    )

    # Show count at end of each bar
    for y, value in enumerate(values):
        ax.text(
            value + 0.5,
            y,
            str(value),
            va="center"
        )

    ax.set_xlim(
        0,
        max(10, max(values) + 10)
    )

    fig.canvas.draw_idle()
    plt.pause(0.01)

