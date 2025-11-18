import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { painPointsApi, ideasApi } from '../services/painPointApi';

export default function PainPointsDashboard() {
  const [stats, setStats] = useState(null);
  const [topIdeas, setTopIdeas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [painPointStats, ideaStats, topIdeasData] = await Promise.all([
        painPointsApi.getStats(),
        ideasApi.getStats(),
        ideasApi.getTop(5),
      ]);

      setStats({
        painPoints: painPointStats,
        ideas: ideaStats,
      });
      setTopIdeas(topIdeasData);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  const severityColors = {
    critical: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Pain Point Finder</h1>
          <p className="mt-2 text-sm text-gray-600">
            실제 사용자 문제점을 발굴하고 SaaS 아이디어를 자동 생성합니다
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation */}
        <div className="mb-8 flex gap-4">
          <Link
            to="/pain-points"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Pain Points
          </Link>
          <Link
            to="/saas-ideas"
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            SaaS Ideas
          </Link>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Pain Points Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Total Pain Points</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {stats?.painPoints?.total_pain_points || 0}
            </div>
            <div className="mt-2 text-xs text-gray-500">
              Avg Confidence: {(stats?.painPoints?.avg_confidence || 0).toFixed(2)}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Critical Issues</div>
            <div className="mt-2 text-3xl font-bold text-red-600">
              {stats?.painPoints?.critical_count || 0}
            </div>
            <div className="mt-2 text-xs text-gray-500">
              High: {stats?.painPoints?.high_count || 0}
            </div>
          </div>

          {/* Ideas Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Total Ideas</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {stats?.ideas?.total_ideas || 0}
            </div>
            <div className="mt-2 text-xs text-gray-500">
              Avg Score: {(stats?.ideas?.avg_score || 0).toFixed(1)}/10
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">High Score Ideas</div>
            <div className="mt-2 text-3xl font-bold text-green-600">
              {stats?.ideas?.high_score_count || 0}
            </div>
            <div className="mt-2 text-xs text-gray-500">Score 8+</div>
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">Pain Point Severity Distribution</h2>
          <div className="flex gap-4">
            {['critical', 'high', 'medium', 'low'].map((severity) => (
              <div key={severity} className="flex-1">
                <div className={`${severityColors[severity]} rounded-lg p-4 text-center`}>
                  <div className="text-2xl font-bold">
                    {stats?.painPoints?.[`${severity}_count`] || 0}
                  </div>
                  <div className="text-sm capitalize">{severity}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Ideas */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold">Top 5 SaaS Ideas</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {topIdeas.length > 0 ? (
              topIdeas.map((idea, index) => (
                <Link
                  key={idea.id}
                  to={`/saas-ideas/${idea.id}`}
                  className="block px-6 py-4 hover:bg-gray-50 transition"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl font-bold text-gray-400">#{index + 1}</span>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{idea.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{idea.tagline}</p>
                          <p className="text-sm text-gray-500 mt-2 line-clamp-2">
                            {idea.problem_statement}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-3 mt-3 text-xs">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                          {idea.business_model}
                        </span>
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded">
                          {idea.complexity}
                        </span>
                        <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded">
                          {idea.estimated_dev_time}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4 flex flex-col items-end">
                      <div className="text-3xl font-bold text-green-600">
                        {idea.overall_score}
                        <span className="text-sm text-gray-500">/10</span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Feasibility: {idea.feasibility_score}
                      </div>
                      <div className="text-xs text-gray-500">Market: {idea.market_score}</div>
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className="px-6 py-8 text-center text-gray-500">No ideas yet</div>
            )}
          </div>
        </div>

        {/* Complexity Distribution */}
        {stats?.ideas && (
          <div className="bg-white rounded-lg shadow p-6 mt-8">
            <h2 className="text-lg font-semibold mb-4">Complexity Distribution</h2>
            <div className="flex gap-4">
              <div className="flex-1 bg-green-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-600">
                  {stats.ideas.simple_count}
                </div>
                <div className="text-sm text-gray-600">Simple</div>
              </div>
              <div className="flex-1 bg-yellow-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {stats.ideas.moderate_count}
                </div>
                <div className="text-sm text-gray-600">Moderate</div>
              </div>
              <div className="flex-1 bg-red-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-600">
                  {stats.ideas.complex_count}
                </div>
                <div className="text-sm text-gray-600">Complex</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
