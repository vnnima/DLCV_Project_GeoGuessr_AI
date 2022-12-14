import pygeohash as geohash
# Define a list of coordinates
def geohashs(coords, precision):
    """generates geohashes and assigns every coordinate to a centroid. Then computes the centroids of the geohashes and returns
        Dictionary with input coordinates as keys and geohash centroids as outputs"""
    # Create a dictionary to store the geohashes
    labels = {}

    # Iterate over the coordinates
    for coord in coords:
        # Create a geohash for the coordinate
        gh = geohash.encode(coord[0], coord[1], precision=precision)
        centroid = geohash.decode(gh)
        # Store the coordinate and the centroid of it´s geohash in the dictionary
        labels[coord] = centroid

    # Return the geohashes
    return labels

