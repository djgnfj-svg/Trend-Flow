export default function SolutionCard({ solution }) {
  const feasibilityColors = {
    high: "bg-green-100 text-green-800",
    medium: "bg-yellow-100 text-yellow-800",
    low: "bg-red-100 text-red-800",
  };

  const effortColors = {
    low: "bg-green-100 text-green-800",
    medium: "bg-yellow-100 text-yellow-800",
    high: "bg-red-100 text-red-800",
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <h4 className="text-lg font-bold text-gray-800 mb-3">{solution.title}</h4>

      <p className="text-gray-600 mb-4">{solution.description}</p>

      <div className="flex flex-wrap gap-2 mb-4">
        {solution.feasibility && (
          <span className={`text-xs px-2 py-1 rounded ${feasibilityColors[solution.feasibility] || 'bg-gray-100 text-gray-800'}`}>
            실현가능성: {solution.feasibility}
          </span>
        )}
        {solution.estimated_effort && (
          <span className={`text-xs px-2 py-1 rounded ${effortColors[solution.estimated_effort] || 'bg-gray-100 text-gray-800'}`}>
            예상작업: {solution.estimated_effort}
          </span>
        )}
      </div>

      {solution.target_audience && (
        <div className="mb-3">
          <span className="text-sm font-medium text-gray-700">타겟: </span>
          <span className="text-sm text-gray-600">{solution.target_audience}</span>
        </div>
      )}

      {solution.tech_stack && solution.tech_stack.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {solution.tech_stack.map((tech, index) => (
            <span key={index} className="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded">
              {tech}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
