'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface Device {
  id: number;
  device_id: string;
  name: string;
  device_type: string;
  is_active: boolean;
  created_at: string;
}

interface EnergySummary {
  average_power_watts: number;
  max_power_watts: number;
  min_power_watts: number;
  reading_count: number;
}

interface TopConsumer {
  name: string;
  type: string;
  average_power_watts: number;
}

interface RawTopConsumer {
  name: string;
  type: string;
  average_power_watts: number | string;
}

export default function DashboardPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [energySummary, setEnergySummary] = useState<EnergySummary | null>(null);
  const [topConsumers, setTopConsumers] = useState<TopConsumer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchDashboardData();
  }, [router]);

  // Redirect if not authenticated
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      console.log('No token found in localStorage');
      router.push('/login');
      return;
    }

    console.log('Token found:', token.substring(0, 20) + '...');

    try {
      setIsLoading(true);
      
      // Fetch devices
      const devicesResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/devices/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      console.log('Devices response status:', devicesResponse.status);
      if (!devicesResponse.ok) {
        const errorText = await devicesResponse.text();
        console.error('Devices error:', errorText);
      }
      
      // Fetch energy summary
      const summaryResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/telemetry/summary`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      console.log('Summary response status:', summaryResponse.status);
      if (!summaryResponse.ok) {
        const errorText = await summaryResponse.text();
        console.error('Summary error:', errorText);
      }
      
      // Fetch top consumers
      const topConsumersResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/telemetry/top-consuming`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      console.log('Top consumers response status:', topConsumersResponse.status);
      if (!topConsumersResponse.ok) {
        const errorText = await topConsumersResponse.text();
        console.error('Top consumers error:', errorText);
      }

      if (devicesResponse.ok) {
        const devicesData = await devicesResponse.json();
        setDevices(devicesData || []);
      } else {
        console.log('No devices found or error loading devices');
        setDevices([]);
      }

      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        // Ensure all values are numbers
        setEnergySummary({
          average_power_watts: Number(summaryData.average_power_watts) || 0,
          max_power_watts: Number(summaryData.max_power_watts) || 0,
          min_power_watts: Number(summaryData.min_power_watts) || 0,
          reading_count: Number(summaryData.reading_count) || 0
        });
      } else {
        console.log('No energy summary found or error loading summary');
        setEnergySummary({
          average_power_watts: 0,
          max_power_watts: 0,
          min_power_watts: 0,
          reading_count: 0
        });
      }

      if (topConsumersResponse.ok) {
        const topConsumersData = await topConsumersResponse.json();
        // Ensure all average_power_watts values are numbers
        const safeData = (topConsumersData || []).map((consumer: RawTopConsumer): TopConsumer => ({
          ...consumer,
          average_power_watts: Number(consumer.average_power_watts) || 0
        }));
        setTopConsumers(safeData);
      } else {
        console.log('No top consumers found or error loading top consumers');
        setTopConsumers([]);
      }
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };



  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        {/* Welcome message for new users */}
        {devices.length === 0 && !isLoading && (
          <div className="bg-blue-50 border border-blue-200 text-blue-700 px-6 py-4 rounded-md mb-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">🎉</span>
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-medium">Welcome to Smart Home Energy Monitoring!</h3>
                <p className="mt-1">
                  You don't have any devices set up yet. Start by adding your first smart device to begin monitoring your energy usage.
                </p>
                <div className="mt-3">
                  <Link
                    href="/devices"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                  >
                    Add Your First Device
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Energy Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-lg">⚡</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Average Power</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {energySummary && typeof energySummary.average_power_watts === 'number' ? `${energySummary.average_power_watts.toFixed(1)} W` : 'N/A'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-lg">🔥</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Peak Power</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {energySummary && typeof energySummary.max_power_watts === 'number' ? `${energySummary.max_power_watts.toFixed(1)} W` : 'N/A'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-lg">📊</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Readings</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {energySummary && typeof energySummary.reading_count === 'number' ? energySummary.reading_count.toLocaleString() : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Devices List */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Your Devices</h2>
            </div>
            <div className="p-6">
              {devices.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No devices found</p>
              ) : (
                <div className="space-y-4">
                  {devices.map((device) => (
                    <div key={device.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div>
                        <h3 className="font-medium text-gray-900">{device.name}</h3>
                        <p className="text-sm text-gray-500">{device.device_type}</p>
                      </div>
                      <div className="flex items-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          device.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {device.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div className="mt-6">
                <Link
                  href="/devices"
                  className="w-full flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-600 bg-indigo-50 hover:bg-indigo-100"
                >
                  Manage Devices
                </Link>
              </div>
            </div>
          </div>

          {/* Top Energy Consumers */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Top Energy Consumers</h2>
            </div>
            <div className="p-6">
              {topConsumers.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No energy data available</p>
              ) : (
                <div className="space-y-4">
                  {topConsumers.map((consumer, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <span className="text-lg font-medium text-gray-500 mr-3">#{index + 1}</span>
                        <div>
                          <h3 className="font-medium text-gray-900">{consumer.name}</h3>
                          <p className="text-sm text-gray-500">{consumer.type}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">
                          {typeof consumer.average_power_watts === 'number' ? consumer.average_power_watts.toFixed(1) : 'N/A'} W
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/chat"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-lg">🤖</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="font-medium text-gray-900">Ask AI Assistant</h3>
                <p className="text-sm text-gray-500">Get energy insights</p>
              </div>
            </Link>

            <Link
              href="/devices"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-lg">🏠</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="font-medium text-gray-900">Manage Devices</h3>
                <p className="text-sm text-gray-500">Add or configure devices</p>
              </div>
            </Link>

            <button
              onClick={fetchDashboardData}
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-lg">🔄</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="font-medium text-gray-900">Refresh Data</h3>
                <p className="text-sm text-gray-500">Update dashboard</p>
              </div>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
} 