export $(grep -v '^#' .env | xargs)
mkdir -p "$PWD/data/city/net/edge/test/xml"
"$SUMO_HOME"/tools/edgesInDistricts.py -n "$PWD/net_config/city.net.xml" -t "$PWD/data/city/net/taz/boundary/test/xml/city_test_taz_poly.poi.xml" -o "$PWD/data/city/net/edge/test/xml/city_test_edges_districts.poi.xml" --add-param True
python3 net_parser.py -i ./src/setup/config/city_test_net_parser.json -c city -n ./net_config/city.net.xml
python3 city_test_setup_files.py
python3 scenario_generator.py
python3 mobility_generator.py -b $BEGIN -e $END -n ./net_config/city.net.xml
mkdir -p "$PWD/data/city/mobility/sim/xml"
"$SUMO_HOME"/bin/duarouter -n ./net_config/city.net.xml -r ./data/city/mobility/test/xml/city_test_mobility.xml --ignore-errors=True --repair=True -o ./data/city/mobility/sim/xml/mobility_simulator.rou.xml
python3 runner.py --nogui