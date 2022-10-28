#!/usr/bin/env sh

mkdir -p "$PWD/data/sf/net/taz/boundary/sfcta/xml"
mkdir -p "$PWD/data/sf/net/taz/boundary/stanford/xml"
mkdir -p "$PWD/data/sf/net/taz/boundary/uber/xml"

echo "Processing polyconvert - sfcta"
"$PWD"/sumo_tools/polyconvert --shapefile-prefixes "$PWD/data/sf/net/taz/boundary/sfcta/shape/sf_sfcta_taz_boundary" -o "$PWD/data/sf/net/taz/boundary/sfcta/xml/sf_sfcta_taz_poly.poi.xml" --shapefile.traditional-axis-mapping True --shapefile.add-param True --shapefile.id-column TAZ --net-file "$PWD/net_config/san-francisco.net.xml"
echo "Processing polyconvert - stanford"
"$PWD"/sumo_tools/polyconvert --shapefile-prefixes "$PWD/data/sf/net/taz/boundary/stanford/shape/sf_stanford_taz_boundary" -o "$PWD/data/sf/net/taz/boundary/stanford/xml/sf_stanford_taz_poly.poi.xml" --shapefile.traditional-axis-mapping True --shapefile.add-param True --shapefile.id-column ZIP --net-file "$PWD/net_config/san-francisco.net.xml"
echo "Processing polyconvert - uber"
"$PWD"/sumo_tools/polyconvert --shapefile-prefixes "$PWD/data/sf/net/taz/boundary/uber/shape/sf_uber_taz_boundary" -o "$PWD/data/sf/net/taz/boundary/uber/xml/sf_uber_taz_poly.poi.xml" --shapefile.traditional-axis-mapping True --shapefile.add-param True --shapefile.id-column TAZ --net-file "$PWD/net_config/san-francisco.net.xml"

mkdir -p "$PWD/data/sf/net/edge/sfcta/xml"
mkdir -p "$PWD/data/sf/net/edge/stanford/xml"
mkdir -p "$PWD/data/sf/net/edge/uber/xml"

echo "Processing districts edge - sfcta"
"$PWD"/sumo_tools/edgesInDistricts.py -n "$PWD/net_config/san-francisco.net.xml" -t "$PWD/data/sf/net/taz/boundary/sfcta/xml/sf_sfcta_taz_poly.poi.xml" -o "$PWD/data/sf/net/edge/sfcta/xml/sf_sfcta_edges_districts.poi.xml"
echo "Processing districts edge - stanford"
"$PWD"/sumo_tools/edgesInDistricts.py -n "$PWD/net_config/san-francisco.net.xml" -t "$PWD/data/sf/net/taz/boundary/stanford/xml/sf_stanford_taz_poly.poi.xml" -o "$PWD/data/sf/net/edge/stanford/xml/sf_stanford_edges_districts.poi.xml"
echo "Processing districts edge - uber"
"$PWD"/sumo_tools/edgesInDistricts.py -n "$PWD/net_config/san-francisco.net.xml" -t "$PWD/data/sf/net/taz/boundary/uber/xml/sf_uber_taz_poly.poi.xml" -o "$PWD/data/sf/net/edge/uber/xml/sf_uber_edges_districts.poi.xml"
