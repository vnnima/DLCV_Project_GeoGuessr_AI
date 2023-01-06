import pandas as pd

def decimal_to_geohash(decimal):
    """Convert a decimal geohash to a base32 geohash

    Args:
        decimal (int): Decimal geohash

    Returns:
        str: Base32 geohash
    """
    base32_digits = '0123456789bcdefghjkmnpqrstuvwxyz';
    base32 = ""
    while decimal > 0:
        base32 = base32_digits[decimal % 32] + base32
        decimal //= 32
    return base32

def create_geocode_mapping(path):
    """Create a dictionary with the geo_code as key and the geohash (decimal) as value
    Args:
        path (str): Path to the csv file with the coordinates

    Returns:
        dict: Dictionary with the geo_code as key and the geohash (decimal) as value
    """

    df = pd.read_csv(path)
    df_geo = df[["geohash_decimal", "geo_code"]]
    df_geo = df_geo.drop_duplicates()
    geo_code_to_geohash = dict(zip(df_geo["geo_code"], df_geo["geohash_decimal"]))
    return geo_code_to_geohash