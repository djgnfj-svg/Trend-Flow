import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ideasApi } from '../services/painPointApi';

export default function IdeaDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [idea, setIdea] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIdea();
  }, [id]);

  const loadIdea = async () => {
    try {
      setLoading(true);
      const data = await ideasApi.getDetail(id);
      setIdea(data);
    } catch (error) {
      console.error('Failed to load idea:', error);
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

  if (!idea) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-lg text-gray-600 mb-4">Idea not found</div>
          <button
            onClick={() => navigate('/saas-ideas')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Ideas
          </button>
        </div>
      </div>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-blue-600';
    if (score >= 4) return 'text-yellow-600';
    return 'text-gray-600';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate('/saas-ideas')}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back to Ideas
            </button>
            <Link to="/" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Title & Score */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">{idea.title}</h1>
              {idea.tagline && <p className="text-xl text-gray-600 italic">{idea.tagline}</p>}
            </div>
            <div className="text-center">
              <div className={`text-6xl font-bold ${getScoreColor(idea.overall_score)}`}>
                {idea.overall_score}
                <span className="text-2xl text-gray-500">/10</span>
              </div>
              <div className="text-sm text-gray-500 mt-2">Overall Score</div>
            </div>
          </div>

          {/* Scores Grid */}
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-blue-600">{idea.feasibility_score}</div>
              <div className="text-sm text-gray-600 mt-1">Feasibility</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-green-600">{idea.market_score}</div>
              <div className="text-sm text-gray-600 mt-1">Market Potential</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="text-sm font-semibold text-purple-800 capitalize">
                {idea.competition_level || 'Unknown'}
              </div>
              <div className="text-sm text-gray-600 mt-1">Competition</div>
            </div>
          </div>
        </div>

        {/* Pain Point */}
        <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-6 mb-6">
          <h2 className="text-lg font-bold text-red-900 mb-2">Pain Point</h2>
          <p className="text-red-800 text-lg mb-3">{idea.problem_statement}</p>
          {idea.problem_detail && (
            <p className="text-red-700 text-sm">{idea.problem_detail}</p>
          )}

          {/* Pain Point Details */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
            {idea.affected_users && (
              <div>
                <div className="text-red-900 font-semibold">Affected Users</div>
                <div className="text-red-700">{idea.affected_users}</div>
              </div>
            )}
            {idea.severity && (
              <div>
                <div className="text-red-900 font-semibold">Severity</div>
                <div className="text-red-700 capitalize">{idea.severity}</div>
              </div>
            )}
            {idea.frequency && (
              <div>
                <div className="text-red-900 font-semibold">Frequency</div>
                <div className="text-red-700 capitalize">{idea.frequency}</div>
              </div>
            )}
            {idea.market_size && (
              <div>
                <div className="text-red-900 font-semibold">Market Size</div>
                <div className="text-red-700 capitalize">{idea.market_size}</div>
              </div>
            )}
          </div>
        </div>

        {/* Description */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Description</h2>
          <p className="text-gray-700 text-lg leading-relaxed">{idea.description}</p>
        </div>

        {/* Business Model */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Business Model</h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600">Model</div>
                <div className="text-lg font-semibold capitalize">{idea.business_model}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Pricing</div>
                <div className="text-lg font-semibold">{idea.pricing_model}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Est. Monthly Revenue</div>
                <div className="text-lg font-semibold text-green-600">
                  {idea.estimated_monthly_revenue}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Development</h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600">Complexity</div>
                <div className="text-lg font-semibold capitalize">{idea.complexity}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Est. Dev Time</div>
                <div className="text-lg font-semibold">{idea.estimated_dev_time}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Target Audience</div>
                <div className="text-lg font-semibold">{idea.target_audience}</div>
              </div>
            </div>
          </div>
        </div>

        {/* MVP */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Minimum Viable Product (MVP)</h2>
          {idea.mvp_description && (
            <p className="text-gray-700 mb-4">{idea.mvp_description}</p>
          )}

          {idea.mvp_features && idea.mvp_features.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Core Features</h3>
              <ul className="space-y-2">
                {idea.mvp_features.map((feature, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Tech Stack */}
        {idea.tech_stack && idea.tech_stack.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Tech Stack</h2>
            <div className="flex flex-wrap gap-3">
              {idea.tech_stack.map((tech, idx) => (
                <span
                  key={idx}
                  className="px-4 py-2 bg-blue-100 text-blue-800 font-semibold rounded-lg"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Market Validation */}
        {idea.validation_score && (
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg shadow-lg p-6 mb-6 border border-indigo-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900">Market Validation</h2>
              <div className="text-center">
                <div className={`text-5xl font-bold ${
                  idea.validation_score >= 8 ? 'text-green-600' :
                  idea.validation_score >= 6 ? 'text-blue-600' :
                  idea.validation_score >= 4 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {idea.validation_score}
                  <span className="text-2xl text-gray-500">/10</span>
                </div>
                <div className="text-sm text-gray-600 mt-1">Validation Score</div>
              </div>
            </div>

            {/* Market Status Badge */}
            <div className="mb-4">
              <span className={`inline-block px-4 py-2 rounded-full text-sm font-bold ${
                idea.market_status === 'blue_ocean' ? 'bg-blue-100 text-blue-800' :
                idea.market_status === 'growing' ? 'bg-green-100 text-green-800' :
                idea.market_status === 'competitive' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {idea.market_status?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
              </span>
            </div>

            {/* Validation Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-white rounded-lg p-4">
                <div className="text-sm text-gray-600">Search Volume</div>
                <div className="text-2xl font-bold text-indigo-600">
                  {idea.search_volume_score || 0}
                  <span className="text-sm text-gray-500">/100</span>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4">
                <div className="text-sm text-gray-600">Trend</div>
                <div className="text-lg font-bold capitalize">
                  <span className={
                    idea.trend_direction === 'rising' ? 'text-green-600' :
                    idea.trend_direction === 'stable' ? 'text-blue-600' :
                    'text-red-600'
                  }>
                    {idea.trend_direction || 'Unknown'}
                  </span>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4">
                <div className="text-sm text-gray-600">Competitors</div>
                <div className="text-2xl font-bold text-purple-600">
                  {idea.competitor_count || 0}
                </div>
              </div>
              <div className="bg-white rounded-lg p-4">
                <div className="text-sm text-gray-600">Saturation</div>
                <div className="text-2xl font-bold text-orange-600">
                  {idea.saturation_score || 0}
                  <span className="text-sm text-gray-500">/100</span>
                </div>
              </div>
            </div>

            {/* Recommendation */}
            {idea.recommendation && (
              <div className="bg-white rounded-lg p-4 border-l-4 border-indigo-500">
                <div className="text-sm font-semibold text-gray-700 mb-1">Recommendation</div>
                <p className="text-gray-800">{idea.recommendation}</p>
              </div>
            )}

            {/* Competitors List */}
            {idea.competitors && idea.competitors.length > 0 && (
              <div className="mt-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Competitors Found</h3>
                <div className="flex flex-wrap gap-2">
                  {idea.competitors.map((competitor, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-white text-gray-700 rounded-lg text-sm border border-gray-300"
                    >
                      {competitor}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {idea.validated_at && (
              <div className="mt-3 text-xs text-gray-500">
                Validated: {new Date(idea.validated_at).toLocaleDateString()}
              </div>
            )}
          </div>
        )}

        {/* Go-to-Market */}
        {idea.go_to_market_strategy && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Go-to-Market Strategy</h2>
            <p className="text-gray-700 leading-relaxed">{idea.go_to_market_strategy}</p>
          </div>
        )}

        {/* Differentiation */}
        {idea.differentiation && (
          <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-bold text-green-900 mb-2">Competitive Advantage</h2>
            <p className="text-green-800">{idea.differentiation}</p>
          </div>
        )}

        {/* Existing Solutions */}
        {idea.existing_solutions && idea.existing_solutions.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Existing Solutions</h2>
            <div className="flex flex-wrap gap-2">
              {idea.existing_solutions.map((solution, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg"
                >
                  {solution}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Similar Products */}
        {idea.similar_products && idea.similar_products.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Similar Products</h2>
            <div className="flex flex-wrap gap-2">
              {idea.similar_products.map((product, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-purple-100 text-purple-700 rounded-lg"
                >
                  {product}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Tags */}
        {idea.tags && idea.tags.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Tags</h2>
            <div className="flex flex-wrap gap-2">
              {idea.tags.map((tag, idx) => (
                <span key={idx} className="px-3 py-1 bg-gray-200 text-gray-800 rounded-full text-sm">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Original Source */}
        {idea.original_url && (
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <a
              href={idea.original_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              View Original Source ({idea.source_name})
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
