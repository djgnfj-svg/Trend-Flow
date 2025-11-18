import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ideasApi } from '../services/painPointApi';

export default function SaaSIdeasList() {
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    min_score: '',
    business_model: '',
    complexity: '',
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('overall_score'); // overall_score, validation_score, created_at
  const [filteredAndSortedIdeas, setFilteredAndSortedIdeas] = useState([]);

  useEffect(() => {
    loadIdeas();
  }, [filters]);

  // Filter and sort ideas client-side
  useEffect(() => {
    let result = [...ideas];

    // Search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      result = result.filter(
        (idea) =>
          idea.title?.toLowerCase().includes(search) ||
          idea.description?.toLowerCase().includes(search) ||
          idea.problem_statement?.toLowerCase().includes(search)
      );
    }

    // Sort
    result.sort((a, b) => {
      if (sortBy === 'overall_score') {
        return (b.overall_score || 0) - (a.overall_score || 0);
      } else if (sortBy === 'validation_score') {
        return (b.validation_score || 0) - (a.validation_score || 0);
      } else if (sortBy === 'created_at') {
        return new Date(b.created_at) - new Date(a.created_at);
      }
      return 0;
    });

    setFilteredAndSortedIdeas(result);
  }, [ideas, searchTerm, sortBy]);

  const loadIdeas = async () => {
    try {
      setLoading(true);
      const data = await ideasApi.getAll(filters);
      setIdeas(data);
    } catch (error) {
      console.error('Failed to load ideas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-blue-600';
    if (score >= 4) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const complexityColors = {
    simple: 'bg-green-100 text-green-800',
    moderate: 'bg-yellow-100 text-yellow-800',
    complex: 'bg-red-100 text-red-800',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SaaS Ideas</h1>
              <p className="mt-2 text-sm text-gray-600">
                AI가 생성한 실행 가능한 비즈니스 아이디어
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
        {/* Search and Sort */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by title, description, or problem..."
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sort By
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="overall_score">Overall Score (High to Low)</option>
                <option value="validation_score">Validation Score (High to Low)</option>
                <option value="created_at">Recently Added</option>
              </select>
            </div>
          </div>

          <h2 className="text-lg font-semibold mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Score
              </label>
              <select
                value={filters.min_score}
                onChange={(e) => handleFilterChange('min_score', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">All</option>
                <option value="8">8+ (Excellent)</option>
                <option value="6">6+ (Good)</option>
                <option value="4">4+ (Fair)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Business Model
              </label>
              <select
                value={filters.business_model}
                onChange={(e) => handleFilterChange('business_model', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">All</option>
                <option value="subscription">Subscription</option>
                <option value="freemium">Freemium</option>
                <option value="one-time">One-time</option>
                <option value="usage-based">Usage-based</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Complexity
              </label>
              <select
                value={filters.complexity}
                onChange={(e) => handleFilterChange('complexity', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">All</option>
                <option value="simple">Simple</option>
                <option value="moderate">Moderate</option>
                <option value="complex">Complex</option>
              </select>
            </div>
          </div>
        </div>

        {/* Ideas List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="text-lg text-gray-600">Loading...</div>
          </div>
        ) : filteredAndSortedIdeas.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-gray-400 text-lg">
              {searchTerm ? `No ideas found matching "${searchTerm}"` : 'No ideas found'}
            </div>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Clear Search
              </button>
            )}
          </div>
        ) : (
          <div>
            <div className="mb-4 text-sm text-gray-600">
              Showing {filteredAndSortedIdeas.length} of {ideas.length} ideas
            </div>
            <div className="space-y-6">
              {filteredAndSortedIdeas.map((idea) => (
              <Link
                key={idea.id}
                to={`/saas-ideas/${idea.id}`}
                className="block bg-white rounded-lg shadow hover:shadow-xl transition p-6"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Header */}
                    <div className="flex items-start gap-4 mb-3">
                      <div className="flex-1">
                        <h3 className="text-2xl font-bold text-gray-900 mb-1">{idea.title}</h3>
                        {idea.tagline && (
                          <p className="text-lg text-gray-600 italic">{idea.tagline}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <div className={`text-4xl font-bold ${getScoreColor(idea.overall_score)}`}>
                          {idea.overall_score}
                          <span className="text-lg text-gray-500">/10</span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">Overall Score</div>
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-gray-700 mb-4 line-clamp-3">{idea.description}</p>

                    {/* Pain Point */}
                    {idea.problem_statement && (
                      <div className="bg-red-50 border-l-4 border-red-400 p-3 mb-4">
                        <div className="text-xs font-semibold text-red-800 mb-1">
                          PAIN POINT
                        </div>
                        <div className="text-sm text-red-700">{idea.problem_statement}</div>
                      </div>
                    )}

                    {/* Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                        {idea.business_model}
                      </span>
                      <span
                        className={`px-3 py-1 rounded-full text-sm ${
                          complexityColors[idea.complexity] || 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {idea.complexity}
                      </span>
                      <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                        {idea.estimated_dev_time}
                      </span>
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                        {idea.estimated_monthly_revenue}
                      </span>
                    </div>

                    {/* Scores */}
                    <div className="flex gap-6 text-sm mb-4">
                      <div>
                        <span className="text-gray-600">Feasibility:</span>
                        <span className="ml-2 font-semibold">{idea.feasibility_score}/10</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Market:</span>
                        <span className="ml-2 font-semibold">{idea.market_score}/10</span>
                      </div>
                      {idea.competition_level && (
                        <div>
                          <span className="text-gray-600">Competition:</span>
                          <span className="ml-2 font-semibold capitalize">
                            {idea.competition_level}
                          </span>
                        </div>
                      )}
                      {idea.validation_score && (
                        <div>
                          <span className="text-gray-600">Validation:</span>
                          <span className={`ml-2 font-semibold ${
                            idea.validation_score >= 8 ? 'text-green-600' :
                            idea.validation_score >= 6 ? 'text-blue-600' :
                            idea.validation_score >= 4 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {idea.validation_score}/10
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Market Status Badge */}
                    {idea.market_status && (
                      <div className="mb-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          idea.market_status === 'blue_ocean' ? 'bg-blue-100 text-blue-800' :
                          idea.market_status === 'growing' ? 'bg-green-100 text-green-800' :
                          idea.market_status === 'competitive' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {idea.market_status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                    )}

                    {/* MVP Features */}
                    {idea.mvp_features && idea.mvp_features.length > 0 && (
                      <div className="mb-4">
                        <div className="text-sm font-semibold text-gray-700 mb-2">MVP Features:</div>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          {idea.mvp_features.slice(0, 3).map((feature, idx) => (
                            <li key={idx}>{feature}</li>
                          ))}
                          {idea.mvp_features.length > 3 && (
                            <li className="text-gray-400">
                              +{idea.mvp_features.length - 3} more...
                            </li>
                          )}
                        </ul>
                      </div>
                    )}

                    {/* Tech Stack */}
                    {idea.tech_stack && idea.tech_stack.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        <span className="text-sm text-gray-600">Tech:</span>
                        {idea.tech_stack.map((tech, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
