import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getRoadById } from '../api/roads.js';
import { RoadDetailContent } from '../components/RoadDetailPanel.jsx';

function RoadDetailPage() {
  const { id } = useParams();
  const [road, setRoad] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    async function loadRoad() {
      try {
        setLoading(true);
        const data = await getRoadById(id);
        if (active) setRoad(data);
      } catch {
        if (active) setError('Unable to load road details.');
      } finally {
        if (active) setLoading(false);
      }
    }

    loadRoad();
    return () => {
      active = false;
    };
  }, [id]);

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-[#0f172a] px-4 py-8">
      <div className="mx-auto max-w-3xl">
        <Link className="mb-5 inline-block text-sm font-semibold text-[#38bdf8]" to="/">
          Back to map
        </Link>
        <div className="overflow-hidden rounded-xl bg-[#1e293b] shadow-2xl">
          {loading ? <p className="p-5 text-[#94a3b8]">Loading road details...</p> : null}
          {!loading && error ? <p className="p-5 text-red-300">{error}</p> : null}
          {!loading && road ? <RoadDetailContent road={road} /> : null}
        </div>
      </div>
    </main>
  );
}

export default RoadDetailPage;

