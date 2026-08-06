from analytics.canopy import sample_canopy_cover, calculate_throughfall


class CanopyService:
    def __init__(self, canopy_raster_path=None):
        self.canopy_raster_path = canopy_raster_path

    def sample(self, lat, lon, precipitation_probability=0):
        canopy_cover = sample_canopy_cover(lat, lon, self.canopy_raster_path)
        return calculate_throughfall(canopy_cover, precipitation_probability)
