from decouple import config

# Get the adb_path
adb_path = config('ADB_PATH')

# Get the app_name
app_name = config('APP_NAME')