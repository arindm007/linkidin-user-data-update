import json

# Load data from format.json and scraper.json
with open('format.json', 'r') as f:
    format_data = json.load(f)

with open('scraper.json', 'r') as f:
    scraper_data = json.load(f)

# Update state and city
if 'personal_info' in scraper_data:
    location = scraper_data['personal_info'].get('location', {})
    format_data['state'] = location.get('state', format_data['state'])
    format_data['city'] = location.get('city', format_data['city'])

# Update education
if 'education' in scraper_data:
    format_data['education'] = scraper_data['education']

# Update experience
if 'work_experience' in scraper_data:
    format_data['experience'] = scraper_data['work_experience']

# Update certifications and licenses
if 'certifications' in scraper_data:
    format_data['certificationsAndLicenses'] = scraper_data['certifications']

# Save updated data to a new JSON file
output_path = 'updated_format.json'
with open(output_path, 'w') as f:
    json.dump(format_data, f, indent=4)

print(f"Updated format.json saved to {output_path}")
