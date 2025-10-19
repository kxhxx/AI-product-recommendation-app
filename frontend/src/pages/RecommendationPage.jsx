import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ProductCard from '../components/ProductCard';

const RecommendationPage = () => {
  const [messages, setMessages] = useState([
    { author: 'bot', text: "Hello! What kind of furniture are you looking for today?" }
  ]);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const recommendResponse = await axios.post(`${API_URL}/recommend`, { query: query, top_k: 3 });
    
    const userMessage = { author: 'user', text: query };
    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      // Step 1: Get recommendations from the backend
      const API_URL = "https://product-recommendation-api-r002.onrender.com";
      const recommendations = recommendResponse.data.recommendations;

      // Step 2: Generate descriptions for each recommendation
      const productsWithDescriptions = await Promise.all(
        recommendations.map(async (product) => {
          const descResponse = await axios.post(`${API_URL}/generate-description`, {            title: product.title,
            material: product.material,
            color: product.color,
          });
          return { ...product, gen_description: descResponse.data.description };
        })
      );

      const botMessage = { author: 'bot', products: productsWithDescriptions };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error("Error fetching recommendations:", error);
      const errorMessage = { author: 'bot', text: "Sorry, I encountered an error. Please try again." };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 flex flex-col h-[calc(100vh-60px)]">
      <div className="flex-grow overflow-y-auto mb-4 p-4 bg-white rounded-lg shadow-inner">
        {messages.map((msg, index) => (
          <div key={index} className={`mb-4 ${msg.author === 'user' ? 'text-right' : 'text-left'}`}>
            {msg.text && (
               <div className={`inline-block p-3 rounded-lg ${msg.author === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
                {msg.text}
               </div>
            )}
            {msg.products && (
              <div>
                <div className="inline-block p-3 rounded-lg bg-gray-200 text-gray-800 mb-2">Here are some recommendations I found for you:</div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {msg.products.map(product => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        {isLoading && <div className="text-center text-gray-500">Thinking...</div>}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="flex-shrink-0 flex">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., a modern wooden coffee table"
          className="flex-grow p-3 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="bg-blue-600 text-white p-3 rounded-r-lg hover:bg-blue-700 disabled:bg-blue-300"
          disabled={isLoading}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default RecommendationPage;