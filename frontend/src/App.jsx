import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar.jsx';
import ComplaintPage from './pages/ComplaintPage.jsx';
import ComplaintTrackerPage from './pages/ComplaintTrackerPage.jsx';
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
          <Route path="/complaints/new" element={<ComplaintPage />} />
          <Route path="/complaints/track/:complaint_id" element={<ComplaintTrackerPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
