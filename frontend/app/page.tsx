'use client'

import { useState, FormEvent, ChangeEvent } from 'react';

// Define the type for the API response from your Python backend
interface ApiResponse {
  response: string; // The answer from the RAG system
  // We can assume your Python API returns JSON like: {"response": "The answer..."}
}

// The main component for the chat interface
export default function HomePage() {
  const [query, setQuery] = useState<string>('');
  const [response, setResponse] = useState<string>('Ask a question about HMRC Corporation Tax (e.g., "What is the R&D tax relief deadline?").');
  const [loading, setLoading] = useState<boolean>(false);

  // Use FormEvent for the form submission
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResponse('Querying HMRC knowledge base...');

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // Send the user's question in a JSON body
        body: JSON.stringify({ query }),
      });

      // The 'as ApiResponse' tells TypeScript what shape the data should be
      const data: ApiResponse = await res.json() as ApiResponse;
      
      if (res.ok) {
        setResponse(data.response);
      } else {
        // Handle server-side errors, assuming the error is in the 'response' field or an 'error' field
        setResponse(`Error: ${data.response || 'Failed to get a response from the server.'}`);
      }
    } catch (error) {
      console.error('Fetch error:', error);
      setResponse('Network Error: Could not connect to the local API.');
    } finally {
      setLoading(false);
      setQuery(''); // Clear the input field
    }
  };

  // Use ChangeEvent for the input field
  const handleQueryChange = (e: ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-50">
      <div className="w-full max-w-2xl bg-white p-8 rounded-xl shadow-2xl">
        
        {/* Title and Description */}
        <h1 className="text-3xl font-bold mb-2 text-center text-blue-800">HMRC RAG Assistant 🇬🇧</h1>
        <p className="text-center text-gray-500 mb-8">Ask any question about the provided Corporation Tax documents.</p>
        
        {/* Response Area */}
        <div className="bg-gray-100 p-4 rounded-lg min-h-[150px] shadow-inner mb-6">
          <p className="font-semibold text-gray-700 mb-2">AI Response:</p>
          <p className="text-gray-900 whitespace-pre-wrap">{response}</p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex gap-4">
          <input
            type="text"
            value={query}
            onChange={handleQueryChange}
            placeholder="E.g., What is the main rate of Corporation Tax?"
            disabled={loading}
            className="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-200"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white font-medium py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-blue-300 transition duration-150"
          >
            {loading ? 'Sending...' : 'Ask'}
          </button>
        </form>
      </div>
    </main>
  );
}