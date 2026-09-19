import React, { useEffect, useRef } from 'react'
import * as THREE from 'three'

/**
 * Photorealistic 3D Earth Globe with:
 * - Continuous rounding / rotation animation around tilted axis
 * - Dynamic Day / Night terminator with glowing city lights
 * - Swirling realistic cloud layer with independent drift
 * - Atmospheric limb Rayleigh glow (electric cyan halo)
 * - Orbiting satellite with telemetry trail & beacon
 * - Deep space starfield
 * - Zero seams or joint lines
 */
export default function EarthScene({ className = '' }) {
  const containerRef = useRef(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    let animationFrameId
    let isDisposed = false

    // 1. Scene & Camera
    const scene = new THREE.Scene()
    const width = container.clientWidth || window.innerWidth
    const height = container.clientHeight || window.innerHeight

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
    // Position camera to frame Earth from low-to-medium orbit
    camera.position.set(0, 0.4, 3.1)

    // 2. WebGL Renderer with High-DPI support
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    })
    renderer.setSize(width, height)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.25
    container.appendChild(renderer.domElement)

    // 3. Texture Loader with local NASA Earth assets
    const textureLoader = new THREE.TextureLoader()
    const dayTexture = textureLoader.load('/textures/planets/earth_atmos_2048.jpg')
    const nightTexture = textureLoader.load('/textures/planets/earth_lights_2048.png')
    const cloudsTexture = textureLoader.load('/textures/planets/earth_clouds_1024.png')
    const specularTexture = textureLoader.load('/textures/planets/earth_specular_2048.jpg')
    const satelliteTexture = textureLoader.load('/satellite_model.png')

    // Set wrapping to RepeatWrapping for seamless 360 rotation
    dayTexture.wrapS = THREE.RepeatWrapping
    nightTexture.wrapS = THREE.RepeatWrapping
    cloudsTexture.wrapS = THREE.RepeatWrapping
    specularTexture.wrapS = THREE.RepeatWrapping

    // 4. Starfield Background (1,500 particles in deep space)
    const starCount = 1200
    const starGeometry = new THREE.BufferGeometry()
    const starPositions = new Float32Array(starCount * 3)
    const starColors = new Float32Array(starCount * 3)

    for (let i = 0; i < starCount; i++) {
      const idx = i * 3
      // Distribute in a hemisphere behind the earth
      const r = 25 + Math.random() * 40
      const theta = Math.random() * Math.PI * 2
      const phi = Math.random() * Math.PI * 0.8
      starPositions[idx] = r * Math.sin(phi) * Math.cos(theta)
      starPositions[idx + 1] = r * Math.cos(phi) * 0.7 + 5 // higher in sky
      starPositions[idx + 2] = -r * Math.sin(phi) * Math.sin(theta) - 10

      // Color variation: white, cyan, and warm yellow stars
      const tint = Math.random()
      if (tint > 0.85) {
        starColors[idx] = 0.5; starColors[idx + 1] = 0.85; starColors[idx + 2] = 1.0 // cyan
      } else if (tint > 0.7) {
        starColors[idx] = 1.0; starColors[idx + 1] = 0.9; starColors[idx + 2] = 0.6 // warm
      } else {
        starColors[idx] = 0.95; starColors[idx + 1] = 0.95; starColors[idx + 2] = 1.0 // white
      }
    }
    starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3))
    starGeometry.setAttribute('color', new THREE.BufferAttribute(starColors, 3))

    const starMaterial = new THREE.PointsMaterial({
      size: 0.08,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
    })
    const starField = new THREE.Points(starGeometry, starMaterial)
    scene.add(starField)

    // 5. Earth Globe Group (tilted at real planetary axial tilt 23.4°)
    const earthGroup = new THREE.Group()
    // Position Earth lower in screen so the top hemisphere arcs across the bottom/center
    earthGroup.position.set(0.1, -2.05, 0)
    earthGroup.rotation.z = -23.4 * (Math.PI / 180)
    earthGroup.rotation.x = 0.18
    scene.add(earthGroup)

    const earthRadius = 2.45

    // 6. Custom Earth Day/Night Shader Material
    // Blends daytime continents/oceans, specular ocean reflection, and night city lights seamlessly!
    const sunDirection = new THREE.Vector3(1.2, 0.35, 0.8).normalize()

    const earthShader = {
      uniforms: {
        dayTexture: { value: dayTexture },
        nightTexture: { value: nightTexture },
        specularTexture: { value: specularTexture },
        sunDirection: { value: sunDirection },
        atmosphereColor: { value: new THREE.Color('#38bdf8') },
      },
      vertexShader: `
        varying vec2 vUv;
        varying vec3 vNormal;
        varying vec3 vWorldPosition;
        varying vec3 vViewPosition;

        void main() {
          vUv = uv;
          vNormal = normalize(normalMatrix * normal);
          vec4 worldPos = modelMatrix * vec4(position, 1.0);
          vWorldPosition = worldPos.xyz;
          vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
          vViewPosition = -mvPosition.xyz;
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        uniform sampler2D dayTexture;
        uniform sampler2D nightTexture;
        uniform sampler2D specularTexture;
        uniform vec3 sunDirection;
        uniform vec3 atmosphereColor;

        varying vec2 vUv;
        varying vec3 vNormal;
        varying vec3 vWorldPosition;
        varying vec3 vViewPosition;

        void main() {
          vec3 normal = normalize(vNormal);
          vec3 viewDir = normalize(vViewPosition);

          // Sunlight calculation
          float nDotL = dot(normal, sunDirection);

          // Smooth transition between night and day across the terminator
          float dayFactor = smoothstep(-0.18, 0.22, nDotL);

          // Sample textures
          vec4 dayColor = texture2D(dayTexture, vUv);
          vec4 nightColor = texture2D(nightTexture, vUv);
          vec4 specMap = texture2D(specularTexture, vUv);

          // Specular reflection of the sun on oceans
          vec3 halfVector = normalize(sunDirection + viewDir);
          float specIntensity = pow(max(dot(normal, halfVector), 0.0), 32.0) * specMap.r * 1.8;
          vec3 specularHighlight = vec3(1.0, 0.95, 0.8) * specIntensity * dayFactor;

          // Night city lights boosted intensity with warm golden amber tint
          vec3 cityLights = nightColor.rgb * vec3(1.4, 1.25, 0.9) * 1.6 * (1.0 - dayFactor);

          // Twilight terminator warm amber glow
          float terminator = smoothstep(0.35, 0.0, abs(nDotL));
          vec3 sunsetGlow = vec3(0.9, 0.45, 0.15) * terminator * 0.45;

          // Atmospheric limb Fresnel glow (electric cyan rim)
          float fresnel = pow(1.0 - max(dot(normal, viewDir), 0.0), 3.2);
          vec3 limbGlow = atmosphereColor * fresnel * 0.95 * (dayFactor * 0.7 + 0.3);

          // Combine all lighting layers seamlessly
          vec3 finalColor = mix(cityLights, dayColor.rgb * 1.1 + specularHighlight, dayFactor);
          finalColor += sunsetGlow + limbGlow;

          gl_FragColor = vec4(finalColor, 1.0);
        }
      `,
    }

    const earthMaterial = new THREE.ShaderMaterial({
      uniforms: earthShader.uniforms,
      vertexShader: earthShader.vertexShader,
      fragmentShader: earthShader.fragmentShader,
    })

    const earthMesh = new THREE.Mesh(
      new THREE.SphereGeometry(earthRadius, 64, 64),
      earthMaterial
    )
    earthGroup.add(earthMesh)

    // 7. Swirling Cloud Layer Mesh (slightly larger sphere with transparency)
    const cloudsMaterial = new THREE.MeshStandardMaterial({
      map: cloudsTexture,
      transparent: true,
      opacity: 0.38,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
    const cloudsMesh = new THREE.Mesh(
      new THREE.SphereGeometry(earthRadius + 0.018, 64, 64),
      cloudsMaterial
    )
    earthGroup.add(cloudsMesh)

    // 8. Outer Atmospheric Halo Glow Mesh
    const atmosphereShader = {
      uniforms: {
        glowColor: { value: new THREE.Color('#38bdf8') },
      },
      vertexShader: `
        varying vec3 vNormal;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec3 glowColor;
        varying vec3 vNormal;
        void main() {
          float intensity = pow(0.7 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.8);
          gl_FragColor = vec4(glowColor, intensity * 0.85);
        }
      `,
    }
    const atmosphereMaterial = new THREE.ShaderMaterial({
      uniforms: atmosphereShader.uniforms,
      vertexShader: atmosphereShader.vertexShader,
      fragmentShader: atmosphereShader.fragmentShader,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
      transparent: true,
      depthWrite: false,
    })
    const atmosphereMesh = new THREE.Mesh(
      new THREE.SphereGeometry(earthRadius + 0.065, 64, 64),
      atmosphereMaterial
    )
    earthGroup.add(atmosphereMesh)

    // 9. Sunrise / Sunburst Corona Flare on Horizon
    const sunFlareCanvas = document.createElement('canvas')
    sunFlareCanvas.width = 256
    sunFlareCanvas.height = 256
    const sCtx = sunFlareCanvas.getContext('2d')
    const gradient = sCtx.createRadialGradient(128, 128, 0, 128, 128, 128)
    gradient.addColorStop(0, 'rgba(255, 255, 230, 1)')
    gradient.addColorStop(0.15, 'rgba(255, 220, 130, 0.8)')
    gradient.addColorStop(0.4, 'rgba(56, 189, 248, 0.45)')
    gradient.addColorStop(1, 'rgba(56, 189, 248, 0)')
    sCtx.fillStyle = gradient
    sCtx.fillRect(0, 0, 256, 256)

    const sunFlareTexture = new THREE.CanvasTexture(sunFlareCanvas)
    const sunFlareMaterial = new THREE.SpriteMaterial({
      map: sunFlareTexture,
      blending: THREE.AdditiveBlending,
      transparent: true,
      opacity: 0.95,
      depthWrite: false,
    })
    const sunFlareSprite = new THREE.Sprite(sunFlareMaterial)
    // Position sunrise flare right on the horizon curvature (upper-right horizon)
    sunFlareSprite.position.set(0.65, 0.48, 0.1)
    sunFlareSprite.scale.set(1.4, 1.4, 1.0)
    scene.add(sunFlareSprite)

    // 10. Satellite in Dynamic Orbital Flight
    const satelliteGroup = new THREE.Group()

    // 3D Billboard Sprite with the high-res satellite PNG
    const satelliteMaterial = new THREE.SpriteMaterial({
      map: satelliteTexture,
      transparent: true,
      opacity: 1.0,
      depthTest: true,
    })
    const satelliteSprite = new THREE.Sprite(satelliteMaterial)
    satelliteSprite.scale.set(0.72, 0.72, 1)
    satelliteGroup.add(satelliteSprite)

    // Blinking Telemetry Beacon LED on Satellite
    const beaconCanvas = document.createElement('canvas')
    beaconCanvas.width = 64
    beaconCanvas.height = 64
    const bCtx = beaconCanvas.getContext('2d')
    const bGrad = bCtx.createRadialGradient(32, 32, 0, 32, 32, 32)
    bGrad.addColorStop(0, '#67e8f9')
    bGrad.addColorStop(0.3, '#0284c7')
    bGrad.addColorStop(1, 'rgba(2, 132, 199, 0)')
    bCtx.fillStyle = bGrad
    bCtx.fillRect(0, 0, 64, 64)

    const beaconTexture = new THREE.CanvasTexture(beaconCanvas)
    const beaconMaterial = new THREE.SpriteMaterial({
      map: beaconTexture,
      blending: THREE.AdditiveBlending,
      transparent: true,
      opacity: 1.0,
    })
    const beaconSprite = new THREE.Sprite(beaconMaterial)
    beaconSprite.position.set(-0.02, 0.04, 0.05)
    beaconSprite.scale.set(0.16, 0.16, 1)
    satelliteGroup.add(beaconSprite)

    scene.add(satelliteGroup)

    // Orbital Path Trajectory Curve: Spans from RIGHT to LEFT across space
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(3.1, 0.55, 0.85),   // starts on the RIGHT edge
      new THREE.Vector3(1.5, 0.85, 0.65),   // passes over sunrise horizon
      new THREE.Vector3(-0.2, 1.10, 0.40),  // glides across center upper sky
      new THREE.Vector3(-1.7, 1.28, 0.10),  // travels through upper left
      new THREE.Vector3(-3.1, 1.38, -0.25), // exits on the LEFT edge
    ])
    const points = curve.getPoints(80)
    const orbitGeometry = new THREE.BufferGeometry().setFromPoints(points)
    const orbitMaterial = new THREE.LineDashedMaterial({
      color: 0x38bdf8,
      linewidth: 1.5,
      scale: 1,
      dashSize: 0.08,
      gapSize: 0.06,
      transparent: true,
      opacity: 0.35,
    })
    const orbitLine = new THREE.Line(orbitGeometry, orbitMaterial)
    orbitLine.computeLineDistances()
    scene.add(orbitLine)

    // 11. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.18)
    scene.add(ambientLight)

    const dirLight = new THREE.DirectionalLight(0xfff5e6, 2.4)
    dirLight.position.set(4, 2, 3)
    scene.add(dirLight)

    // 12. Animation Loop: Earth Continuous Rotation & Satellite Orbit Motion (Right to Left Loop)
    let clock = new THREE.Clock()
    const orbitDuration = 15.0 // 15 seconds for complete pass from right to left

    const animate = () => {
      if (isDisposed) return
      animationFrameId = requestAnimationFrame(animate)

      const elapsed = clock.getElapsedTime()

      // Continuous, seamless Earth spherical rotation around its polar axis
      earthMesh.rotation.y = elapsed * 0.032

      // Clouds rotate at slightly faster pace for realistic atmospheric drift
      cloudsMesh.rotation.y = elapsed * 0.038

      // Subtle atmospheric pulse
      atmosphereMesh.scale.setScalar(1.0 + Math.sin(elapsed * 1.5) * 0.003)

      // Satellite continuous orbital motion: REVERSE (RIGHT TO LEFT)
      // As soon as it disappears on the left (progress -> 1.0), it immediately appears on the right (progress -> 0.0)
      const progress = (elapsed % orbitDuration) / orbitDuration // 0.0 (right) to 1.0 (left)
      const orbitPoint = curve.getPointAt(progress)
      satelliteGroup.position.copy(orbitPoint)

      // Align satellite heading smoothly with flight path tangent moving right to left
      const tangent = curve.getTangentAt(progress)
      const flightAngle = Math.atan2(tangent.y, tangent.x)
      // Keep satellite upright with realistic pitch along trajectory
      const normalizedPitch = Math.sin(flightAngle) * 0.25
      satelliteSprite.material.rotation = normalizedPitch

      // Micro edge fade (only 2% of path) so it disappears right at the left margin
      // and appears on the right margin with zero empty delay
      let edgeOpacity = 1.0
      if (progress < 0.02) {
        edgeOpacity = progress / 0.02
      } else if (progress > 0.98) {
        edgeOpacity = (1.0 - progress) / 0.02
      }
      satelliteSprite.material.opacity = Math.max(0.0, Math.min(1.0, edgeOpacity))

      // Satellite scale with subtle float breathing
      const currentScale = 0.68 + Math.sin(elapsed * 1.2) * 0.02
      satelliteSprite.scale.set(currentScale, currentScale, 1)

      // Telemetry beacon LED blinking on satellite antenna
      const beaconPulse = Math.sin(elapsed * 4.5)
      const beaconActive = beaconPulse > 0.15
      beaconSprite.material.opacity = (beaconActive ? 1.0 : 0.1) * edgeOpacity
      beaconSprite.scale.setScalar(beaconActive ? 0.22 : 0.08)

      // Sun flare subtle shimmering
      sunFlareSprite.material.opacity = 0.85 + Math.sin(elapsed * 2.2) * 0.1

      renderer.render(scene, camera)
    }

    animate()

    // 13. Responsive Window Resize Handler
    const handleResize = () => {
      if (!container || isDisposed) return
      const newWidth = container.clientWidth
      const newHeight = container.clientHeight
      camera.aspect = newWidth / newHeight
      camera.updateProjectionMatrix()
      renderer.setSize(newWidth, newHeight)
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
    }

    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => {
      isDisposed = true
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener('resize', handleResize)
      if (container && renderer.domElement && container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement)
      }
      renderer.dispose()
      earthMesh.geometry.dispose()
      earthMaterial.dispose()
      cloudsMesh.geometry.dispose()
      cloudsMaterial.dispose()
      atmosphereMesh.geometry.dispose()
      atmosphereMaterial.dispose()
      starGeometry.dispose()
      starMaterial.dispose()
      sunFlareTexture.dispose()
      sunFlareMaterial.dispose()
      satelliteMaterial.dispose()
      beaconTexture.dispose()
      beaconMaterial.dispose()
      orbitGeometry.dispose()
      orbitMaterial.dispose()
    }
  }, [])

  return (
    <div
      ref={containerRef}
      className={`absolute inset-0 w-full h-full pointer-events-none overflow-hidden ${className}`}
      style={{ zIndex: 0 }}
    />
  )
}
