'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
            Monitor Your Home's
            <span className="text-indigo-600"> Energy Usage</span>
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Track energy consumption in real-time, get insights from conversational AI, 
            and optimize your smart home devices for better efficiency.
          </p>
          <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
            <div className="rounded-md shadow">
              <Link
                href="/register"
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10"
              >
                Start Monitoring
              </Link>
            </div>
            <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
              <Link
                href="/login"
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-20">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {/* Real-time Monitoring */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-lg">📊</span>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">Real-time Monitoring</h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Track energy consumption of all your smart devices in real-time with detailed analytics.
                  </p>
                </div>
              </div>
            </div>

            {/* Conversational AI */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-lg">🤖</span>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">AI Assistant</h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Ask natural language questions about your energy usage and get intelligent insights.
                  </p>
                </div>
              </div>
            </div>

            {/* Device Management */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-lg">🏠</span>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">Smart Device Management</h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Manage all your smart home devices from one centralized dashboard.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Example Queries */}
        <div className="mt-20 bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Ask Your AI Assistant
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Energy Usage Queries</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• "How much energy did my fridge use yesterday?"</li>
                <li>• "Which devices are using the most power?"</li>
                <li>• "Show me my energy summary for today"</li>
                <li>• "Compare energy usage between my devices"</li>
              </ul>
            </div>
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Device Management</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• "List my devices"</li>
                <li>• "What's the power consumption of my AC?"</li>
                <li>• "Show me the most efficient devices"</li>
                <li>• "How much energy did I use last month?"</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 mt-20">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-base text-gray-400">
              © 2024 Smart Home Energy Monitor. Built with Next.js and FastAPI.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
