import numpy as np
import osmnx as ox
import geopandas as gpd

# %%

def getRoadAndPathwayNetwork(all_structures,boundaryLoc):
    max_lat_dwell = max(all_structures['lat'].values)
    min_lat_dwell = min(all_structures['lat'].values)
    max_lon_dwell = max(all_structures['lon'].values)
    min_lon_dwell = min(all_structures['lon'].values)
    
    # Add in unique id (starts at 0 to enable index matching)
    all_structures['ID'] = np.arange(len(all_structures))
    
    # Get max and min lats for all data
    north = max_lat_dwell
    south = min_lat_dwell
    east = max_lon_dwell
    west = min_lon_dwell
    
    # Pull Grid from Networkx
    G_all = ox.graph.graph_from_bbox(north, south, east, west, network_type='all', retain_all=True)
    
    # Get Boundary File
    boundary = gpd.read_file(boundaryLoc)
    
    # Project into new coord system
    boundary = boundary.to_crs("EPSG:4326")
    
    # Bondary as polygon object
    boundary_polygon = boundary['geometry'][0]
    
    # Get nodes in gdf type
    nodes = ox.graph_to_gdfs(G_all, edges=False)
    
    # Find intersecting nodes
    intersecting_nodes = list(nodes[nodes.intersects(boundary_polygon)].index)
    
    # Create subgraph
    gSite = G_all.subgraph(intersecting_nodes)
    
    return gSite