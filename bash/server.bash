PORT_NUMBER=5000
lsof -i tcp:${PORT_NUMBER} | awk 'NR!=1 {print $2}' | xargs kill
python3 -m server.server.py
