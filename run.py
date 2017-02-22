import sys
import api

host, port = [s.strip() for s in sys.argv[1].split(":")]
api.app.run(host=host, port=int(port))
