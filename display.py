import math
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

def display_network_state_by_movement( fig, axes, vehicles, nodes, links, current_time ):

    ax_nodes, ax_links = axes

    # -----------------------------
    # TOP: vehicles at each node movement
    # -----------------------------

    node_labels = []
    node_values = []

    for node_id, incoming_link in nodes.index:

        count = (
            (
                (vehicles["state"] == "queued") |
                (vehicles["state"] == "processing")
            )
            &
            (vehicles["current_node"] == node_id)
            &
            (vehicles["incoming_link"] == incoming_link)
        ).sum()

        node_name = nodes.at[
            (node_id, incoming_link),
            "name"
        ]

        if incoming_link == "L0":
            incoming_name = "Home"
        else:
            incoming_name = links.at[
                incoming_link,
                "road_name"
            ]

        node_labels.append(
            f"{node_name} ← {incoming_name}"
        )

        node_values.append(count)

    # -----------------------------
    # BOTTOM: vehicles on each link
    # -----------------------------

    link_labels = []
    link_values = []

    for link_id in links.index:

        if incoming_link == "L0":
            count(vehicles["state"] == "home").sum()

        else:
            count = ( (vehicles["state"] == "driving") & (vehicles["current_link"] == link_id) ).sum()

        link_labels.append(
            links.at[link_id, "road_name"]
        )

        link_values.append(count)

    # -----------------------------
    # Clear previous frame
    # -----------------------------

    ax_nodes.clear()
    ax_links.clear()

    # -----------------------------
    # Plot node movements
    # -----------------------------

    ax_nodes.barh(
        node_labels,
        node_values
    )

    ax_nodes.set_xlabel("Number of Vehicles")
    # ax_nodes.set_ylabel("Node / Incoming Link")
    ax_nodes.set_title(
        f"Node Queues — {current_time / 60:.1f} minutes"
    )

    for y, value in enumerate(node_values):
        ax_nodes.text(
            value + 0.5,
            y,
            str(value),
            va="center"
        )

    ax_nodes.set_xlim(
        0,
        max(10, max(node_values) + 10)
    )

    # -----------------------------
    # Plot road links
    # -----------------------------

    ax_links.barh(
        link_labels,
        link_values
    )

    ax_links.set_xlabel("Number of Vehicles")
    # ax_links.set_ylabel("Road Segment")
    ax_links.set_title("Vehicles Traveling on Links")

    for y, value in enumerate(link_values):
        ax_links.text(
            value + 0.5,
            y,
            str(value),
            va="center"
        )

    ax_links.set_xlim(
        0,
        max(10, max(link_values) + 10)
    )

    # -----------------------------
    # Refresh display
    # -----------------------------

    fig.tight_layout()

    fig.canvas.draw_idle()
    plt.pause(0.01)

# def plot_node_queues(history, nodes, links):

#     # One subplot for each node
#     node_ids = nodes.index.get_level_values("id").unique()

#     fig, axes = plt.subplots(
#         len(node_ids),
#         1,
#         figsize=(14, 2.5 * len(node_ids)),
#         sharex=True
#     )

#     # Handle case of only one node
#     if len(node_ids) == 1:
#         axes = [axes]

#     time = history["time"] / 60

#     for ax, node_id in zip(axes, node_ids):

#         # Node title
#         node_name = nodes.loc[(node_id, slice(None)), "name"].iloc[0]
#         ax.set_title(node_name)

#         # Plot every incoming approach
#         incoming_links = (
#             nodes.loc[(node_id, slice(None))]
#             .index
#             .get_level_values("incoming_link")
#         )

#         for incoming_link in incoming_links:

#             key = f"{node_id}_{incoming_link}_queue"

#             road_name = (
#                 links.at[incoming_link, "road_name"]
#                 .split(" (")[0]
#             )

#             ax.plot(
#                 time,
#                 history[key],
#                 label=road_name,
#                 linewidth=2
#             )

#         ax.set_ylabel("Vehicles")
#         ax.grid(alpha=0.3)
#         ax.legend(loc="upper right")

#     axes[-1].set_xlabel("Time (minutes)")

#     fig.suptitle(
#         "Queue Lengths Throughout Evacuation",
#         fontsize=16
#     )

#     fig.tight_layout()

#     return fig, axes


def plot_node_queues(history, nodes, links, ncols=3):

    node_ids = nodes.index.get_level_values("id").unique()

    nrows = math.ceil(len(node_ids) / ncols)

    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(15, 3 * nrows),
        sharex=True
    )

    # Flatten axes into one list
    axes = axes.flatten()

    time = history["time"] / 60

    for ax, node_id in zip(axes, node_ids):

        node_data = nodes.loc[(node_id, slice(None))]

        node_name = node_data["name"].iloc[0]

        incoming_links = (
            node_data
            .index
            .get_level_values("incoming_link")
        )

        for incoming_link in incoming_links:

            key = f"{node_id}_{incoming_link}_queue"

            road_name = (
                links.at[incoming_link, "road_name"]
                .split(" (")[0]
            )

            ax.plot(
                time,
                history[key],
                label=road_name,
                linewidth=1.5
            )

        ax.set_title(node_name)

        ax.set_ylabel("Vehicles")

        ax.grid(alpha=0.25)

        if len(incoming_links) > 1:
            ax.legend(fontsize=8)

    # Turn off unused subplot spaces
    for ax in axes[len(node_ids):]:
        ax.axis("off")

    # X-axis label on bottom row
    for ax in axes[-ncols:]:
        if ax.has_data():
            ax.set_xlabel("Time (minutes)")

    fig.suptitle(
        "Queue Lengths Throughout Evacuation",
        fontsize=16
    )

    fig.tight_layout()

    return fig, axes
