import { Link } from 'react-router-dom';

export default function TrendCard({ trend }) {
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Link to={`/trends/${trend.id}`}>
      <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow cursor-pointer">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-800 mb-2">{trend.title}</h3>
            {trend.category && (
              <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                {trend.category}
              </span>
            )}
          </div>
          {trend.rank && (
            <div className="ml-4">
              <span className="bg-yellow-400 text-yellow-900 font-bold px-3 py-1 rounded-full text-sm">
                #{trend.rank}
              </span>
            </div>
          )}
        </div>

        {trend.description && (
          <p className="text-gray-600 mb-4 line-clamp-2">{trend.description}</p>
        )}

        <div className="flex flex-wrap gap-3 text-sm text-gray-500">
          {trend.source && (
            <div className="flex items-center gap-1">
              <span className="font-medium">출처:</span>
              <span>{trend.source.name}</span>
            </div>
          )}
          {trend.collected_at && (
            <div className="flex items-center gap-1">
              <span className="font-medium">수집:</span>
              <span>{formatDate(trend.collected_at)}</span>
            </div>
          )}
        </div>

        {trend.analysis && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">분석 완료</span>
                {trend.analysis.importance_score && (
                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                    중요도: {trend.analysis.importance_score}/10
                  </span>
                )}
              </div>
              {trend.analysis.solutions && trend.analysis.solutions.length > 0 && (
                <span className="text-xs text-gray-500">
                  솔루션 {trend.analysis.solutions.length}개
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </Link>
  );
}
