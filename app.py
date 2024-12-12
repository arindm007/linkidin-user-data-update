from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
from bson.objectid import ObjectId
import json
import os
import urllib.parse

app = Flask(__name__)

# MongoDB Connection
client = MongoClient('mongodb+srv://soumyamittal:soumya@cluster0.ksmhs.mongodb.net/')  # Replace with your MongoDB URI
db = client['test']  # Replace with your database name
collection = db['users']  # Replace with your collection name

# LinkedIn API Configuration
api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
api_key = '0cZRLLBM_tum5f_xRaUXPA'  # Replace with your actual API key
headers = {'Authorization': 'Bearer ' + api_key}

# Function to fetch user details from LinkedIn

def fetch_linkedin_details(social_link):
    if not social_link:
        return None

    # # Clean the URL: remove any leading/trailing spaces
    # social_link = social_link.strip()

    # # Only clean if the string contains 'linkedin :' (case insensitive check)
    # if 'linkedin :' in social_link.lower():
    #     social_link = social_link.split('linkedin :')[1].strip()  # Clean unwanted prefix

    # # Ensure the URL is properly encoded
    # social_link = social_link['linkedIN']
    str = social_link
    start = str.find("https")
    url = str[start:]
  
    

    try:
        response = requests.get(api_endpoint,
                                params={'url': url, 'skills': 'include'},
                                headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

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

# API Endpoint
@app.route('/fetch-details', methods=['GET'])
def fetch_details():
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        object_id = ObjectId(user_id)
    except Exception as e:
        return jsonify({"error": "Invalid ObjectId"}), 400

    # Query MongoDB for the user
    user = collection.find_one({"_id": object_id}, {"_id": 1, "socialMediaLinks": 1})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Extract LinkedIn URL(s) from the socialMediaLinks list
    social_media_links = user.get('socialMediaLinks', [])
    linkedin_urls = []

    for link in social_media_links:
        # Check if link is a dictionary or a string
        if isinstance(link, str) and 'linkedin' in link:
            linkedin_urls.append(link)
        elif isinstance(link, dict) and 'linkedin' in link:
            linkedin_urls.append(link['linkedin'])

    if not linkedin_urls:
        return jsonify({"error": "LinkedIn URL not found"}), 404

    # Now you have a list of LinkedIn URLs
    print("LinkedIn URLs found:", linkedin_urls[0])

    # Fetch LinkedIn profile details for the first LinkedIn URL found
    profile_data = fetch_linkedin_details(linkedin_urls[0])

    if not profile_data:
        return jsonify({"error": "Failed to fetch LinkedIn details"}), 500

    # Transform the profile data
    structured_data = transform_profile_data(profile_data)

    # Prepare the data to be updated in MongoDB
    update_data = {
        "experience": structured_data.get("work_experience", []),
        "education": structured_data.get("education", []),
        "skills": structured_data.get("skills", []),
        "certificationsAndLicenses": structured_data.get("certifications", [])
    }

    # Update MongoDB document with the new fields
    result = collection.update_one(
        {"_id": object_id}, 
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "User not found for update"}), 404


    # Save to JSON file
    with open('linkedin_data.json', 'w') as json_file:
        json.dump(structured_data, json_file, indent=4)

    return jsonify({"message": "Data saved to linkedin_data.json", "data": structured_data})

if __name__ == '__main__':
    app.run(debug=True)
