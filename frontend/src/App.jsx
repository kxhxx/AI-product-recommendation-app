import { BrowserRouter as Router, Routes, Route, Link, NavLink } from 'react-router-dom';
import RecommendationPage from './pages/RecommendationPage';
import AnalyticsPage from './pages/AnalyticsPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100 font-sans">
        <nav className="bg-white shadow-md">
          <div className="max-w-4xl mx-auto px-4">
            <div className="flex justify-between items-center py-3">
              <Link to="/" className="text-2xl font-bold text-gray-800">
                FurnitureAI
              </Link>
              <div className="flex space-x-4">
                <NavLink
                  to="/"
                  className={({ isActive }) =>
                    isActive ? "text-blue-600 font-semibold" : "text-gray-500 hover:text-blue-600"
                  }
                >
                  Recommendations
                </NavLink>
                <NavLink
                  to="/analytics"
                  className={({ isActive }) =>
                    isActive ? "text-blue-600 font-semibold" : "text-gray-500 hover:text-blue-600"
                  }
                >
                  Analytics
                </NavLink>
              </div>
            </div>
          </div>
        </nav>
        <main>
          <Routes>
            <Route path="/" element={<RecommendationPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;