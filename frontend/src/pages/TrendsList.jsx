import { useState, useEffect } from 'react';
import { api } from '../services/api';
import TrendCard from '../components/TrendCard';

export default function TrendsList() {
  const [trends, setTrends] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(10);
  const [analyzedOnly, setAnalyzedOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrends();
  }, [page, analyzedOnly]);

  const loadTrends = async () => {
    try {
      setLoading(true);
      const data = await api.getTrends({
        page,
        per_page: perPage,
        analyzed_only: analyzedOnly,
      });
      setTrends(data.trends);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to load trends:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">트렌드 목록</h1>

          {/* Filter */}
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={analyzedOnly}
                onChange={(e) => {
                  setAnalyzedOnly(e.target.checked);
                  setPage(1);
                }}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-gray-700">분석 완료된 항목만 보기</span>
            </label>
            <span className="text-gray-500 text-sm ml-auto">
              총 {total}개의 트렌드
            </span>
          </div>
        </div>

        {/* Trends Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-2xl text-gray-600">Loading...</div>
          </div>
        ) : trends.length > 0 ? (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {trends.map((trend) => (
                <TrendCard key={trend.id} trend={trend} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 bg-white rounded-lg shadow disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  이전
                </button>

                <div className="flex gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1)
                    .filter(p => {
                      if (totalPages <= 7) return true;
                      if (p === 1 || p === totalPages) return true;
                      if (p >= page - 1 && p <= page + 1) return true;
                      return false;
                    })
                    .map((p, idx, arr) => {
                      if (idx > 0 && arr[idx - 1] !== p - 1) {
                        return [
                          <span key={`ellipsis-${p}`} className="px-2 py-2">...</span>,
                          <button
                            key={p}
                            onClick={() => setPage(p)}
                            className={`px-4 py-2 rounded-lg ${
                              page === p
                                ? 'bg-blue-600 text-white'
                                : 'bg-white hover:bg-gray-50'
                            }`}
                          >
                            {p}
                          </button>
                        ];
                      }
                      return (
                        <button
                          key={p}
                          onClick={() => setPage(p)}
                          className={`px-4 py-2 rounded-lg ${
                            page === p
                              ? 'bg-blue-600 text-white'
                              : 'bg-white hover:bg-gray-50'
                          }`}
                        >
                          {p}
                        </button>
                      );
                    })}
                </div>

                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 bg-white rounded-lg shadow disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  다음
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">트렌드 데이터가 없습니다.</p>
          </div>
        )}
      </div>
    </div>
  );
}
