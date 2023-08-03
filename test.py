import numpy as np
import geopandas as gpd
import libpysal as lp
from esda.moran import Moran

# Sample data (replace this with your spatial dataset)
# Assuming you have a GeoDataFrame with spatial information
data = gpd.GeoDataFrame({'ID': range(5),
                         'geometry': gpd.points_from_xy([2, 5, 1, 9, 3], [3, 8, 2, 7, 6])})

# Create a spatial weights matrix (W) using k-nearest neighbors
W = lp.weights.KNN.from_dataframe(data, k=2)

# Calculate spatial autocorrelation using Moran's I
moran = Moran(data['ID'], W)

print("Spatial Autocorrelation Statistics:")
print("Moran's I:", moran.I)
print("Expected Moran's I:", moran.EI)
print("Z-Score:", moran.z_norm)
print("P-Value:", moran.p_norm)
