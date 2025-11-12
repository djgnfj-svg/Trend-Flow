import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TrendsList from './pages/TrendsList';
import TrendDetail from './pages/TrendDetail';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-md">
          <div className="max-w-7xl mx-auto px-8 py-4">
            <div className="flex items-center justify-between">
              <Link to="/" className="text-2xl font-bold text-blue-600">
                Trend-Flow
              </Link>
              <div className="flex gap-6">
                <Link
                  to="/"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  대시보드
                </Link>
                <Link
                  to="/trends"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  트렌드 목록
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trends" element={<TrendsList />} />
          <Route path="/trends/:id" element={<TrendDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
