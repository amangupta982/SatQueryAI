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
