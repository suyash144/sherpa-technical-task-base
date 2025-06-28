import { SourceReference } from "../types";

interface SourcesTableProps {
  sources: SourceReference[];
}

export function SourcesTable({ sources }: SourcesTableProps) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
      <div className="bg-gray-100 px-4 py-2 border-b border-gray-200">
        <h4 className="text-sm font-medium text-gray-700">Sources</h4>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left font-medium text-gray-700">Document</th>
              <th className="px-4 py-2 text-left font-medium text-gray-700">Page</th>
              <th className="px-4 py-2 text-left font-medium text-gray-700">Relevance</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sources.map((source, index) => (
              <tr key={`${source.document_id}-${source.page}-${index}`} className="hover:bg-gray-50">
                <td className="px-4 py-2 text-gray-900">  
                  <div className="max-w-xs truncate" title={source.filename}>  
                    {source.url ? (  
                      <a   
                        href={source.url}   
                        target="_blank"   
                        rel="noopener noreferrer"  
                        className="text-blue-600 hover:text-blue-800 underline"  
                      >  
                        {source.filename}  
                      </a>  
                    ) : (  
                      source.filename  
                    )}  
                  </div>  
                </td>
                <td className="px-4 py-2 text-gray-700">{source.page}</td>
                <td className="px-4 py-2 text-gray-700">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {source.relevance_score.toFixed(2)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 