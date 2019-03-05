from environmental_raster_glc import PatchExtractor

extractor = PatchExtractor('/Users/ykarmim/Documents/Cours/Master/Projet_DAC/geoLifeClef/data/rasters_GLC19', size=64, verbose=True)

extractor.append('chbio_1')

# extractor.add_all()

print(extractor[43.61, 3.88].shape)
