# Remote Sensing Spectral Indices and Optical-SAR Fusion

## 1. What is NDVI? (Normalized Difference Vegetation Index)
The Normalized Difference Vegetation Index (NDVI) is a numerical indicator that assesses the presence and vigor of photosynthetic green vegetation.

### Mathematical Formula:
$$\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$$

In Sentinel-2, NIR corresponds to Band 8 (~842 nm) and Red corresponds to Band 4 (~665 nm).

### Biological and Physical Mechanism:
- Healthy vegetation contains chlorophyll pigments that strongly absorb red and blue light for photosynthesis.
- The spongy mesophyll cell structure of healthy green leaves strongly reflects and transmits Near-Infrared (NIR) radiation to prevent cellular overheating.
- Consequently, dense healthy canopies produce high NDVI values (+0.6 to +0.9).
- Stressed or dying vegetation exhibits lower NIR reflectance and higher red reflectance, yielding moderate NDVI values (+0.2 to +0.5).
- Bare soil, sand, and rock reflect red and NIR similarly, producing values near zero (0.0 to +0.15).
- Water absorbs almost all NIR radiation while reflecting green and red, yielding negative NDVI values (-0.5 to -0.1).

## 2. What is NDWI? (Normalized Difference Water Index)
NDWI delineates open water bodies and detects moisture content:
- **McFeeters NDWI (Water Extent)**:
  $$\text{NDWI}_{\text{McFeeters}} = \frac{\text{Green} - \text{NIR}}{\text{Green} + \text{NIR}}$$
  Positive values highlight open water features (lakes, reservoirs, rivers) while suppressing vegetation and soil.
- **Gao NDWI (Vegetation Canopy Water Content)**:
  $$\text{NDWI}_{\text{Gao}} = \frac{\text{NIR} - \text{SWIR}}{\text{NIR} + \text{SWIR}}$$
  Monitors moisture stress in crop canopies and forest foliage.

## 3. Why do we combine optical and SAR imagery?
Combining optical and SAR imagery resolves intrinsic sensing limitations:
1. **Cloud & Weather Penetration**: Optical imagery is often contaminated by clouds, haze, or smoke; SAR microwave pulses penetrate all weather phenomena, enabling continuous monitoring.
2. **Complementary Physics**:
   - Optical sensors capture surface reflectance driven by atomic and molecular chemical composition (chlorophyll, water, minerals).
   - SAR sensors capture structural morphology, surface roughness, double-bounce geometries, and dielectric permittivity (dielectric moisture).
3. **Flood Inundation & Vegetation Disambiguation**: Under dense forest or emergent aquatic plants, optical imagery sees only green leaves; SAR L-band and C-band double bounce reveals standing water beneath the canopy.
4. **Day-and-Night Intelligence**: SAR operates around the clock, providing critical rapid-response data during emergencies regardless of solar illumination.
