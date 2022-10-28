mkdir -p "$PWD/data/city/net/edge/test/xml"
"$PWD"/sumo_tools/edgesInDistricts.py -n "$PWD/net_config/city.net.xml" -t "$PWD/data/city/net/taz/boundary/test/xml/city_test_taz_poly.poi.xml" -o "$PWD/data/city/net/edge/test/xml/city_test_edges_districts.poi.xml" --add-param True
python3 city_test_setup_files.py
python3 net_parser.py -i ./src/setup/config/city_test_net_parser.json -c city -n ./net_config/city.net.xml
python3 mobility_generator.py -b 0 -e 2000 -n ./net_config/city.net.xml