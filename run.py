from device_registry import app
import os

PORT = int(os.environ.get("PORT"))

app.run(host='0.0.0.0', port=PORT, debug=True)
