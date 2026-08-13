import ee
import urllib.request
from io import BytesIO
from PIL import Image
ee.Authenticate()

ee.Initialize(project='biosphereai')

def build_hls_landcover_comparison(center_lon=-76.05, center_lat=42.10, years=(2015, 2020, 2026), tile_size_miles=5.0):
    # Returns metadata specs for the comparison years. All now use HLSS30 (Sentinel-2)
    specs = []
    for year in years:
        dataset = "NASA/HLS/HLSS30/v002"  # Changed to HLSS30 for all years
        specs.append({
            "year": year,
            "dataset": dataset
        })
    return specs

def fetch_hls_comparison_images(center_lon=-76.05, center_lat=42.10, years=(2015, 2020, 2026), tile_size_miles=5.0):
    image_records = []
    
    # Approx: 1 mile is ~0.0145 degrees
    half_size = (tile_size_miles / 2.0) * 0.0145
    geom = ee.Geometry.Rectangle([
        center_lon - half_size,
        center_lat - half_size,
        center_lon + half_size,
        center_lat + half_size
    ])
    
    for target_year in years:
        year = target_year
        col = None
        count = 0
        
        # Self-healing loop: if current/future years have no data yet (e.g. 2026 lag), 
        # try the previous year until we find valid data.
        while count == 0 and year >= 2015:  # Sentinel-2 data starts in 2015
            print(f"[HLS] Fetching {year} from NASA/HLS/..." )
            
            # Use Sentinel-2 HLS (HLSS30) for all years
            collection_name = "NASA/HLS/HLSS30/v002"
            
            if year == 2015:
                # Search the entire year of 2015 since Sentinel-2 launched in mid-2015
                start_date = "2015-01-23"  # Sentinel-2A launch date
                end_date = "2016-12-31"
            else:
                # Standard spring window for other years
                start_date = f"{year}-04-01"
                end_date = f"{year}-05-31"
                
            try:
                col = ee.ImageCollection(collection_name) \
                    .filterBounds(geom) \
                    .filterDate(start_date, end_date)
                count = col.size().getInfo()
                
                # If 0 images found (except for 2015 which is already a full range), widen search to the ENTIRE year
                if count == 0 and year != 2015:
                    print(f"[HLS] 0 images in spring {year}. Widening search to entire year...")
                    start_date = f"{year}-01-01"
                    end_date = f"{year}-12-31"
                    col = ee.ImageCollection(collection_name) \
                        .filterBounds(geom) \
                        .filterDate(start_date, end_date)
                    count = col.size().getInfo()
                
                print(f"[HLS] Found {count} images for {year}")
                
            except Exception as e:
                print(f"[HLS ERROR] Failed to query {year}: {e}")
                count = 0
                
            # If still 0 images, roll back to the previous year and try again (primarily for 2026/future years)
            if count == 0:
                print(f"[HLS Warning] No data found for {year}. Rolling back search year...")
                year -= 1
                
        # Process the image once a valid year with images is found
        if count > 0 and col is not None:
            try:
                # Composite the collection and clip to our region
                image = col.median().clip(geom)
                
                print(f"[HLS] Getting thumbnail URL for {year}...")
                
                vis_params = {
                    'bands': ['B4', 'B3', 'B2'],
                    'min': 0,
                    'max': 0.3
                }
                
                thumb_params = {
                    'dimensions': 512,
                    'region': geom
                }
                
                thumb_url = image.visualize(**vis_params).getThumbURL(thumb_params)
                
                # Download and convert to PIL Image
                response = urllib.request.urlopen(thumb_url)
                img_data = response.read()
                pil_img = Image.open(BytesIO(img_data))
                
                # Save under the originally requested target year slot so the UI maps it correctly
                image_records.append({
                    "year": target_year,
                    "actual_year_used": year,
                    "image": pil_img
                })
                
            except Exception as e:
                print(f"[HLS ERROR] Failed to process image for {year}: {e}")
                
    return image_records
