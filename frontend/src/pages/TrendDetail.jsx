import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import SolutionCard from '../components/SolutionCard';

export default function TrendDetail() {
  const { id } = useParams();
  const [trend, setTrend] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrend();
  }, [id]);

  const loadTrend = async () => {
    try {
      setLoading(true);
      const data = await api.getTrendById(id);
      setTrend(data);
    } catch (error) {
      console.error('Failed to load trend:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-2xl text-gray-600">Loading...</div>
      </div>
    );
  }

  if (!trend) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-gray-500 text-lg mb-4">트렌드를 찾을 수 없습니다.</p>
            <Link to="/trends" className="text-blue-600 hover:text-blue-800">
              목록으로 돌아가기
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <Link to="/trends" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-6">
          ← 목록으로 돌아가기
        </Link>

        {/* Trend Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-800 mb-4">{trend.title}</h1>
              <div className="flex flex-wrap gap-2 mb-4">
                {trend.category && (
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded">
                    {trend.category}
                  </span>
                )}
                {trend.rank && (
                  <span className="bg-yellow-400 text-yellow-900 font-bold px-3 py-1 rounded">
                    #{trend.rank}
                  </span>
                )}
              </div>
            </div>
          </div>

          {trend.description && (
            <p className="text-gray-700 text-lg mb-6">{trend.description}</p>
          )}

          <div className="grid grid-cols-2 gap-4 text-sm border-t pt-4">
            {trend.source && (
              <div>
                <span className="font-medium text-gray-700">출처:</span>
                <span className="ml-2 text-gray-600">{trend.source.name}</span>
              </div>
            )}
            {trend.collected_at && (
              <div>
                <span className="font-medium text-gray-700">수집 시간:</span>
                <span className="ml-2 text-gray-600">{formatDate(trend.collected_at)}</span>
              </div>
            )}
            {trend.url && (
              <div className="col-span-2">
                <span className="font-medium text-gray-700">URL:</span>
                <a
                  href={trend.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-2 text-blue-600 hover:text-blue-800 break-all"
                >
                  {trend.url}
                </a>
              </div>
            )}
          </div>
        </div>

        {/* Analysis Section */}
        {trend.analysis ? (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">분석 결과</h2>

              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">요약</h3>
                <p className="text-gray-600">{trend.analysis.summary}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                {trend.analysis.sentiment && (
                  <div>
                    <span className="font-medium text-gray-700">감정 분석:</span>
                    <span className="ml-2 text-gray-600">{trend.analysis.sentiment}</span>
                  </div>
                )}
                {trend.analysis.importance_score && (
                  <div>
                    <span className="font-medium text-gray-700">중요도:</span>
                    <span className="ml-2 font-bold text-orange-600">
                      {trend.analysis.importance_score}/10
                    </span>
                  </div>
                )}
              </div>

              {trend.analysis.problems && trend.analysis.problems.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">발견된 문제점</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {trend.analysis.problems.map((problem, idx) => (
                      <li key={idx} className="text-gray-600">{problem}</li>
                    ))}
                  </ul>
                </div>
              )}

              {trend.analysis.keywords && trend.analysis.keywords.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">키워드</h3>
                  <div className="flex flex-wrap gap-2">
                    {trend.analysis.keywords.map((keyword, idx) => (
                      <span key={idx} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Solutions */}
            {trend.analysis.solutions && trend.analysis.solutions.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-4">제안된 솔루션</h2>
                <div className="grid grid-cols-1 gap-6">
                  {trend.analysis.solutions.map((solution) => (
                    <SolutionCard key={solution.id} solution={solution} />
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-gray-500">이 트렌드는 아직 분석되지 않았습니다.</p>
          </div>
        )}
      </div>
    </div>
  );
}
