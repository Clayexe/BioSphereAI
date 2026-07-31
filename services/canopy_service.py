from analytics.canopy import sample_canopy_cover, calculate_throughfall


class CanopyService:
    def sample(self, lat, lon, precipitation_probability=0):
        canopy_cover = sample_canopy_cover(lat, lon)
        return calculate_throughfall(canopy_cover, precipitation_probability)
