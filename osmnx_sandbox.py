import requests
import osmnx as ox
import networkx as nx

# ox.settings.use_cache = True
ox.settings.http_user_agent = (
    "EvacuationModel/1.0 (personal wildfire evacuation research)"
)

# Summit and Hwy 17: 37.145557, -121.984653
# Farthest point east along Highland Way: 37.095403, -121.877198
# Download the local driving network
bbox = (
    37.15,    # north
    37.09,    # south
    -121.87,  # east
    -121.99   # west
)

G = ox.graph_from_bbox(
    bbox,
    network_type="drive"
)

# Geocode approximate intersection anchors
mar_vista_point = (37.102582, -121.896839)
washout_point = (37.104740, -121.898612)
mtbache_highland_point = (37.1060157, -121.9001665)

print("Mar Vista:", mar_vista_point)
print("Washout:", washout_point)

# Snap each point to the nearest drivable road node
mar_node = ox.distance.nearest_nodes(
    G,
    X=mar_vista_point[1],
    Y=mar_vista_point[0]
)

washout_node = ox.distance.nearest_nodes(
    G,
    X=washout_point[1],
    Y=washout_point[0]
)

mtbache_highland_node = ox.distance.nearest_nodes(
    G,
    X=mtbache_highland_point[1],
    Y=mtbache_highland_point[0]
)

# Find shortest drivable path
route = nx.shortest_path(
    G,
    mar_node,
    mtbache_highland_point,
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