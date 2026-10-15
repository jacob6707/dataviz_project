import os

import pandas as pd
import requests

base_url = "https://www.vgchartz.com"

def download_boxart_images(df: pd.DataFrame, output_folder: str, limit: int = 10):
    """
    Download box art images for the first `limit` game titles in the DataFrame.

    Parameters:
    - df: DataFrame containing game data with an 'img' column for image slugs.
    - output_folder: Folder to save downloaded images.
    - limit: Number of images to download (default is 10).
    """
    # Create a folder to save box art images
    os.makedirs(output_folder, exist_ok=True)

    # Loop over the dataset
    for index, row in df.head(limit).iterrows():
        slug = row['img']  # e.g., "/games/boxart/full_6510540AmericaFrontccc.jpg"
        if pd.isna(slug) or slug.strip() == "":
            continue  # skip missing URLs
        
        url = construct_boxart_url(slug)
        filename = os.path.join(output_folder, os.path.basename(slug))
        
        try:
            # Download the image
            response = requests.get(url)
            response.raise_for_status()  # raise error if download fails
            
            # Save to file
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filename}")
        except requests.HTTPError as e:
            print(f"Failed to download {url}: {e}")

def download_boxart_image(slug: str, output_folder: str):
    """
    Download a single box art image given its slug.

    Parameters:
    - slug: The image slug (e.g., "/games/boxart/full_6510540AmericaFrontccc.jpg").
    - output_folder: Folder to save the downloaded image.
    """
    if pd.isna(slug) or slug.strip() == "":
        print("Invalid slug provided.")
        return
    
    url = construct_boxart_url(slug)
    filename = os.path.join(output_folder, os.path.basename(slug))
    
    try:
        # Download the image
        response = requests.get(url)
        response.raise_for_status()  # raise error if download fails
        
        # Save to file
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {filename}")
    except requests.HTTPError as e:
        print(f"Failed to download {url}: {e}")

def construct_boxart_url(slug: str) -> str:
    """
    Construct the full URL for a box art image given its slug.

    Parameters:
    - slug: The image slug (e.g., "/games/boxart/full_6510540AmericaFrontccc.jpg").

    Returns:
    - Full URL to the box art image.
    """
    if pd.isna(slug) or slug.strip() == "":
        return ""
    
    return base_url + slug