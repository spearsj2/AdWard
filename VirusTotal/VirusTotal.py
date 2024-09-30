import requests # Used for making API calls
import os # Used to read the .env file storing personal variables
import dotenv # Reads the .env file and loads it into the file
import base64 # Encodes urls to get the analysis ID of the url
import json # Used to transform the API response the parable Python data

# Load .env file
dotenv.load_dotenv()
os.system('cls')
VT_API_KEY = os.getenv('VT_API_KEY')

def func_checkurl(str_UrlToCheck, bool_WriteResponseToFile):
    try:
        # POST request to VirusTotal
        url = "https://www.virustotal.com/api/v3/urls"
        payload = {"url": str_UrlToCheck}
        headers = {
            "accept": "application/json",
            "x-apikey": VT_API_KEY,
            "content-type": "application/x-www-form-urlencoded"
        }

        # Make the POST request
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        # Encodes the given url in base64 to get the url Analysis ID
        str_encoded_url_id = base64.urlsafe_b64encode(str_UrlToCheck.encode()).decode().strip("=")

        # Combines the url analysis ID with a VirusTotal GET request
        url = "https://www.virustotal.com/api/v3/urls/" + str_encoded_url_id
        headers = {
            "accept": "application/json",
            "x-apikey": VT_API_KEY # Environment variable
        }

        # Make the GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        # Converts the response to JSON formatted data
        data = response.json()

        # Gets the last analysis stats from the JSONified response to be used for grading urls
        last_analysis_stats = (
            data
            .get("data", {})
            .get("attributes", {})
            .get("last_analysis_stats")
        )

        if last_analysis_stats is None:
            print(f"No analysis stats found for {str_UrlToCheck}.")
            return
        # Exclude the "timeout" key if it exists
        last_analysis_stats_filtered = {k: v for k, v in last_analysis_stats.items() if k != "timeout"}


        # Print and write the last analysis stats
        # Note: This only prints and writes responses, not errors. Those show in the console
        print(f"{str_UrlToCheck} - {last_analysis_stats_filtered}")
        if bool_WriteResponseToFile == True:
            with open("Virustotal/response.txt", "a") as file:
                file.write(f"{str_UrlToCheck} - {json.dumps(last_analysis_stats_filtered)}\n")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.Timeout:
        print("The request timed out. Please try again later.")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")
    except KeyError as key_err:
        print(f"Key error: {key_err} - The expected structure is missing.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Testing the function
# func_checkurl("https://www.youtube.com", True)