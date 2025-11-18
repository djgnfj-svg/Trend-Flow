import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { painPointsApi } from '../services/painPointApi';

export default function PainPointsList() {
  const [painPoints, setPainPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    severity: '',
    category: '',
    source: '',
    min_confidence: '',
  });

  useEffect(() => {
    loadPainPoints();
  }, [filters]);

  const loadPainPoints = async () => {
    try {
      setLoading(true);
      const data = await painPointsApi.getAll(filters);
      setPainPoints(data);
    } catch (error) {
      console.error('Failed to load pain points:', error);
    } finally {
      setLoading(false);
    }
  };

  const severityColors = {
    critical: 'bg-red-100 text-red-800 border-red-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200',
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Pain Points</h1>
              <p className="mt-2 text-sm text-gray-600">
                실제 사용자들이 겪고 있는 문제점들
              </p>
            </div>
            <Link
              to="/"
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Dashboard
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Severity
              </label>
              <select
                value={filters.severity}
                onChange={(e) => handleFilterChange('severity', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">All</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Confidence
              </label>
              <select
                value={filters.min_confidence}
                onChange={(e) => handleFilterChange('min_confidence', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">All</option>
                <option value="0.8">0.8+</option>
                <option value="0.7">0.7+</option>
                <option value="0.6">0.6+</option>
                <option value="0.5">0.5+</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <input
                type="text"
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                placeholder="e.g., productivity"
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Source</label>
              <input
                type="text"
                value={filters.source}
                onChange={(e) => handleFilterChange('source', e.target.value)}
                placeholder="e.g., reddit_sideproject"
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
          </div>
        </div>

        {/* Pain Points List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="text-lg text-gray-600">Loading...</div>
          </div>
        ) : painPoints.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-gray-400 text-lg">No pain points found</div>
          </div>
        ) : (
          <div className="space-y-4">
            {painPoints.map((painPoint) => (
              <div
                key={painPoint.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition p-6"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          severityColors[painPoint.severity] || 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {painPoint.severity?.toUpperCase() || 'UNKNOWN'}
                      </span>
                      <span className="px-3 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                        {painPoint.category || 'Uncategorized'}
                      </span>
                      <span className="text-xs text-gray-500">
                        Confidence: {(painPoint.confidence_score || 0).toFixed(2)}
                      </span>
                    </div>

                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {painPoint.problem_statement}
                    </h3>

                    {painPoint.problem_detail && (
                      <p className="text-gray-600 mb-3 line-clamp-2">
                        {painPoint.problem_detail}
                      </p>
                    )}

                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      {painPoint.affected_users && (
                        <div>
                          <span className="font-medium">Users:</span> {painPoint.affected_users}
                        </div>
                      )}
                      {painPoint.frequency && (
                        <div>
                          <span className="font-medium">Frequency:</span> {painPoint.frequency}
                        </div>
                      )}
                      {painPoint.market_size && (
                        <div>
                          <span className="font-medium">Market:</span> {painPoint.market_size}
                        </div>
                      )}
                      {painPoint.willingness_to_pay && (
                        <div>
                          <span className="font-medium">WTP:</span>{' '}
                          {painPoint.willingness_to_pay}
                        </div>
                      )}
                    </div>

                    {painPoint.keywords && painPoint.keywords.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {painPoint.keywords.map((keyword, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
                      <div>Source: {painPoint.source_name || 'Unknown'}</div>
                      {painPoint.content_url && (
                        <a
                          href={painPoint.content_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          View Original
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
