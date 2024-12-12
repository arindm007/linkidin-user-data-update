import requests
import json
import os

# Configuration
api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
linkedin_profile_url = 'https://www.linkedin.com/in/aadarshsoni/'
api_key = '_1j568pt0HsKUu5jDAXTBA'  # Fetch the API key from an environment variable
headers = {'Authorization': 'Bearer ' + api_key}

# API Request
try:
    response = requests.get(api_endpoint,
                            params={'url': linkedin_profile_url, 'skills': 'include'},
                            headers=headers)
    response.raise_for_status()  # Raise HTTPError for bad responses
    profile_data = response.json()
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
    profile_data = {}

# Transform Function
def transform_profile_data(data):
    """Transform the API response into a structured format."""
    return {
        "personal_info": {
            "public_identifier": data.get("public_identifier"),
            "full_name": data.get("full_name"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "profile_pic_url": data.get("profile_pic_url"),
            "background_cover_image_url": data.get("background_cover_image_url"),
            "headline": data.get("headline"),
            "summary": data.get("summary"),
            "location": {
                "city": data.get("city"),
                "state": data.get("state"),
                "country": data.get("country_full_name")
            },
            "follower_count": data.get("follower_count"),
            "connections": data.get("connections")
        },
        "work_experience": [
            {
                "title": exp.get("title"),
                "company": exp.get("company"),
                "location": exp.get("location"),
                "starts_at": f"{exp['starts_at']['year']}-{exp['starts_at']['month']:02d}-{exp['starts_at']['day']:02d}" if exp.get("starts_at") else None,
                "ends_at": f"{exp['ends_at']['year']}-{exp['ends_at']['month']:02d}-{exp['ends_at']['day']:02d}" if exp.get("ends_at") else None,
                "description": exp.get("description"),
                "company_linkedin_url": exp.get("company_linkedin_profile_url"),
                "logo_url": exp.get("logo_url")
            } for exp in data.get("experiences", [])
        ],
        "education": [
            {
                "degree": edu.get("degree_name"),
                "field_of_study": edu.get("field_of_study"),
                "school": edu.get("school"),
                "starts_at": f"{edu['starts_at']['year']}-{edu['starts_at']['month']:02d}-{edu['starts_at']['day']:02d}" if edu.get("starts_at") else None,
                "ends_at": f"{edu['ends_at']['year']}-{edu['ends_at']['month']:02d}-{edu['ends_at']['day']:02d}" if edu.get("ends_at") else None,
                "school_linkedin_url": edu.get("school_linkedin_profile_url"),
                "logo_url": edu.get("logo_url")
            } for edu in data.get("education", [])
        ],
        "certifications": [
            {
                "name": cert.get("name"),
                "authority": cert.get("authority"),
                "url": cert.get("url")
            } for cert in data.get("certifications", [])
        ],
        "skills": data.get("skills", []),
        "groups": [
            {
                "name": group.get("name"),
                "url": group.get("url")
            } for group in data.get("groups", [])
        ]
    }

# Transform and Save Data
if profile_data:
    structured_data = transform_profile_data(profile_data)

    # Save to JSON file
    with open('linkedin_data.json', 'w') as json_file:
        json.dump(structured_data, json_file, indent=4)

    print("Data saved to linkedin_data.json")
else:
    print("No profile data available.")
