import matplotlib.colors as mcolors


ice_zones = ["Beau", "Chuk"]
ice_zones_full = ["Beaufort", "Chukchi"]

ice_years = [
    "1996-97",
    "1997-98",
    "1998-99",
    "1999-00",
    "2000-01",
    "2001-02",
    "2002-03",
    "2003-04",
    "2004-05",
    "2005-06",
    "2006-07",
    "2007-08",
    "2008-09",
    "2009-10",
    "2010-11",
    "2011-12",
    "2012-13",
    "2013-14",
    "2014-15",
    "2015-16",
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
]

ice_eras = ["1996-2005", "2005-2014", "2014-2023"]

# File names have different prefixes depending on where the data came from:
# r,e - From M2014 dataset derived from RadarSAT (r) and EnviSAT (e) (1996-2008)
# c - Averaged between ASIP and NIC (2008-2017, 2019-2022)
# a - ASIP data exclusively (2017-2019, 2022-2023)
data_sources = {
    "r": "RadarSAT",
    "e": "EnviSAT",
    "c": "ASIP and NIC Average",
    "a": "ASIP",
}

pixel_values = {
    0: "Not Landfast Ice",
    32: "Coast Vector Shadow",
    64: "Out of Bounds",
    111: "No Data",
    128: "Land",
    255: "Landfast Ice",
}

mmm_pixel_values = {
    0: "Ocean",
    1: "Maximum Landfast Ice Extent",
    2: "Median Landfast Ice Extent",
    3: "Minimum Landfast Ice Extent",
    4: "Mean Landfast Ice Edge",
    5: "Land",
    6: "Out of Domain",
    7: "Coast Vector Shadow",
}

# For daily SLIE data plots
daily_slie_colors = {
    0: [255, 255, 255],  # Not Landfast Ice (white)
    32: [191, 212, 212],  # Coast Vector Shadow (gray-green)
    64: [230, 230, 230],  # Out of Bounds (light gray)
    111: [128, 128, 128],  # No Data (gray)
    128: [204, 230, 204],  # Land (pale green)
    255: [0, 0, 255],  # Landfast Ice (blue)
}
daily_slie_colors_normalized = {
    k: (r / 255, g / 255, b / 255) for k, (r, g, b) in daily_slie_colors.items()
}
daily_slie_cmap = mcolors.ListedColormap(
    [daily_slie_colors_normalized[k] for k in pixel_values.keys()]
)
daily_slie_boundaries = list(pixel_values.keys()) + [max(pixel_values.keys()) + 1]
daily_slie_norm = mcolors.BoundaryNorm(
    daily_slie_boundaries, daily_slie_cmap.N, clip=True
)

# for MMM data, as provided by Andy Mahoney
colors = [
    [255, 255, 255],  # 0: non-fast ice or ocean (white)
    [204, 204, 255],  # 1: maximum fast ice extent (light blue)
    [102, 102, 255],  # 2: median fast ice extent (mid-blue)
    [0, 0, 255],  # 3: minimum fast ice extent (dark blue)
    [0, 0, 0],  # 4: mean fast ice edge (black)
    [204, 230, 204],  # 5: land (pale green)
    [230, 230, 230],  # 6: out of domain (light gray)
    [191, 212, 212],  # 7: shadow zone (gray-green)
]
# Normalize the RGB values to the range [0, 1] as required by Matplotlib
colors_normalized = [(r / 255, g / 255, b / 255) for r, g, b in colors]
mmm_cmap = mcolors.ListedColormap(colors_normalized)
