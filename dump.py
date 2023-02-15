"""import json
To create the swagger config
"""
import json
from hospital_AC_API import api, app


app.config["SERVER_NAME"] = "localhost"
app.app_context().__enter__()
data = json.dumps(api.__schema__, indent=2)

with open("data.json", "w") as jsonfile:
    json.dump(json.loads(data), jsonfile)
