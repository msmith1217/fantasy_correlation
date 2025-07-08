import requests
import os

def download_nfl_team_logos(output_directory="images"):
    """
    Downloads NFL team logos (SVG format) from Rotowire and saves them
    to the specified output directory.

    Args:
        output_directory (str): The directory where SVG files will be saved.
                                Defaults to "images".
    """
    base_url = "https://content.rotowire.com/images/teamlogo/football/"
    # List of NFL team abbreviations
    # This list covers all 32 NFL teams as of the current season.
    team_abbreviations = [
        "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE",
        "DAL", "DEN", "DET", "GB", "GNB", # GNB is sometimes used for Green Bay, including both for robustness
        "HOU", "IND", "JAX", "KC", "LAC", "LV", "LA", "MIA",
        "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SF",
        "SEA", "TB", "TEN", "WAS"
    ]

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory: {output_directory}")

    print("Starting download of NFL team logos...")

    for team_abbr in team_abbreviations:
        # Construct the URL for the SVG, including the version parameter if needed
        # The 'v=11' is often a cache-busting parameter, keep it if it's part of the required URL
        svg_url = f"{base_url}{team_abbr}.svg?v=11"
        file_name = f"{team_abbr}.svg"
        file_path = os.path.join(output_directory, file_name)

        try:
            # Send a GET request to the URL. Use stream=True for efficient downloading of binary data.
            response = requests.get(svg_url, stream=True)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Open the file in binary write mode ('wb')
                with open(file_path, 'wb') as f:
                    # Iterate over the response content in chunks to save memory for large files
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Successfully downloaded {file_name}")
            else:
                print(f"Failed to download {file_name}. Status code: {response.status_code}")
                print(f"URL attempted: {svg_url}")

        except requests.exceptions.RequestException as e:
            # Catch any request-related errors (e.g., network issues, invalid URL)
            print(f"An error occurred while downloading {file_name}: {e}")
            print(f"URL attempted: {svg_url}")
        except IOError as e:
            # Catch any file writing errors
            print(f"An error occurred while writing {file_name} to disk: {e}")

    print("\nDownload process completed.")

# Call the function to start the download
if __name__ == "__main__":
    download_nfl_team_logos(os.getcwd())
