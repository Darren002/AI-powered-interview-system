import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Interview from './pages/Interview';
import Report from './pages/Report';
import Dashboard from './pages/Dashboard';
import CandidateDetail from './pages/CandidateDetail';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-black text-white" style={{ backgroundColor: '#000000' }}>
        <Navbar />
        <main className="pt-20">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/interview/:sessionId" element={<Interview />} />
            <Route path="/report/:sessionId" element={<Report />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/hr/candidate/:sessionId" element={<CandidateDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;