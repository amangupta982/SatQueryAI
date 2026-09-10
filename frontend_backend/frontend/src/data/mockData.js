// Centralized mock data for SatQuery AI.
// In production, everything here would come from a FastAPI backend
// exposing endpoints like /api/analyze, /api/history, /api/compare.

export const activeImage = {
  id: 'img_0192',
  filename: 'Bengaluru_Sector_14.tif',
  sizeMb: 24.6,
  width: 4096,
  height: 4096,
  resolution: '0.5 m/px',
  acquisitionDate: '24 Aug 2026',
  satellite: 'Cartosat-3',
  coordinates: '13.0827° N, 77.5946° E',
  thumbnail: '/satellite_scene.jpg',
}

export const datasets = [
  { id: 'ds1', name: 'Cartosat-3 - Urban India' },
  { id: 'ds2', name: 'Sentinel-2 - Land Cover' },
  { id: 'ds3', name: 'ResourceSat-2 - Agriculture' },
  { id: 'ds4', name: 'RISAT-1 - SAR Composite' },
]

export const analysisStats = {
  objectsDetected: 42,
  buildings: 18,
  roads: 12,
  waterBodies: 3,
  vegetationAreas: 9,
  vegetationCoverage: 34,
  urbanCoverage: 41,
  waterCoverage: 8,
  otherCoverage: 17,
  confidence: 92,
}

export const landCoverage = [
  { label: 'Urban Area', value: 41, color: '#2563eb' },
  { label: 'Vegetation', value: 34, color: '#22c55e' },
  { label: 'Water', value: 8, color: '#60a5fa' },
  { label: 'Other', value: 17, color: '#cbd5e1' },
]

export const aiInsights = [
  'Dense urban development detected in the northern region.',
  'Vegetation coverage is higher in the western section.',
  'A water body was detected near the center of the scene.',
  'Multiple road networks connect the primary urban structures.',
  'No major anomalous regions detected in this pass.',
]

export const detectionBoxes = [
  { id: 1, type: 'building', label: 'Building', confidence: 96.2, x: 22, y: 28, w: 9, h: 7 },
  { id: 2, type: 'building', label: 'Building', confidence: 94.8, x: 34, y: 20, w: 7, h: 6 },
  { id: 3, type: 'road', label: 'Road', confidence: 91.0, x: 10, y: 55, w: 30, h: 4 },
  { id: 4, type: 'water', label: 'Water Body', confidence: 97.3, x: 60, y: 60, w: 18, h: 14 },
  { id: 5, type: 'vegetation', label: 'Vegetation', confidence: 89.6, x: 68, y: 22, w: 16, h: 12 },
  { id: 6, type: 'vehicle', label: 'Vehicle', confidence: 91.4, x: 46, y: 46, w: 3, h: 2 },
  { id: 7, type: 'building', label: 'Building', confidence: 93.1, x: 50, y: 32, w: 6, h: 5 },
  { id: 8, type: 'road', label: 'Road', confidence: 88.7, x: 55, y: 66, w: 24, h: 3 },
]

export const detectionLegend = [
  { type: 'building', label: 'Buildings', color: '#e8a94f' },
  { type: 'road', label: 'Roads', color: '#e8637a' },
  { type: 'water', label: 'Water', color: '#5fb7e8' },
  { type: 'vegetation', label: 'Vegetation', color: '#7fd88f' },
]

export const suggestedQueries = [
  { text: 'Detect roads in this area', type: 'road' },
  { text: 'Show vegetation density', type: 'vegetation' },
  { text: 'Find water bodies', type: 'water' },
  { text: 'Compare with another region', type: 'compare' },
]

export const initialChatMessages = [
  {
    id: 'm1',
    role: 'user',
    text: 'Are there any buildings near the river in this area?',
    time: '09:43',
    delivered: true,
  },
  {
    id: 'm2',
    role: 'assistant',
    text: 'Yes. I detected several building structures within ~80 meters of the river on the western side.\n\nI found a total of 6 buildings close to the water body.',
    time: '09:43',
    card: {
      title: 'Buildings Near River',
      stats: [
        { label: 'Detected Buildings', value: '6' },
        { label: 'Avg. Distance', value: '~80 m' },
        { label: 'Confidence', value: '92%' },
      ],
    },
  },
]

// Keyword-driven mock AI response engine.
export function getMockAIResponse(query) {
  const q = query.toLowerCase()

  if (q.includes('building')) {
    return {
      text: 'I identified 18 building structures in this scene, primarily clustered in the northern and central blocks.',
      stats: [
        { label: 'Buildings', value: '18' },
        { label: 'Avg. Confidence', value: '94.1%' },
      ],
      activateLayer: 'buildings',
    }
  }
  if (q.includes('vegetation') || q.includes('green')) {
    return {
      text: 'Vegetation covers approximately 34% of the analyzed region, concentrated in the western section.',
      highlight: { label: 'Vegetation Coverage', value: '34%' },
      activateLayer: 'vegetation',
    }
  }
  if (q.includes('water') || q.includes('river') || q.includes('lake')) {
    return {
      text: 'I detected 3 distinct water bodies in this scene, including one large reservoir near the center.',
      stats: [
        { label: 'Water Bodies', value: '3' },
        { label: 'Coverage', value: '12%' },
      ],
      activateLayer: 'water',
    }
  }
  if (q.includes('road')) {
    return {
      text: 'The road network analysis found 12 distinct road segments connecting the primary urban structures.',
      stats: [
        { label: 'Roads', value: '12' },
        { label: 'Total Length', value: '8.4 km' },
      ],
      activateLayer: 'roads',
    }
  }
  if (q.includes('compare')) {
    return {
      text: 'To compare regions, switch to Compare Images mode and select two scenes — I can run change detection between them.',
      cta: 'compare',
    }
  }
  return {
    text: "I've analyzed the scene across four categories: buildings, roads, water bodies and vegetation. Ask me about any of them, or try one of the suggested queries below.",
  }
}

export const auditMetrics = {
  totalInferences: 326,
  weeklyGrowth: '+24 this wk',
  subtitle1: 'Multi-sensor Earth observation queries',
  successRate: '97.5%',
  ratio: '318 / 326',
  subtitle2: '7 failed · 1 live processing',
  avgLatency: '2.8s',
  p95: 'P95: 4.1s',
  subtitle3: 'Vision-language inference + raster extraction',
  activeConstellations: 5,
  levelBadge: 'Level-2A',
  subtitle4: 'Sentinel-2, Landsat-9, Cartosat, Resourcesat',
}

export const executionLogRecords = [
  {
    id: 'AN-2610',
    date: '09 Sep 2026',
    time: '11:24 IST',
    sensor: 'Sentinel-2 Multispectral',
    sensorType: 'Optical',
    status: 'Completed',
    latency: '6.2 s',
    prompt: 'Find areas where vegetation decreased significantly between 2024 and 2026.',
    resultSummary: 'Vegetation decline in 14 regions - 42.8 km²',
    region: 'Ahmedabad, Gujarat',
    confidence: '87.4%',
    telemetry: {
      sceneId: 'S2B_MSIL2A_20260909T054639_N0511_R033',
      gsd: '10m Ground Sample Distance',
      cloudCover: '4.2%',
      bands: 'B02 (Blue), B03 (Green), B04 (Red), B08 (NIR)',
      inferenceEngine: 'SatQuery-VLM-v2.4-ISRO / TensorRT-LLM',
      gpuCluster: 'NVIDIA H100 SXM5 (Node nrsc-shd-04)',
      latencyBreakdown: {
        tileFetch: '0.84s',
        atmosphericCorrection: '1.12s',
        vlmInference: '2.64s',
        rasterSegmentation: '1.60s',
      },
      tokensUsed: 1420,
    },
  },
  {
    id: 'AN-2609',
    date: '08 Sep 2026',
    time: '18:05 IST',
    sensor: 'RISAT-1A SAR',
    sensorType: 'Synthetic Aperture Radar',
    status: 'Completed',
    latency: '9.8 s',
    prompt: 'Show areas affected by flooding',
    resultSummary: 'Inundation across 115.6 km² of floodplain',
    region: 'Majuli, Assam',
    confidence: '91.2%',
    telemetry: {
      sceneId: 'RS1A_FRS1_20260908T123512_HH_HV',
      gsd: '3.0m Stripmap Mode',
      cloudCover: 'Penetrated (C-Band 5.35 GHz SAR)',
      bands: 'HH + HV Dual Polarimetric Sigma0',
      inferenceEngine: 'SatQuery-FloodNet-SAR-v3',
      gpuCluster: 'NVIDIA A100-80GB (Node nrsc-shd-02)',
      latencyBreakdown: {
        speckleFilter: '1.80s',
        geocoding: '2.10s',
        waterThresholding: '3.40s',
        polygonExtraction: '2.50s',
      },
      tokensUsed: 980,
    },
  },
  {
    id: 'AN-2608',
    date: '08 Sep 2026',
    time: '10:41 IST',
    sensor: 'Landsat 9 OLI-2',
    sensorType: 'Multispectral',
    status: 'Completed',
    latency: '7.4 s',
    prompt: 'Identify changes in vegetation',
    resultSummary: 'Net NDVI decline of 0.11 over command area',
    region: 'Barmer Basin, Rajasthan',
    confidence: '82.9%',
    telemetry: {
      sceneId: 'LC09_L2SP_149042_20260908_02_T1',
      gsd: '15m Panchromatic / 30m Multispectral',
      cloudCover: '1.8%',
      bands: 'Band 4 (Red), Band 5 (NIR), Band 6 (SWIR 1)',
      inferenceEngine: 'SatQuery-BiomassNDVI-v1.8',
      gpuCluster: 'NVIDIA H100 SXM5 (Node nrsc-shd-05)',
      latencyBreakdown: {
        tileFetch: '1.02s',
        ndviCalculation: '1.45s',
        anomalyDetection: '3.20s',
        summaryGeneration: '1.73s',
      },
      tokensUsed: 1150,
    },
  },
  {
    id: 'AN-2607',
    date: '07 Sep 2026',
    time: '16:12 IST',
    sensor: 'Cartosat-3 PAN/MX',
    sensorType: 'High-Resolution Optical',
    status: 'Completed',
    latency: '14.1 s',
    prompt: 'Find newly constructed structures',
    resultSummary: '236 new structures detected in 4 wards',
    region: 'Bengaluru, Karnataka',
    confidence: '88.1%',
    telemetry: {
      sceneId: 'CS3_MX_20260907_BLR_0941',
      gsd: '0.28m PAN / 1.12m Multispectral 4-Band',
      cloudCover: '6.5%',
      bands: 'PAN, B2 (Blue), B3 (Green), B4 (Red)',
      inferenceEngine: 'SatQuery-UrbanFootprint-HR-v4',
      gpuCluster: 'NVIDIA H100 SXM5 (Node nrsc-shd-01)',
      latencyBreakdown: {
        panSharpening: '3.80s',
        buildingSegmentation: '5.60s',
        temporalDiff: '3.20s',
        spatialVerification: '1.50s',
      },
      tokensUsed: 2280,
    },
  },
  {
    id: 'AN-2606',
    date: '06 Sep 2026',
    time: '09:57 IST',
    sensor: 'Sentinel-2 Multispectral',
    sensorType: 'Optical',
    status: 'Completed',
    latency: '11.6 s',
    prompt: 'Compare urban expansion between 2024 and 2026',
    resultSummary: 'Built-up footprint grew 6.8 % (61.3 km²)',
    region: 'Delhi NCR',
    confidence: '90.3%',
    telemetry: {
      sceneId: 'S2A_MSIL2A_20260906T052641_N0511_R105',
      gsd: '10m Ground Sample Distance',
      cloudCover: '8.1%',
      bands: 'B02, B03, B04, B08, B11, B12',
      inferenceEngine: 'SatQuery-ChangeDetection-Temporal-v2',
      gpuCluster: 'NVIDIA H100 SXM5 (Node nrsc-shd-03)',
      latencyBreakdown: {
        dualTileAlignment: '2.40s',
        ndbiMasking: '3.10s',
        vlmVerification: '4.20s',
        vectorization: '1.90s',
      },
      tokensUsed: 1840,
    },
  },
  {
    id: 'AN-2605',
    date: '05 Sep 2026',
    time: '15:30 IST',
    sensor: 'Sentinel-2 Multispectral',
    sensorType: 'Optical',
    status: 'Completed',
    latency: '6.1 s',
    prompt: 'Detect water bodies in this region',
    resultSummary: '72 water bodies delineated - 39.4 km²',
    region: 'Rann of Kutch, Gujarat',
    confidence: '93.5%',
    telemetry: {
      sceneId: 'S2B_MSIL2A_20260905T055629_N0511_R076',
      gsd: '10m GSD',
      cloudCover: '0.4%',
      bands: 'B03 (Green), B08 (NIR), B11 (SWIR)',
      inferenceEngine: 'SatQuery-HydroDelineate-v2',
      gpuCluster: 'NVIDIA H100 SXM5 (Node nrsc-shd-04)',
      latencyBreakdown: {
        mndwiExtraction: '1.10s',
        waterBodyTracing: '2.30s',
        areaComputation: '1.20s',
        reportSynthesis: '1.50s',
      },
      tokensUsed: 890,
    },
  },
  {
    id: 'AN-2604',
    date: '05 Sep 2026',
    time: '08:14 IST',
    sensor: 'Landsat 8 OLI/TIRS',
    sensorType: 'Optical & Thermal',
    status: 'Processing',
    latency: '—',
    prompt: 'Which coastal segments show shoreline retreat?',
    resultSummary: 'Retreat > 8 m on 3 segments',
    region: 'Mumbai Coastal, Maharashtra',
    confidence: '76.8%',
    telemetry: {
      sceneId: 'LC08_L2SP_148047_20260905_02_T1',
      gsd: '30m Multispectral + Thermal',
      cloudCover: '12.3%',
      bands: 'B1-B7 Optical, Band 10 TIRS-1',
      inferenceEngine: 'SatQuery-CoastLineTracking-v1.4',
      gpuCluster: 'NVIDIA H100 SXM5 (Node nrsc-shd-06) [Active Task #88219]',
      latencyBreakdown: {
        tidalNormalization: 'In Progress (54%)',
        shorelineExtraction: 'Queued',
        transectMeasurement: 'Pending',
      },
      tokensUsed: 620,
    },
  },
  {
    id: 'AN-2603',
    date: '04 Sep 2026',
    time: '22:48 IST',
    sensor: 'Cartosat-3 PAN/MX',
    sensorType: 'High-Resolution Optical',
    status: 'Failed',
    latency: '—',
    prompt: 'Identify new roads north of the ring corridor',
    resultSummary: 'Scene rejected — cloud cover 71 %',
    region: 'Ahmedabad, Gujarat',
    confidence: 'N/A',
    telemetry: {
      sceneId: 'CS3_PAN_20260904_AHM_8812',
      gsd: '0.28m Panchromatic',
      cloudCover: '71.2% (Rejection threshold > 25%)',
      bands: 'PAN Channel 1',
      inferenceEngine: 'SatQuery-RoadExtractor-v2.1',
      gpuCluster: 'NVIDIA H100 SXM5 (Node nrsc-shd-02)',
      errorReason: 'Pre-flight QC rejected: scene cloud opacity obscuring target bounding box > 70%. Automatic task terminated.',
      latencyBreakdown: {
        qcCheck: '0.41s',
        cloudMasking: '0.82s',
        abortHandshake: '0.12s',
      },
      tokensUsed: 140,
    },
  },
  {
    id: 'AN-2602',
    date: '03 Sep 2026',
    time: '12:36 IST',
    sensor: 'Sentinel-2 Multispectral',
    sensorType: 'Optical',
    status: 'Completed',
    latency: '8.3 s',
    prompt: 'Find agricultural areas under stress',
    resultSummary: 'Stress signature on 27.9 km² of cropland',
    region: 'Vidarbha, Maharashtra',
    confidence: '84.7%',
    telemetry: {
      sceneId: 'S2A_MSIL2A_20260903T053641_N0511_R062',
      gsd: '10m / 20m RedEdge',
      cloudCover: '3.7%',
      bands: 'B05, B06, B07 (Red Edge), B08A (Narrow NIR)',
      inferenceEngine: 'SatQuery-AgriVigor-v2',
      gpuCluster: 'NVIDIA H100 SXM5 (Node nrsc-shd-04)',
      latencyBreakdown: {
        redEdgeIndexCalc: '1.90s',
        chlorophyllStressDetection: '3.10s',
        clusterGrouping: '1.80s',
        reportGeneration: '1.50s',
      },
      tokensUsed: 1340,
    },
  },
]

export const historyItems = [
  {
    id: 'h1',
    filename: 'Delhi_Region_01.tif',
    date: '28 Aug 2026',
    location: '28.61° N, 77.20° E',
    objects: 42,
    status: 'Completed',
    thumbnail:
      'https://images.unsplash.com/photo-1446776709462-d6b525c57bd3?q=80&w=800&auto=format&fit=crop',
  },
  {
    id: 'h2',
    filename: 'Bengaluru_Sector_14.tif',
    date: '24 Aug 2026',
    location: '13.08° N, 77.59° E',
    objects: 42,
    status: 'Completed',
    thumbnail:
      'https://images.unsplash.com/photo-1451187863213-d1bcbaae3fa3?q=80&w=800&auto=format&fit=crop',
  },
  {
    id: 'h3',
    filename: 'Mumbai_Coastal_Belt.tif',
    date: '19 Aug 2026',
    location: '19.07° N, 72.87° E',
    objects: 67,
    status: 'Completed',
    thumbnail:
      'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?q=80&w=800&auto=format&fit=crop',
  },
  {
    id: 'h4',
    filename: 'Chennai_Industrial_Zone.tif',
    date: '14 Aug 2026',
    location: '13.08° N, 80.27° E',
    objects: 29,
    status: 'Completed',
    thumbnail:
      'https://images.unsplash.com/photo-1502481851512-e9e2529bfbf9?q=80&w=800&auto=format&fit=crop',
  },
  {
    id: 'h5',
    filename: 'Hyderabad_Hitech_City.tif',
    date: '09 Aug 2026',
    location: '17.44° N, 78.38° E',
    objects: 53,
    status: 'Processing',
    thumbnail:
      'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=800&auto=format&fit=crop',
  },
]

export const comparisonResult = {
  newStructures: 18,
  vegetationLoss: 6,
  newRoadSegments: 2,
  imageA: {
    filename: 'Sector_14_2024.tif',
    date: '12 Mar 2024',
    thumbnail:
      'https://images.unsplash.com/photo-1451187863213-d1bcbaae3fa3?q=80&w=1200&auto=format&fit=crop',
  },
  imageB: {
    filename: 'Sector_14_2026.tif',
    date: '24 Aug 2026',
    thumbnail:
      'https://images.unsplash.com/photo-1446776709462-d6b525c57bd3?q=80&w=1200&auto=format&fit=crop',
  },
}

export const detectionTypes = ['Buildings', 'Roads', 'Vehicles', 'Water Bodies', 'Vegetation', 'Custom']

export const userProfile = {
  name: 'A. Sharma',
  role: 'Remote Sensing Analyst',
  team: 'Team Aranya · SIH 2026',
  avatarInitials: 'AS',
}

// ==========================================
// PRESET SAMPLE DATASETS FOR NEW ANALYSIS
// ==========================================
export const samplePresetDatasets = {
  'river-urban-expansion': {
    id: 'river-urban-expansion',
    name: 'River Urban Expansion',
    task: 'Change Analysis',
    defaultQuery: 'What changed in the built-up area near the river between these two images?',
    scenes: [
      {
        id: 'scene-river-2023',
        name: 'Scene 1 (T0)',
        date: 'Jan 15, 2023',
        sensor: 'Sentinel-2 (Optical)',
        modality: 'Optical',
        resolution: '10 m',
        dimensions: '1024 × 1024',
        bands: '4 bands (RGB + NIR)',
        preview: 'https://images.unsplash.com/photo-1502481851512-e9e2529bfbf9?q=80&w=800&auto=format&fit=crop',
      },
      {
        id: 'scene-river-2024',
        name: 'Scene 2 (T1)',
        date: 'Mar 10, 2024',
        sensor: 'Sentinel-2 (Optical)',
        modality: 'Optical',
        resolution: '10 m',
        dimensions: '1024 × 1024',
        bands: '4 bands (RGB + NIR)',
        preview: 'https://images.unsplash.com/photo-1446776709462-d6b525c57bd3?q=80&w=800&auto=format&fit=crop',
      },
    ],
  },
  'river-buildings-grounding': {
    id: 'river-buildings-grounding',
    name: 'River Buildings Grounding',
    task: 'Object Detection',
    defaultQuery: 'Detect and count all building structures and waterfront infrastructure along the riverbank.',
    scenes: [
      {
        id: 'scene-cartosat-blr',
        name: 'Scene 1',
        date: 'Jan 24, 2026',
        sensor: 'Cartosat-3 (Optical)',
        modality: 'Optical',
        resolution: '0.28 m PAN / 1.12 m MX',
        dimensions: '2048 × 2048',
        bands: '4 bands (VNIR)',
        preview: 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=800&auto=format&fit=crop',
      },
    ],
  },
  'flood-sar-inundation': {
    id: 'flood-sar-inundation',
    name: 'Flood SAR Inundation',
    task: 'Optical + SAR',
    defaultQuery: 'Identify water-covered regions and flood extent using optical and synthetic aperture radar backscatter.',
    scenes: [
      {
        id: 'scene-optical-flooding',
        name: 'Scene 1 (Optical)',
        date: 'Sep 06, 2026',
        sensor: 'Sentinel-2 (Optical)',
        modality: 'Optical',
        resolution: '10 m',
        dimensions: '1024 × 1024',
        bands: '12 bands (L2A)',
        preview: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?q=80&w=800&auto=format&fit=crop',
      },
      {
        id: 'scene-sar-flooding',
        name: 'Scene 2 (SAR)',
        date: 'Sep 08, 2026',
        sensor: 'RISAT-1A (C-Band SAR)',
        modality: 'SAR',
        resolution: '3.0 m',
        dimensions: '1024 × 1024',
        bands: 'Dual-Pol (HH + HV)',
        preview: 'https://images.unsplash.com/photo-1451187863213-d1bcbaae3fa3?q=80&w=800&auto=format&fit=crop',
      },
    ],
  },
}

// ==========================================
// RECENT ANALYSES (FOR HOMEPAGE & SETUP)
// ==========================================
export const recentAnalyses = [
  {
    id: 'urban-expansion-2026',
    title: 'Urban Expansion Detection',
    task: 'Change Analysis',
    date: 'Sep 10, 2026',
    sensor: 'Sentinel-2 (Optical)',
    imageCount: 2,
    summary: 'Detected 13.4% increase in built-up area near the river.',
    thumbnail: 'https://images.unsplash.com/photo-1502481851512-e9e2529bfbf9?q=80&w=800&auto=format&fit=crop',
  },
  {
    id: 'buildings-near-river-2026',
    title: 'Buildings Near River',
    task: 'Object Detection',
    date: 'Sep 9, 2026',
    sensor: 'Cartosat-3 (Optical)',
    imageCount: 1,
    summary: 'Detected 24 buildings with 92% confidence.',
    thumbnail: 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=800&auto=format&fit=crop',
  },
  {
    id: 'flooded-area-2026',
    title: 'Flooded Area Analysis',
    task: 'Optical + SAR',
    date: 'Sep 8, 2026',
    sensor: 'Optical + SAR',
    imageCount: 2,
    summary: 'Identified water-covered regions using multimodal analysis.',
    thumbnail: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?q=80&w=800&auto=format&fit=crop',
  },
]

// ==========================================
// COMPREHENSIVE STRUCTURED ANALYSIS RESULTS
// ==========================================
export const structuredAnalysisResults = {
  'urban-expansion-2026': {
    id: 'urban-expansion-2026',
    title: 'Urban Expansion Detection',
    task: 'Change Analysis',
    executionTime: '12.8s',
    timestamp: 'Sep 10, 2026 · 18:42 IST',
    modelName: 'SatQuery-BiTemporal-DiffNet-v2.1',
    query: 'What changed in the built-up area near the river between these two images?',
    beforeImage: {
      label: 'BEFORE',
      date: 'Jan 15, 2023',
      sensor: 'Sentinel-2 L2A',
      url: 'https://images.unsplash.com/photo-1502481851512-e9e2529bfbf9?q=80&w=1200&auto=format&fit=crop',
    },
    afterImage: {
      label: 'AFTER',
      date: 'Mar 10, 2024',
      sensor: 'Sentinel-2 L2A',
      url: 'https://images.unsplash.com/photo-1446776709462-d6b525c57bd3?q=80&w=1200&auto=format&fit=crop',
    },
    changeMap: {
      label: 'CHANGE MAP',
      url: 'https://images.unsplash.com/photo-1446776709462-d6b525c57bd3?q=80&w=1200&auto=format&fit=crop',
    },
    metrics: [
      { label: 'Changed Area', value: '14.2 km²', detail: 'Total land-use transition' },
      { label: 'Change Percentage', value: '+13.4%', detail: 'Net built-up expansion' },
      { label: 'Changed Pixels', value: '1,420,850 px', detail: 'Resolution: 10m GSD' },
      { label: 'Canopy Reduction', value: '-4.8 km²', detail: 'Vegetation displacement' },
    ],
    interpretation:
      'Significant urban expansion is detected along the northern and eastern riparian corridor of the river between January 15, 2023 and March 10, 2024. A total of 14.2 km² (+13.4%) transitioned into built-up infrastructure, characterized by dense residential foundations, industrial warehouse clusters, and newly paved access roads.',
    supportingEvidence: [
      'Normalized Difference Built-up Index (NDBI) shift from 0.12 (vegetated/fallow baseline) to 0.48 across 14 distinct zones.',
      'Surface reflectance in Band 4 (Red) and Band 11 (SWIR) shows characteristic signatures of asphalt and concrete curing.',
      'Loss of riparian buffer zone (-4.8 km²) with high spatial correlation to municipal zoning expansion boundaries.',
    ],
    limitations:
      'Marginal atmospheric haze (AOD = 0.19) on March 10 acquisition was corrected using Sen2Cor Level-2A surface reflectance normalization.',
    confidence: '94.2% (Ensemble Agreement)',
    evidenceArtifacts: [
      { name: 'Change Mask GeoTIFF', type: 'raster', size: '24.2 MB' },
      { name: 'Vector Polygons Shapefile', type: 'vector', size: '3.8 MB' },
      { name: 'Spectral NDVI/NDBI Diff', type: 'matrix', size: '18.5 MB' },
    ],
    executionTrace: {
      requestId: 'REQ-DIFF-20260910-8812',
      pipelineStages: [
        { name: 'Input Radiometric Validation', status: 'Completed', duration: '0.94s' },
        { name: 'Sub-Pixel Co-Registration & Alignment', status: 'Completed', duration: '2.15s' },
        { name: 'Task & Backbone Model Selection', status: 'Completed', duration: '0.32s' },
        { name: 'Bi-Temporal Feature Extraction (Swin-EO)', status: 'Completed', duration: '4.80s' },
        { name: 'Difference Masking & Morphological Cleanup', status: 'Completed', duration: '2.64s' },
        { name: 'Evidence Synthesis & Report Generation', status: 'Completed', duration: '1.95s' },
      ],
      modelCheckpoint: 'SatQuery-BiTemporal-DiffNet-v2.1-Weights-SHA256:7f8a9e',
      gpuNode: 'ISRO-NRSC-SHDN-GPU04 (NVIDIA H100 80GB SXM5)',
      sensorBands: 'Sentinel-2 B02 (Blue), B03 (Green), B04 (Red), B08 (NIR), B11 (SWIR)',
      inputScenes: ['S2B_MSIL2A_20230115T054639_N0500_R033', 'S2A_MSIL2A_20240310T054641_N0511_R033'],
    },
  },

  'buildings-near-river-2026': {
    id: 'buildings-near-river-2026',
    title: 'Buildings Near River',
    task: 'Object Detection',
    executionTime: '7.2s',
    timestamp: 'Sep 09, 2026 · 14:15 IST',
    modelName: 'SatQuery-GroundingDINO-EO-v3',
    query: 'Detect and count all building structures and waterfront infrastructure along the riverbank.',
    mainImage: {
      label: 'HIGH-RESOLUTION OPTICAL SCENE',
      date: 'Jan 24, 2026',
      sensor: 'Cartosat-3 (0.28m PAN / 1.12m MX)',
      url: 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=1200&auto=format&fit=crop',
    },
    objectsDetectedCount: 24,
    categories: [
      { name: 'Commercial Buildings', count: 14, color: '#2563eb' },
      { name: 'Residential Blocks', count: 6, color: '#16a34a' },
      { name: 'Waterfront Jetties', count: 3, color: '#0284c7' },
      { name: 'Bridge Piers', count: 1, color: '#d97706' },
    ],
    detections: [
      { id: 'det-1', label: 'Commercial Complex A', category: 'Commercial Buildings', confidence: '96.8%', bbox: [22, 28, 14, 12], coordinates: '13.0842° N, 77.5921° E' },
      { id: 'det-2', label: 'Commercial Complex B', category: 'Commercial Buildings', confidence: '95.4%', bbox: [40, 22, 12, 10], coordinates: '13.0848° N, 77.5935° E' },
      { id: 'det-3', label: 'Waterfront Cargo Jetty', category: 'Waterfront Jetties', confidence: '94.1%', bbox: [58, 62, 16, 14], coordinates: '13.0815° N, 77.5980° E' },
      { id: 'det-4', label: 'River Crossing Pier', category: 'Bridge Piers', confidence: '93.5%', bbox: [12, 54, 28, 6], coordinates: '13.0820° N, 77.5902° E' },
      { id: 'det-5', label: 'Residential Cluster Alpha', category: 'Residential Blocks', confidence: '91.2%', bbox: [68, 24, 15, 13], coordinates: '13.0860° N, 77.5992° E' },
      { id: 'det-6', label: 'Commercial Warehouse', category: 'Commercial Buildings', confidence: '90.7%', bbox: [48, 44, 9, 8], coordinates: '13.0833° N, 77.5954° E' },
    ],
    interpretation:
      'SatQuery detected 24 high-confidence structural objects within the designated 500-meter riparian observation buffer. Detections include 20 habitable buildings (14 commercial facilities, 6 residential multi-story complexes), 3 reinforced waterfront jetties, and 1 continuous road bridge abutment structure.',
    supportingEvidence: [
      'Edge delineation in 0.28m panchromatic band confirms rectilinear roof perimeters with distinct cast shadow geometry.',
      'Spectral signature in NIR confirms absence of rooftop vegetation over detected industrial spans.',
      'Average object confidence across all 24 bounding boxes is 92.4%.',
    ],
    limitations:
      'Tree canopy overhang along the southwestern embankments partially obscures footprint boundaries for 2 small ancillary sheds.',
    confidence: '92.0% Mean Average Precision (mAP@50)',
    evidenceArtifacts: [
      { name: 'Bounding Boxes GeoJSON', type: 'vector', size: '1.2 MB' },
      { name: 'Cropped Chips Archive', type: 'zip', size: '14.8 MB' },
    ],
    executionTrace: {
      requestId: 'REQ-GROUND-20260909-4419',
      pipelineStages: [
        { name: 'Pan-Sharpening & Radiometric Calibration', status: 'Completed', duration: '1.80s' },
        { name: 'Prompt Text Tokenization & Cross-Attention', status: 'Completed', duration: '0.45s' },
        { name: 'Object Proposal & Feature Pyramid Network', status: 'Completed', duration: '3.10s' },
        { name: 'Non-Maximum Suppression (IoU > 0.45)', status: 'Completed', duration: '0.65s' },
        { name: 'Coordinate Projection to WGS84 / UTM 43N', status: 'Completed', duration: '1.20s' },
      ],
      modelCheckpoint: 'SatQuery-GroundingDINO-Cartosat3-v3.0',
      gpuNode: 'ISRO-NRSC-SHDN-GPU01 (NVIDIA H100 80GB SXM5)',
      sensorBands: 'Cartosat-3 PAN (0.45-0.75 μm) + VNIR (Blue, Green, Red, NIR)',
      inputScenes: ['CS3_PAN_MX_20260124_SEC14_0941'],
    },
  },

  'flooded-area-2026': {
    id: 'flooded-area-2026',
    title: 'Flooded Area Analysis',
    task: 'Optical + SAR',
    executionTime: '15.4s',
    timestamp: 'Sep 08, 2026 · 11:20 IST',
    modelName: 'SatQuery-SAR-FloodNet-Multimodal-v2',
    query: 'Identify water-covered regions and flood extent using optical and synthetic aperture radar backscatter.',
    opticalImage: {
      label: 'OPTICAL (Sentinel-2 L2A)',
      date: 'Sep 06, 2026',
      sensor: 'Sentinel-2 Multispectral',
      cloudCover: '76% Cloud Cover',
      url: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?q=80&w=1200&auto=format&fit=crop',
    },
    sarImage: {
      label: 'SAR (RISAT-1A C-Band)',
      date: 'Sep 08, 2026',
      sensor: 'RISAT-1A SAR (5.35 GHz)',
      cloudCover: 'Penetrated 100%',
      url: 'https://images.unsplash.com/photo-1451187863213-d1bcbaae3fa3?q=80&w=1200&auto=format&fit=crop',
    },
    fusedImage: {
      label: 'FUSED INUNDATION MASK',
      date: 'Multisensor Alignment',
      sensor: 'Optical + C-Band Co-Registered',
      url: 'https://images.unsplash.com/photo-1451187863213-d1bcbaae3fa3?q=80&w=1200&auto=format&fit=crop',
    },
    metrics: [
      { label: 'Total Inundated Area', value: '115.6 km²', detail: 'Active standing floodwaters' },
      { label: 'Baseline Water Body', value: '42.1 km²', detail: 'Pre-monsoon river channel' },
      { label: 'Net Flood Surge', value: '+73.5 km²', detail: 'Submerged cropland and roads' },
      { label: 'Optical Cloud Cover', value: '76.4%', detail: 'Penetrated by SAR radar' },
    ],
    interpretation:
      'Multimodal integration of optical and C-band synthetic aperture radar overcame heavy monsoon cloud occlusion (76.4% obscuration in optical scene). The radar microwave pulses penetrated cloud moisture, exhibiting characteristic specular surface reflection (sigma-0 backscatter < -16.5 dB in HV channel) that cleanly delineated 115.6 km² of floodplain inundation.',
    supportingEvidence: [
      'Radar cross-section shows sharp specular attenuation over calm standing water (-18.2 dB vs -8.4 dB over unflooded soils).',
      'Optical cloud-free windows were used to classify pre-flood land cover baselines (predominantly paddy and alluvium).',
      'Submersion spans 4 major transport corridors and an estimated 62.4 km² of agricultural cropland.',
    ],
    limitations:
      'Wind-induced surface roughness on large open water expanses creates minor backscatter speckle; suppressed using a 5x5 Lee adaptive speckle filter.',
    confidence: '91.8% (Multi-pass Validated)',
    evidenceArtifacts: [
      { name: 'Flood Hazard Geotiff', type: 'raster', size: '32.1 MB' },
      { name: 'Inundation Boundary Shapefile', type: 'vector', size: '4.7 MB' },
    ],
    executionTrace: {
      requestId: 'REQ-SAR-20260908-1120',
      pipelineStages: [
        { name: 'Optical Cloud Masking (SCL / Sen2Cor)', status: 'Completed', duration: '1.20s' },
        { name: 'SAR Range Doppler Terrain Correction (SRTM 30m)', status: 'Completed', duration: '3.40s' },
        { name: 'Speckle Filtering (Lee Filter 5x5)', status: 'Completed', duration: '1.80s' },
        { name: 'Multimodal Spatial Co-Registration', status: 'Completed', duration: '2.90s' },
        { name: 'Thresholding & Active Contour Flood Extraction', status: 'Completed', duration: '4.10s' },
        { name: 'Analytical Report & Metric Synthesis', status: 'Completed', duration: '2.00s' },
      ],
      modelCheckpoint: 'SatQuery-SAR-FloodNet-Multimodal-v2.4',
      gpuNode: 'ISRO-NRSC-SHDN-GPU02 (NVIDIA A100 80GB SXM4)',
      sensorBands: 'Optical (B02, B03, B04, B08) + RISAT-1A SAR (5.35 GHz C-band HH/HV)',
      inputScenes: ['S2B_MSIL2A_20260906T054639', 'RS1A_FRS1_20260908T123512_HH_HV'],
    },
  },

  'vqa-sample': {
    id: 'vqa-sample',
    title: 'Visual Question Answering',
    task: 'Visual Question Answering',
    executionTime: '4.8s',
    timestamp: 'Sep 10, 2026 · 16:30 IST',
    modelName: 'SatQuery-VLM-v2.4-ISRO',
    query: 'What is the primary land use and vegetation condition in the western agricultural sector?',
    mainImage: {
      label: 'SATELLITE OBSERVATION SCENE',
      date: 'Aug 24, 2026',
      sensor: 'Sentinel-2 Multispectral',
      url: 'https://images.unsplash.com/photo-1502481851512-e9e2529bfbf9?q=80&w=1200&auto=format&fit=crop',
    },
    interpretation:
      'The western sector of the analyzed scene is predominantly designated for intensive irrigated agriculture. Spectral analysis reveals active vegetative growth with an average Normalized Difference Vegetation Index (NDVI) of 0.68. A series of linear canal feeders and irrigation ponds are identifiable running parallel to the primary secondary road.',
    supportingEvidence: [
      'NDVI values range from 0.62 to 0.74, indicating healthy green biomass canopy without observable moisture stress.',
      'Spectral absorption in Band 4 (Red) paired with high reflectance in Band 8 (NIR) matches photosynthetic chlorophyll activity.',
      'Field parcel geometries indicate organized multi-crop agrarian plots averaging 1.8 to 2.4 hectares in area.',
    ],
    limitations:
      'Absence of ground truth phenological calendar restricts crop type classification to general broadleaf/cereal category.',
    confidence: 'Confidence not provided by model',
    evidenceArtifacts: [
      { name: 'NDVI Vegetation Surface', type: 'raster', size: '18.2 MB' },
      { name: 'Summary Analysis Report', type: 'pdf', size: '2.4 MB' },
    ],
    executionTrace: {
      requestId: 'REQ-VQA-20260910-1630',
      pipelineStages: [
        { name: 'Natural Language Query Embedding & Entity Grounding', status: 'Completed', duration: '0.62s' },
        { name: 'Multispectral Tile Extraction & Atmospheric Correction', status: 'Completed', duration: '1.14s' },
        { name: 'Vision-Language Cross-Attention Inference', status: 'Completed', duration: '2.10s' },
        { name: 'Scientific Factuality & Grounding Verification', status: 'Completed', duration: '0.94s' },
      ],
      modelCheckpoint: 'SatQuery-VLM-v2.4-ISRO-70B-FP8',
      gpuNode: 'ISRO-NRSC-SHDN-GPU04 (NVIDIA H100 80GB SXM5)',
      sensorBands: 'Sentinel-2 L2A (B02, B03, B04, B08, B8A, B11)',
      inputScenes: ['S2A_MSIL2A_20260824T052641_N0511_R105'],
    },
  },
}

// ==========================================
// EARTH OBSERVATION DATASETS CATALOG
// ==========================================
export const eoDatasetsCatalog = [
  {
    id: 'sentinel-2',
    name: 'Sentinel-2 MSI',
    agency: 'ESA / Copernicus',
    platform: 'Sentinel-2A & Sentinel-2B',
    modality: 'Multispectral Optical',
    resolution: '10 m / 20 m / 60 m GSD',
    revisit: '5 days (at equator)',
    swathWidth: '290 km',
    bands: [
      { band: 'B02', name: 'Blue', center: '490 nm', res: '10 m' },
      { band: 'B03', name: 'Green', center: '560 nm', res: '10 m' },
      { band: 'B04', name: 'Red', center: '665 nm', res: '10 m' },
      { band: 'B08', name: 'Broad NIR', center: '842 nm', res: '10 m' },
      { band: 'B05-B07', name: 'Red Edge', center: '705-783 nm', res: '20 m' },
      { band: 'B11, B12', name: 'SWIR 1 & 2', center: '1610-2190 nm', res: '20 m' },
    ],
    applications: ['Land-use classification', 'Bi-temporal change detection', 'Vegetation health / NDVI', 'Urban sprawl tracking'],
    dataTier: 'Level-2A Bottom-Of-Atmosphere (BOA) Surface Reflectance',
    availability: 'Global Archive (2015 - Present) · Open Access',
  },
  {
    id: 'landsat-9',
    name: 'Landsat 9 OLI-2 / TIRS-2',
    agency: 'USGS / NASA',
    platform: 'Landsat 9',
    modality: 'Multispectral Optical & Thermal Infrared',
    resolution: '15 m PAN / 30 m VNIR-SWIR / 100 m Thermal',
    revisit: '16 days (8 days with Landsat 8)',
    swathWidth: '185 km',
    bands: [
      { band: 'Band 1', name: 'Coastal Aerosol', center: '443 nm', res: '30 m' },
      { band: 'Band 2-4', name: 'Visible RGB', center: '482-654 nm', res: '30 m' },
      { band: 'Band 5', name: 'NIR', center: '865 nm', res: '30 m' },
      { band: 'Band 6, 7', name: 'SWIR 1 & 2', center: '1608-2200 nm', res: '30 m' },
      { band: 'Band 8', name: 'Panchromatic', center: '590 nm', res: '15 m' },
      { band: 'Band 10', name: 'Thermal IR', center: '10.9 μm', res: '100 m' },
    ],
    applications: ['Long-term decadal change analysis', 'Thermal anomaly mapping', 'Water surface temperature', 'Crop cycle monitoring'],
    dataTier: 'Collection 2 Level-2 Surface Reflectance & Temperature',
    availability: 'Global Archive (2021 - Present) · Open Access',
  },
  {
    id: 'cartosat-3',
    name: 'Cartosat-3 PAN & MX',
    agency: 'ISRO (India)',
    platform: 'Cartosat-3 Agile Spacecraft',
    modality: 'Very High-Resolution Optical',
    resolution: '0.28 m Panchromatic / 1.12 m 4-Band MX',
    revisit: 'Adaptive agile retargeting (< 4 days)',
    swathWidth: '17 km (PAN/MX)',
    bands: [
      { band: 'PAN', name: 'Panchromatic', center: '450-750 nm', res: '0.28 m' },
      { band: 'B1', name: 'Blue', center: '450-520 nm', res: '1.12 m' },
      { band: 'B2', name: 'Green', center: '520-590 nm', res: '1.12 m' },
      { band: 'B3', name: 'Red', center: '620-680 nm', res: '1.12 m' },
      { band: 'B4', name: 'NIR', center: '770-860 nm', res: '1.12 m' },
    ],
    applications: ['High-precision urban infrastructure grounding', 'Cadastral mapping', 'Building boundary extraction', 'Disaster impact assessment'],
    dataTier: 'Ortho-Rectified Precision Terrain Corrected',
    availability: 'Regional Archive (ISRO Bhuvan / NRSC Bhoonidhi)',
  },
  {
    id: 'risat-1a',
    name: 'RISAT-1A (EOS-04) SAR',
    agency: 'ISRO (India)',
    platform: 'EOS-04 Spacecraft',
    modality: 'C-Band Synthetic Aperture Radar',
    resolution: '1 m Spotlight / 3-6 m Stripmap / 25 m ScanSAR',
    revisit: '25 days repeat orbit (all-weather day/night)',
    swathWidth: '10 km - 240 km depending on mode',
    bands: [
      { band: 'C-Band', name: '5.35 GHz Radar', center: '5.6 cm wavelength', res: '1-25 m' },
      { band: 'Polarizations', name: 'Single / Dual / Hybrid', center: 'HH, HV, VV, VH', res: 'Mode dep.' },
    ],
    applications: ['All-weather cloud-penetrating flood mapping', 'Soil moisture estimation', 'Paddy rice crop monitoring', 'Coastal boundary detection'],
    dataTier: 'Level-1 Ground Range Detected (GRD) & Level-2 Geocoded',
    availability: 'National Remote Sensing Centre (NRSC)',
  },
  {
    id: 'resourcesat-2',
    name: 'ResourceSat-2 / 2A (LISS-4 & AWiFS)',
    agency: 'ISRO (India)',
    platform: 'ResourceSat-2A',
    modality: 'Multispectral Agriculture & Forestry',
    resolution: '5.8 m (LISS-4) / 23.5 m (LISS-3) / 56 m (AWiFS)',
    revisit: '5 days (LISS-4 mono/steerable)',
    swathWidth: '70 km (LISS-4) / 740 km (AWiFS)',
    bands: [
      { band: 'B2', name: 'Green', center: '520-590 nm', res: '5.8 m' },
      { band: 'B3', name: 'Red', center: '620-680 nm', res: '5.8 m' },
      { band: 'B4', name: 'NIR', center: '770-860 nm', res: '5.8 m' },
      { band: 'B5', name: 'SWIR (LISS-3/AWiFS)', center: '1550-1700 nm', res: '23.5 m' },
    ],
    applications: ['Crop acreage estimation', 'Forest canopy density monitoring', 'Drought surveillance', 'Soil salinity mapping'],
    dataTier: 'Precision Georeferenced Level-1B & Level-2',
    availability: 'Bhoonidhi Archive · NRSC',
  },
]

