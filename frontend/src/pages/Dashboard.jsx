import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import StatCard from '../components/StatCard';
import TrendCard from '../components/TrendCard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [dailyStats, setDailyStats] = useState([]);
  const [latestTrends, setLatestTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewData, dailyData, trendsData] = await Promise.all([
        api.getOverviewStats(),
        api.getDailyStats(),
        api.getLatestTrends(),
      ]);

      setStats(overviewData);
      setDailyStats(dailyData);
      setLatestTrends(trendsData.trends);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-2xl text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">Trend-Flow Dashboard</h1>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="총 트렌드"
            value={stats?.total_trends || 0}
            icon="📊"
            color="blue"
          />
          <StatCard
            title="분석 완료"
            value={stats?.analyzed_trends || 0}
            icon="✓"
            color="green"
          />
          <StatCard
            title="솔루션"
            value={stats?.total_solutions || 0}
            icon="💡"
            color="purple"
          />
          <StatCard
            title="평균 중요도"
            value={stats?.avg_importance ? stats.avg_importance.toFixed(1) : 'N/A'}
            icon="⭐"
            color="orange"
          />
        </div>

        {/* Daily Stats Chart */}
        {dailyStats && dailyStats.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">일별 통계</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dailyStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="trend_count" stroke="#3b82f6" name="수집된 트렌드" />
                <Line type="monotone" dataKey="analyzed_count" stroke="#10b981" name="분석 완료" />
                <Line type="monotone" dataKey="solution_count" stroke="#8b5cf6" name="생성된 솔루션" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Latest Trends */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">최근 트렌드</h2>
            <Link to="/trends" className="text-blue-600 hover:text-blue-800 font-medium">
              전체 보기 →
            </Link>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {latestTrends && latestTrends.length > 0 ? (
              latestTrends.map((trend) => (
                <TrendCard key={trend.id} trend={trend} />
              ))
            ) : (
              <p className="text-gray-500 col-span-2">트렌드 데이터가 없습니다.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
