#!/usr/bin/env sh

mkdir -p "$PWD/data/sf/net/taz/boundary/sfcta/xml"
mkdir -p "$PWD/data/sf/net/taz/boundary/stanford/xml"
mkdir -p "$PWD/data/sf/net/taz/boundary/uber/xml"

echo "Processing polyconvert - sfcta"
"$PWD"/sumo_tools/polyconvert --shapefile-prefixes "$PWD/data/sf/net/taz/boundary/sfcta/shape/sf_sfcta_taz_boundary" -o "$PWD/data/sf/net/taz/boundary/sfcta/xml/sf_sfcta_taz_poly.poi.xml" --shapefile.traditional-axis-mapping True --shapefile.add-param True --shapefile.id-column TAZ --net-file "$PWD/net_config/sf.net.xml"
echo "Processing polyconvert - stanford"
"$PWD"/sumo_tools/polyconvert --shapefile-prefixes "$PWD/data/sf/net/taz/boundary/stanford/shape/sf_stanford_taz_boundary" -o "$PWD/data/sf/net/taz/boundary/stanford/xml/sf_stanford_taz_poly.poi.xml" --shapefile.traditional-axis-mapping True --shapefile.add-param True --shapefile.id-column ZIP --net-file "$PWD/net_config/sf.net.xml"
echo "Processing polyconvert - uber"
"$PWD"/sumo_tools/polyconvert --shapefile-prefixes "$PWD/data/sf/net/taz/boundary/uber/shape/sf_uber_taz_boundary" -o "$PWD/data/sf/net/taz/boundary/uber/xml/sf_uber_taz_poly.poi.xml" --shapefile.traditional-axis-mapping True --shapefile.add-param True --shapefile.id-column TAZ --net-file "$PWD/net_config/sf.net.xml"

mkdir -p "$PWD/data/sf/net/edge/sfcta/xml"
mkdir -p "$PWD/data/sf/net/edge/stanford/xml"
mkdir -p "$PWD/data/sf/net/edge/uber/xml"

echo "Processing districts edge - sfcta"
"$PWD"/sumo_tools/edgesInDistricts.py -n "$PWD/net_config/sf.net.xml" -t "$PWD/data/sf/net/taz/boundary/sfcta/xml/sf_sfcta_taz_poly.poi.xml" -o "$PWD/data/sf/net/edge/sfcta/xml/sf_sfcta_edges_districts.poi.xml"
echo "Processing districts edge - stanford"
"$PWD"/sumo_tools/edgesInDistricts.py -n "$PWD/net_config/sf.net.xml" -t "$PWD/data/sf/net/taz/boundary/stanford/xml/sf_stanford_taz_poly.poi.xml" -o "$PWD/data/sf/net/edge/stanford/xml/sf_stanford_edges_districts.poi.xml"
echo "Processing districts edge - uber"
"$PWD"/sumo_tools/edgesInDistricts.py -n "$PWD/net_config/sf.net.xml" -t "$PWD/data/sf/net/taz/boundary/uber/xml/sf_uber_taz_poly.poi.xml" -o "$PWD/data/sf/net/edge/uber/xml/sf_uber_edges_districts.poi.xml"

python3 net_parser.py -i ./src/setup/config/sf_net_parser.json -c city -n ./net_config/sf.net.xml
python3 scenario_generator.py
python3 mobility_generator.py -b 0 -e 5000 -n ./net_config/sf.net.xml
mkdir -p "$PWD/data/city/mobility/sim/xml"
./sumo_tools/duarouter -n ./net_config/sf.net.xml -r ./data/sf/mobility/sfcta/xml/sf_sfcta_mobility.xml --ignore-errors=True --repair=True -o ./data/sf/mobility/sim/xml/mobility_simulator.rou.xml