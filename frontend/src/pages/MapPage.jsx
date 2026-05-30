import { Fragment, useEffect, useMemo, useState } from 'react';
import { MapContainer, Polyline, TileLayer, useMap } from 'react-leaflet';
import { getAllRoads, getRoadById, searchRoads } from '../api/roads.js';
import RoadDetailPanel, { ROAD_TYPE_COLORS } from '../components/RoadDetailPanel.jsx';

const CHENNAI_CENTER = [13.0827, 80.2707];

function Legend() {
  return (
    <div className="absolute bottom-5 left-5 z-[500] hidden rounded-xl bg-[#1e293b]/95 p-4 text-sm text-[#f1f5f9] shadow-xl backdrop-blur md:block">
      <div className="mb-3 font-bold">Road Types</div>
      <div className="space-y-2">
        {Object.entries(ROAD_TYPE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span>{type}</span>
          </div>
        ))}
      </div>
      <p className="mt-3 text-xs text-[#94a3b8]">Click any road to view details</p>
    </div>
  );
}

function MapFocus({ road }) {
  const map = useMap();

  useEffect(() => {
    if (!road) return;
    const bounds = [
      [road.start_lat, road.start_lng],
      [road.end_lat, road.end_lng],
    ];
    map.fitBounds(bounds, { padding: [80, 80], maxZoom: 15 });
  }, [map, road]);

  return null;
}

function SearchBox({ onSelect }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const trimmed = query.trim();
    if (!trimmed) {
      setResults([]);
      setError('');
      return undefined;
    }

    const timer = window.setTimeout(async () => {
      try {
        setLoading(true);
        setError('');
        const matches = await searchRoads(trimmed);
        setResults(matches.slice(0, 8));
      } catch {
        setError('Search failed');
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 400);

    return () => window.clearTimeout(timer);
  }, [query]);

  const chooseRoad = (road) => {
    setQuery(road.road_name);
    setResults([]);
    onSelect(road);
  };

  return (
    <div className="absolute left-4 right-4 top-4 z-[650] mx-auto max-w-xl">
      <div className="rounded-xl bg-[#1e293b]/95 p-2 shadow-2xl backdrop-blur">
        <label className="sr-only" htmlFor="road-search">
          Search roads
        </label>
        <input
          id="road-search"
          className="h-12 w-full rounded-lg border border-slate-600 bg-[#0f172a] px-4 text-sm font-medium text-[#f1f5f9] outline-none transition placeholder:text-[#94a3b8] focus:border-[#38bdf8]"
          type="search"
          placeholder="Search Chennai roads"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </div>
      {(results.length > 0 || loading || error) && (
        <div className="mt-2 overflow-hidden rounded-xl bg-[#1e293b] shadow-2xl">
          {loading ? <div className="px-4 py-3 text-sm text-[#94a3b8]">Searching...</div> : null}
          {error ? <div className="px-4 py-3 text-sm text-red-300">{error}</div> : null}
          {!loading &&
            results.map((road) => (
              <button
                key={road.road_id}
                type="button"
                className="block w-full px-4 py-3 text-left text-sm text-[#f1f5f9] transition hover:bg-[#334155]"
                onClick={() => chooseRoad(road)}
              >
                <span className="block font-semibold">{road.road_name}</span>
                <span className="text-xs text-[#94a3b8]">
                  {road.road_type} - {road.zone}
                </span>
              </button>
            ))}
        </div>
      )}
    </div>
  );
}

function MapPage() {
  const [roads, setRoads] = useState([]);
  const [roadsLoading, setRoadsLoading] = useState(true);
  const [roadsError, setRoadsError] = useState('');
  const [selectedRoadId, setSelectedRoadId] = useState('');
  const [selectedRoad, setSelectedRoad] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');
  const [focusedRoad, setFocusedRoad] = useState(null);
  const [hoveredRoadId, setHoveredRoadId] = useState('');

  useEffect(() => {
    let active = true;

    async function loadRoads() {
      try {
        setRoadsLoading(true);
        const data = await getAllRoads();
        if (active) setRoads(data);
      } catch {
        if (active) setRoadsError('Unable to load roads from the backend.');
      } finally {
        if (active) setRoadsLoading(false);
      }
    }

    loadRoads();
    return () => {
      active = false;
    };
  }, []);

  const roadsById = useMemo(() => new Map(roads.map((road) => [road.road_id, road])), [roads]);

  const openRoad = async (road) => {
    const roadId = road.road_id;
    setSelectedRoadId(roadId);
    setFocusedRoad(road);
    setSelectedRoad(null);
    setDetailError('');
    setDetailLoading(true);

    try {
      const detail = await getRoadById(roadId);
      setSelectedRoad(detail);
    } catch {
      setDetailError('Unable to load road details.');
    } finally {
      setDetailLoading(false);
    }
  };

  const closePanel = () => {
    setSelectedRoadId('');
    setSelectedRoad(null);
    setDetailError('');
    setFocusedRoad(null);
  };

  return (
    <main className="flex h-[calc(100vh-4rem)] flex-col bg-[#0f172a] md:flex-row">
      <section className="relative h-full min-h-[calc(100vh-4rem)] md:w-[70%]">
        <MapContainer center={CHENNAI_CENTER} zoom={12} className="h-full w-full">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapFocus road={focusedRoad} />
          {roads.map((road) => {
            const selected = selectedRoadId === road.road_id;
            const hovered = hoveredRoadId === road.road_id;
            const positions = [
              [road.start_lat, road.start_lng],
              [road.end_lat, road.end_lng],
            ];
            const color = ROAD_TYPE_COLORS[road.road_type] || '#38bdf8';
            return (
              <Fragment key={road.road_id}>
                {selected ? (
                  <Polyline
                    positions={positions}
                    pathOptions={{ color: '#facc15', weight: 11, opacity: 0.95 }}
                  />
                ) : null}
                <Polyline
                  positions={positions}
                  pathOptions={{
                    color,
                    weight: selected ? 8 : hovered ? 7 : 4,
                    opacity: selected || hovered ? 1 : 0.8,
                  }}
                  eventHandlers={{
                    mouseover: () => setHoveredRoadId(road.road_id),
                    mouseout: () => setHoveredRoadId(''),
                    click: () => openRoad(road),
                  }}
                />
              </Fragment>
            );
          })}
        </MapContainer>

        <SearchBox
          onSelect={(road) => {
            const fullRoad = roadsById.get(road.road_id) || road;
            openRoad(fullRoad);
          }}
        />
        <Legend />

        {roadsLoading ? (
          <div className="absolute left-4 top-24 z-[600] rounded-xl bg-[#1e293b] px-4 py-3 text-sm text-[#94a3b8] shadow-xl">
            Loading roads...
          </div>
        ) : null}
        {roadsError ? (
          <div className="absolute left-4 top-24 z-[600] rounded-xl bg-red-950 px-4 py-3 text-sm text-red-100 shadow-xl">
            {roadsError}
          </div>
        ) : null}
      </section>

      <RoadDetailPanel road={selectedRoad} loading={detailLoading} error={detailError} onClose={closePanel} />
    </main>
  );
}

export default MapPage;
