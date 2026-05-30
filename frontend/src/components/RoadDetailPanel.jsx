import { Link, useNavigate } from 'react-router-dom';

export const ROAD_TYPE_COLORS = {
  NH: '#ef4444',
  SH: '#f97316',
  Corporation: '#3b82f6',
  Panchayat: '#22c55e',
};

const healthColor = (score) => {
  if (score >= 70) return 'bg-[#22c55e]';
  if (score >= 40) return 'bg-[#f59e0b]';
  return 'bg-[#ef4444]';
};

const budgetColor = (ratio) => {
  if (ratio < 80) return 'bg-[#22c55e]';
  if (ratio <= 95) return 'bg-[#f59e0b]';
  return 'bg-[#ef4444]';
};

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value || 0);

const formatDate = (value) => {
  if (!value) return 'Not available';
  return new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value));
};

function Skeleton() {
  return (
    <div className="space-y-4 p-5">
      {[1, 2, 3, 4].map((item) => (
        <div key={item} className="rounded-xl bg-[#334155] p-4 shadow-lg">
          <div className="mb-3 h-5 w-2/3 animate-pulse rounded bg-slate-500/70" />
          <div className="h-3 w-full animate-pulse rounded bg-slate-600/70" />
          <div className="mt-2 h-3 w-4/5 animate-pulse rounded bg-slate-600/70" />
        </div>
      ))}
    </div>
  );
}

function LegendContent() {
  return (
    <div className="space-y-5 p-5">
      <div>
        <h2 className="text-xl font-bold text-[#f1f5f9]">Road Network</h2>
        <p className="mt-2 text-sm leading-6 text-[#94a3b8]">Click any road to view details.</p>
      </div>
      <div className="rounded-xl bg-[#334155] p-4 shadow-lg">
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[#94a3b8]">Road Type Legend</h3>
        <div className="space-y-3 text-sm text-[#f1f5f9]">
          {Object.entries(ROAD_TYPE_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-3">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: color }} />
              <span>{type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Badge({ children, className = '', style }) {
  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-bold ${className}`} style={style}>
      {children}
    </span>
  );
}

export function RoadDetailContent({ road }) {
  const navigate = useNavigate();
  const project = road?.latest_project;
  const maintenance = road?.latest_maintenance;
  const authority = road?.assigned_authority;
  const complaints = road?.complaint_summary;
  const spentRatio =
    project?.sanctioned_amount > 0 ? Math.min(100, (project.spent_amount / project.sanctioned_amount) * 100) : 0;
  const healthScore = road?.health_score ?? 0;

  return (
    <div className="space-y-4 p-5">
      <section className="rounded-xl bg-[#334155] p-4 shadow-lg">
        <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold leading-tight text-[#f1f5f9]">{road.road_name}</h1>
            <p className="mt-2 text-sm text-[#94a3b8]">
              {road.zone} - {road.ward}
            </p>
          </div>
          <Badge className="text-white" style={{ backgroundColor: ROAD_TYPE_COLORS[road.road_type] }}>
            {road.road_type}
          </Badge>
        </div>
      </section>

      <section className="rounded-xl bg-[#334155] p-4 shadow-lg">
        <div className="mb-3 flex items-center justify-between gap-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94a3b8]">Road Health Score</h2>
          <span className="text-xl font-bold text-[#f1f5f9]">{healthScore}</span>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-[#1e293b]">
          <div className={`h-full rounded-full ${healthColor(healthScore)}`} style={{ width: `${healthScore}%` }} />
        </div>
        <p className="mt-3 text-sm text-[#94a3b8]">
          {maintenance?.days_since_repair != null
            ? `Last repaired ${maintenance.days_since_repair} days ago`
            : 'Repair history not available'}
        </p>
      </section>

      <section className="rounded-xl bg-[#334155] p-4 shadow-lg">
        <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94a3b8]">Project Budget</h2>
            <p className="mt-2 text-sm text-[#94a3b8]">{project?.contractor_name || 'Contractor not available'}</p>
            <p className="text-xs text-[#94a3b8]">{project?.tender_id || 'Tender ID not available'}</p>
          </div>
          <Badge className="bg-[#1e293b] text-[#38bdf8]">{project?.status || 'Unknown'}</Badge>
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between gap-4">
            <span className="text-[#94a3b8]">Sanctioned</span>
            <span className="font-semibold text-[#f1f5f9]">{formatCurrency(project?.sanctioned_amount)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-[#94a3b8]">Spent</span>
            <span className="font-semibold text-[#f1f5f9]">{formatCurrency(project?.spent_amount)}</span>
          </div>
        </div>
        <div className="mt-4 h-3 overflow-hidden rounded-full bg-[#1e293b]">
          <div className={`h-full rounded-full ${budgetColor(spentRatio)}`} style={{ width: `${spentRatio}%` }} />
        </div>
      </section>

      <section className="rounded-xl bg-[#334155] p-4 shadow-lg">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[#94a3b8]">Maintenance</h2>
        <div className="space-y-3 text-sm text-[#f1f5f9]">
          <div className="flex justify-between gap-4">
            <span className="text-[#94a3b8]">Last relaying</span>
            <span>{formatDate(maintenance?.last_relaying_date)}</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-[#94a3b8]">Activity</span>
            <Badge className="bg-[#1e293b] text-[#f1f5f9]">{maintenance?.activity_type || 'Unknown'}</Badge>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-[#94a3b8]">Next scheduled</span>
            <span>{formatDate(maintenance?.next_scheduled)}</span>
          </div>
        </div>
      </section>

      <section className="rounded-xl bg-[#334155] p-4 shadow-lg">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[#94a3b8]">Authority</h2>
        <p className="font-semibold text-[#f1f5f9]">{authority?.department_name || 'Authority not assigned'}</p>
        <p className="mt-2 text-sm text-[#94a3b8]">
          {authority?.officer_name || 'Officer not available'}
          {authority?.designation ? `, ${authority.designation}` : ''}
        </p>
        {authority?.contact ? (
          <a className="mt-3 inline-block text-sm font-semibold text-[#38bdf8]" href={`tel:${authority.contact}`}>
            {authority.contact}
          </a>
        ) : null}
      </section>

      <section className="rounded-xl bg-[#334155] p-4 shadow-lg">
        <div className="mb-3 flex items-center justify-between gap-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[#94a3b8]">Complaints</h2>
          <div className="text-sm text-[#f1f5f9]">
            <span className="font-bold">{complaints?.total_complaints ?? 0}</span>
            <span className="text-[#94a3b8]"> total - </span>
            <span className="font-bold">{complaints?.open_complaints ?? 0}</span>
            <span className="text-[#94a3b8]"> open</span>
          </div>
        </div>
        {complaints?.latest_descriptions?.length ? (
          <ul className="mb-4 list-disc space-y-2 pl-5 text-sm text-[#94a3b8]">
            {complaints.latest_descriptions.map((description) => (
              <li key={description}>{description.length > 60 ? `${description.slice(0, 60)}...` : description}</li>
            ))}
          </ul>
        ) : (
          <p className="mb-4 text-sm text-[#94a3b8]">No complaints recorded yet.</p>
        )}
        <button
          type="button"
          className="w-full rounded-xl bg-[#38bdf8] px-4 py-3 text-sm font-bold text-[#0f172a] transition hover:bg-sky-300"
          onClick={() => navigate(`/complaints/new?road_id=${road.road_id}`)}
        >
          Report Issue
        </button>
      </section>

      <Link className="block text-center text-sm font-semibold text-[#38bdf8]" to={`/road/${road.road_id}`}>
        Open full road page
      </Link>
    </div>
  );
}

function RoadDetailPanel({ road, loading, error, onClose }) {
  const isActive = Boolean(road || loading || error);

  return (
    <aside
      className={`fixed inset-x-0 bottom-0 z-[900] max-h-[60vh] overflow-y-auto rounded-t-2xl bg-[#1e293b] shadow-2xl transition-transform duration-300 ease-in-out md:static md:h-full md:max-h-none md:w-[30%] md:translate-y-0 md:rounded-none ${
        isActive ? 'translate-y-0' : 'translate-y-full'
      }`}
    >
      <div className="sticky top-0 z-10 flex items-center justify-between bg-[#1e293b]/95 px-5 py-4 backdrop-blur">
        <div className="mx-auto h-1.5 w-12 rounded-full bg-[#94a3b8] md:hidden" />
        {road || loading || error ? (
          <button
            type="button"
            className="ml-auto flex h-9 w-9 items-center justify-center rounded-full bg-[#334155] text-lg font-bold text-[#f1f5f9] transition hover:bg-slate-500"
            aria-label="Close road detail"
            onClick={onClose}
          >
            x
          </button>
        ) : null}
      </div>
      {loading ? <Skeleton /> : null}
      {!loading && error ? <p className="p-5 text-sm text-red-300">{error}</p> : null}
      {!loading && !error && road ? <RoadDetailContent road={road} /> : null}
      {!loading && !error && !road ? <LegendContent /> : null}
    </aside>
  );
}

export default RoadDetailPanel;
