import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

// Old pages (기존 Trend 페이지)
import Dashboard from './pages/Dashboard';
import TrendsList from './pages/TrendsList';
import TrendDetail from './pages/TrendDetail';

// New Pain Point Finder pages
import PainPointsDashboard from './pages/PainPointsDashboard';
import PainPointsList from './pages/PainPointsList';
import SaaSIdeasList from './pages/SaaSIdeasList';
import IdeaDetail from './pages/IdeaDetail';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg">
          <div className="max-w-7xl mx-auto px-8 py-4">
            <div className="flex items-center justify-between">
              <Link to="/" className="text-2xl font-bold text-white">
                Pain Point Finder
              </Link>
              <div className="flex gap-6">
                <Link
                  to="/"
                  className="text-white hover:text-blue-100 font-medium transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  to="/pain-points"
                  className="text-white hover:text-blue-100 font-medium transition-colors"
                >
                  Pain Points
                </Link>
                <Link
                  to="/saas-ideas"
                  className="text-white hover:text-blue-100 font-medium transition-colors"
                >
                  SaaS Ideas
                </Link>
                <Link
                  to="/old/trends"
                  className="text-white/70 hover:text-white text-sm font-medium transition-colors"
                >
                  (Old Trends)
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          {/* Pain Point Finder Routes */}
          <Route path="/" element={<PainPointsDashboard />} />
          <Route path="/pain-points" element={<PainPointsList />} />
          <Route path="/saas-ideas" element={<SaaSIdeasList />} />
          <Route path="/saas-ideas/:id" element={<IdeaDetail />} />

          {/* Old Trend Routes */}
          <Route path="/old" element={<Dashboard />} />
          <Route path="/old/trends" element={<TrendsList />} />
          <Route path="/old/trends/:id" element={<TrendDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
