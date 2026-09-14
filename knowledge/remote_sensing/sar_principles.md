# Synthetic Aperture Radar (SAR) Principles

## 1. What is SAR?
Synthetic Aperture Radar (SAR) is an active microwave remote-sensing imaging system. Unlike optical sensors that rely on reflected solar radiation, SAR illuminates the Earth's surface with its own radar pulses (typically in the microwave spectrum: X-band, C-band, or L-band) and records the amplitude and phase of the backscattered signal.

The "synthetic aperture" technique overcomes the physical antenna size limitation: by synthesizing the forward motion of the satellite antenna along its orbital flight path, signal processing algorithms simulate an antenna hundreds of meters long, yielding high spatial resolution irrespective of altitude.

## 2. Why is SAR useful during cloudy conditions and at night?
Because SAR operates in microwave frequencies (wavelengths ranging from ~1 cm in X-band to ~24 cm in L-band), radar waves penetrate clouds, haze, smoke, dust, precipitation, and atmospheric moisture with minimal attenuation. Furthermore, as an active sensor providing its own illumination, SAR operates identically during daytime and nighttime, ensuring uninterrupted observation of monsoons, cloud-covered flood disasters, and polar night regions.

## 3. SAR Backscatter and Polarimetry
Radar backscatter measures the radar cross-section per unit surface area ($\sigma^0$, sigma nought), expressed in decibels (dB):
- **Specular Reflection**: Flat surfaces such as calm water, paved runways, and smooth highways reflect radar pulses away from the receiver, appearing dark (very low backscatter, -20 dB to -28 dB).
- **Diffuse Scattering**: Rough terrain, bare soil, and sparse vegetation scatter radar waves in many directions, appearing medium-bright (-12 dB to -18 dB).
- **Volume Scattering**: Multi-layered forest canopies and dense crops cause multiple internal reflections, depolarizing the signal.
- **Double Bounce (Corner Reflector)**: Right-angle geometries between building walls and paved ground or flooded tree trunks and water create double-bounce reflections, directing high energy back to the antenna and appearing bright (-5 dB to +5 dB).

### Polarimetric Modes:
- **Single-Pol**: HH or VV.
- **Dual-Pol**: VV + VH (typical Sentinel-1 mode over land) or HH + HV (typical RISAT-1 mode).
- **Quad-Pol**: Full polarimetric matrix measuring HH, HV, VH, and VV amplitude and relative phase, enabling Freeman-Durden and Cloude-Pottier target decompositions.
