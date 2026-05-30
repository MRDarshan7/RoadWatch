import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar.jsx';
import ComplaintPlaceholderPage from './pages/ComplaintPlaceholderPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import MapPage from './pages/MapPage.jsx';
import RoadDetailPage from './pages/RoadDetailPage.jsx';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0f172a] text-[#f1f5f9]">
        <Navbar />
        <Routes>
          <Route path="/" element={<MapPage />} />
          <Route path="/road/:id" element={<RoadDetailPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/complaints/new" element={<ComplaintPlaceholderPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
