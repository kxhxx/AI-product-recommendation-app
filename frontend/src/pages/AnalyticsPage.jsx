import React from 'react';
import priceDistributionImg from '../assets/price_distribution.png';
import topBrandsImg from '../assets/top_brands.png';
import topMaterialsImg from '../assets/top_materials.png';

const AnalyticsPage = () => {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
        Furniture Dataset Analytics
      </h1>
      <div className="space-y-8">
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4 text-center">Product Price Distribution</h2>
          <img src={priceDistributionImg} alt="Price Distribution" className="mx-auto rounded-md" />
          <p className="text-center text-gray-600 mt-2">
            This histogram shows the frequency of products across different price points.
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4 text-center">Top 10 Brands by Product Count</h2>
          <img src={topBrandsImg} alt="Top Brands" className="mx-auto rounded-md" />
            <p className="text-center text-gray-600 mt-2">
            This chart highlights the brands with the most products available in our dataset.
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4 text-center">Top 10 Most Common Materials</h2>
          <img src={topMaterialsImg} alt="Top Materials" className="mx-auto rounded-md" />
            <p className="text-center text-gray-600 mt-2">
            This chart displays the most frequently used materials in the furniture products.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;