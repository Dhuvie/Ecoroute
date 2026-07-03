import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Polyline, Marker, Popup, CircleMarker } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix default marker icons (Vite doesn't bundle them by default)
delete (L.Icon.Default.prototype as unknown as { _getIconUrl: unknown })._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

interface RouteMapProps {
  path: [number, number][]
  origin?: [number, number]
  destination?: [number, number]
  height?: string
  trafficPoints?: { lat: number; lon: number; level: 'low' | 'medium' | 'high' }[]
}

const TRAFFIC_COLORS = {
  low: '#22c55e',
  medium: '#f59e0b',
  high: '#ef4444',
}

export default function RouteMap({
  path,
  origin,
  destination,
  height = '400px',
  trafficPoints = [],
}: RouteMapProps) {
  const [mapReady, setMapReady] = useState(false)
  useEffect(() => setMapReady(true), [])

  if (!mapReady || path.length === 0) {
    return (
      <div
        className="rounded-lg bg-ink-800/30 flex items-center justify-center text-slate-500 text-sm"
        style={{ height }}
      >
        No route data yet
      </div>
    )
  }

  const center: [number, number] = path[Math.floor(path.length / 2)] || path[0]
  const bounds = L.latLngBounds(path.map(([lat, lon]) => [lat, lon]))

  return (
    <div className="rounded-lg overflow-hidden border border-ink-800" style={{ height }}>
      <MapContainer
        center={center}
        zoom={6}
        scrollWheelZoom
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        <Polyline positions={path} color="#22c55e" weight={4} opacity={0.8} />
        {origin && (
          <Marker position={origin}>
            <Popup>Origin</Popup>
          </Marker>
        )}
        {destination && (
          <Marker position={destination}>
            <Popup>Destination</Popup>
          </Marker>
        )}
        {trafficPoints.map((pt, i) => (
          <CircleMarker
            key={i}
            center={[pt.lat, pt.lon]}
            radius={6}
            pathOptions={{
              color: TRAFFIC_COLORS[pt.level],
              fillColor: TRAFFIC_COLORS[pt.level],
              fillOpacity: 0.7,
            }}
          >
            <Popup>Traffic: {pt.level}</Popup>
          </CircleMarker>
        ))}
        {/* Auto-fit */}
        <FitBounds bounds={bounds} />
      </MapContainer>
    </div>
  )
}

// Helper component to fit bounds
function FitBounds({ bounds }: { bounds: L.LatLngBounds }) {
  const map = useMap()
  useEffect(() => {
    try {
      map.fitBounds(bounds, { padding: [40, 40] })
    } catch {
      // ignore
    }
  }, [map, bounds])
  return null
}

// Hook
import { useMap } from 'react-leaflet'
