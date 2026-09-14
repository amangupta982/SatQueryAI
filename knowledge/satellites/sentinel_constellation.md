# European Space Agency (ESA) Copernicus Sentinel Constellation

## What is the difference between Sentinel-1 and Sentinel-2?

Sentinel-1 and Sentinel-2 are complementary Earth observation satellite missions under the European Copernicus programme, each employing completely different sensing physics:

### Sentinel-1 (Microwave C-Band SAR)
- **Sensor Type**: Active C-band Synthetic Aperture Radar (5.405 GHz, ~5.6 cm wavelength).
- **Day/Night Capability**: Operates 24/7, day and night.
- **Cloud Penetration**: Immune to clouds, rain, fog, and smoke.
- **Primary Data**: Surface roughness, dielectric permittivity (soil/vegetation moisture), structural geometry, and double-bounce urban structures.
- **Key Swath Modes**: Interferometric Wide Swath (IW, 250 km swath width, 5x20 m spatial resolution, dual polarization VV+VH).
- **Key Applications**: Flood extent mapping, maritime vessel tracking, ground displacement interferometry (InSAR), ice sheet monitoring.

### Sentinel-2 (Multispectral Optical MSI)
- **Sensor Type**: Passive MultiSpectral Instrument (MSI) measuring reflected sunlight across 13 spectral bands from visible to shortwave infrared (443 nm to 2190 nm).
- **Day/Night Capability**: Daylight only.
- **Cloud Penetration**: Vulnerable to clouds, cirrus, cloud shadows, and aerosol scattering.
- **Primary Data**: Biochemical reflectance properties (chlorophyll absorption, water absorption, lignin/cellulose), true-color visualization.
- **Bands and Resolutions**:
  - 10-meter: Band 2 (Blue), Band 3 (Green), Band 4 (Red), Band 8 (Near-Infrared / NIR).
  - 20-meter: Red Edge (Bands 5, 6, 7, 8a), Shortwave Infrared (Bands 11, 12).
  - 60-meter: Coastal aerosol (B1), Water vapour (B9), Cirrus cloud detection (B10).
- **Key Applications**: Crop type classification, vegetation health monitoring (NDVI), water quality, land cover mapping.

### Why Combine Sentinel-1 and Sentinel-2?
Combining optical and SAR data fuses chemical and spectral absorption information (Sentinel-2) with structural roughness and soil moisture dynamics (Sentinel-1). In cloudy seasons, SAR maintains uninterrupted time-series tracking; in cloud-free conditions, cross-attention fusion resolves ambiguities between wet bare soil and sparse crops.
