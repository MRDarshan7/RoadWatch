import { NavLink } from 'react-router-dom';
import { useState } from 'react';

const navItems = [
  { to: '/', label: 'Map' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/complaints/new', label: 'Report Issue' },
];

function Logo() {
  return (
    <svg
      aria-hidden="true"
      className="h-8 w-8"
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M16 42C25 33 22 15 32 6"
        stroke="#38bdf8"
        strokeWidth="5"
        strokeLinecap="round"
      />
      <path
        d="M24 42C31 32 29 19 38 9"
        stroke="#f1f5f9"
        strokeWidth="5"
        strokeLinecap="round"
      />
      <path d="M26 35L30 29M28 23L32 17" stroke="#1a1a2e" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function Navbar() {
  const [open, setOpen] = useState(false);

  const linkClass = ({ isActive }) =>
    `rounded-lg px-3 py-2 text-sm font-semibold transition ${
      isActive ? 'bg-[#38bdf8] text-[#0f172a]' : 'text-white hover:bg-white/10'
    }`;

  return (
    <header className="sticky top-0 z-[1100] bg-[#1a1a2e] text-white shadow-lg">
      <nav className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <NavLink to="/" className="flex items-center gap-3" onClick={() => setOpen(false)}>
          <Logo />
          <span className="text-xl font-bold tracking-normal">RoadWatch</span>
        </NavLink>

        <button
          type="button"
          className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-white/20 text-white md:hidden"
          aria-label="Toggle navigation"
          onClick={() => setOpen((value) => !value)}
        >
          <span className="flex flex-col gap-1.5">
            <span className="block h-0.5 w-5 bg-white" />
            <span className="block h-0.5 w-5 bg-white" />
            <span className="block h-0.5 w-5 bg-white" />
          </span>
        </button>

        <div className="hidden items-center gap-2 md:flex">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={linkClass}>
              {item.label}
            </NavLink>
          ))}
        </div>
      </nav>

      {open ? (
        <div className="border-t border-white/10 px-4 pb-4 md:hidden">
          <div className="flex flex-col gap-2 pt-3">
            {navItems.map((item) => (
              <NavLink key={item.to} to={item.to} className={linkClass} onClick={() => setOpen(false)}>
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>
      ) : null}
    </header>
  );
}

export default Navbar;

