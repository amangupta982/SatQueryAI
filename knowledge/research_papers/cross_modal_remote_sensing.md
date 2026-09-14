# Cross-Modal Alignment and Multi-Sensor Fusion in Remote Sensing

## Cross-Attention Mechanisms in Optical-SAR Alignment
Optical and Synthetic Aperture Radar (SAR) sensors register fundamentally disjoint physical phenomena: dielectric microwave backscatter versus solar optical surface reflectance. Direct pixel-level fusion often leads to severe artifacts due to speckle noise and differing geometric distortions (such as layover, foreshortening, and shadow).

### Modern Deep Multi-Sensor Architectures:
1. **Heterogeneous Feature Extraction**: Separate convolutional or vision transformer encoders project optical and SAR rasters into aligned latent feature spaces.
2. **Cross-Attention Fusion**: Query projections from the optical feature map attend to key and value projections from the SAR feature map, dynamically weighting radar texture where optical clarity is degraded by clouds or shadows.
3. **Speckle-Robust Representations**: Multi-look filtering or learned speckle invariance layers in the radar stream prevent multiplicative noise from polluting high-level semantic embeddings.
4. **Bi-Temporal Latent Differencing**: For change detection, cross-temporal attention heads model seasonal phenology versus persistent anthropogenic land-use transitions.
