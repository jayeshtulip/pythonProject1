import re

volume_id = "vol-06c830462b4a4c1fad1aecb4d0579e38"

# Use regular expressions to match and replace the desired format
formatted_volume_id = re.sub(r'vol-([a-f0-9]{8})([a-f0-9]{4})([a-f0-9]{4})([a-f0-9]{4})([a-f0-9]{12})', r'\1-\2-\3-\4-\5', volume_id)

print(formatted_volume_id)
