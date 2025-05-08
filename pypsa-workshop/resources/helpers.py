# Helper functions


def create_geometries(network):
    """
    Create GeoDataFrames for different network components with specified coordinate reference system (CRS).

    Parameters
    ----------
        network (PyPSA Network): The network object containing buses, lines, links, converters, and transformers data.
        is_converter (bool): Boolean that specifies if link element is a converter.
        crs (str, optional): Coordinate reference system to be used for the GeoDataFrames. Defaults to GEO_CRS.

    Returns
    -------
    tuple: A tuple containing the following GeoDataFrames:
        - buses (GeoDataFrame): GeoDataFrame containing bus data with geometries.
        - lines (GeoDataFrame): GeoDataFrame containing line data with geometries.
        - links (GeoDataFrame): GeoDataFrame containing link data with geometries.
        - converters (GeoDataFrame): GeoDataFrame containing converter data with geometries.
        - transformers (GeoDataFrame): GeoDataFrame containing transformer data with geometries.
    """
    import geopandas as gpd
    from shapely.wkt import loads

    crs=network.crs

    network.buses["dc"] = network.buses["carrier"].map({"DC": "t", "AC": "f"})
    buses = network.buses.reset_index()[
        [
            "Bus",
            "v_nom",
            "dc",
            "symbol",
            "under_construction",
            "tags",
            "geometry",
        ]
    ]
    buses["geometry"] = buses.geometry.apply(lambda x: loads(x))
    buses = gpd.GeoDataFrame(buses, geometry="geometry", crs=crs)

    lines = network.lines.reset_index()[
        [
            "Line",
            "bus0",
            "bus1",
            "v_nom",
            "i_nom",
            "num_parallel",
            "s_nom",
            "r",
            "x",
            "b",
            "length",
            "underground",
            "under_construction",
            "type",
            "tags",
            "geometry",
        ]
    ]
    # Create shapely linestring from geometry column
    lines["geometry"] = lines.geometry.apply(lambda x: loads(x))
    lines = gpd.GeoDataFrame(lines, geometry="geometry", crs=crs)

    is_converter = network.links.index.str.startswith("conv") == True
    links = (
        network.links[~is_converter]
        .reset_index()
        .rename(columns={"voltage": "v_nom"})[
            [
                "Link",
                "bus0",
                "bus1",
                "v_nom",
                "p_nom",
                "length",
                "underground",
                "under_construction",
                "tags",
                "geometry",
            ]
        ]
    )
    links["geometry"] = links.geometry.apply(lambda x: loads(x))
    links = gpd.GeoDataFrame(links, geometry="geometry", crs=crs)

    converters = (
        network.links[is_converter]
        .reset_index()
        .rename(columns={"voltage": "v_nom"})[
            [
                "Link",
                "bus0",
                "bus1",
                "v_nom",
                "p_nom",
                "geometry",
            ]
        ]
    )
    converters["geometry"] = converters.geometry.apply(lambda x: loads(x))
    converters = gpd.GeoDataFrame(converters, geometry="geometry", crs=crs)

    transformers = network.transformers.reset_index()[
        [
            "Transformer",
            "bus0",
            "bus1",
            "voltage_bus0",
            "voltage_bus1",
            "s_nom",
            "geometry",
        ]
    ]
    transformers["geometry"] = transformers.geometry.apply(lambda x: loads(x))
    transformers = gpd.GeoDataFrame(transformers, geometry="geometry", crs=crs)

    return buses, lines, links, converters, transformers