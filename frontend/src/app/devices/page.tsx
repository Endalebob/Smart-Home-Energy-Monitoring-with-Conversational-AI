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

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    device_type: ''
  });
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchDevices();
  }, [router]);

  // Redirect if not authenticated
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const fetchDevices = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      setIsLoading(true);
      setError('');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/devices/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setDevices(data || []);
      } else {
        console.log('No devices found or error loading devices');
        setDevices([]);
        // Don't show error for empty devices - this is normal for new users
        if (response.status !== 404) {
          setError('Failed to load devices');
        }
      }
    } catch (err) {
      console.error('Error fetching devices:', err);
      setDevices([]);
      setError('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/devices/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setFormData({ name: '', device_type: '' });
        setShowAddForm(false);
        fetchDevices();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create device');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleUpdate = async (deviceId: string) => {
    const token = localStorage.getItem('token');
    if (!token || !editingDevice) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/devices/${deviceId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: editingDevice.name,
          device_type: editingDevice.device_type,
          is_active: editingDevice.is_active
        }),
      });

      if (response.ok) {
        setEditingDevice(null);
        fetchDevices();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update device');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleDelete = async (deviceId: string) => {
    if (!confirm('Are you sure you want to delete this device?')) return;

    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/devices/${deviceId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        fetchDevices();
      } else {
        setError('Failed to delete device');
      }
    } catch (err) {
      setError('Network error');
    }
  };



  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading devices...</p>
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

        {/* Page Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Device Management</h2>
            <p className="mt-2 text-gray-600">Manage your smart home devices and monitor their energy usage</p>
          </div>
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            Add Device
          </button>
        </div>

        {/* Add Device Form */}
        {showAddForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Device</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Device Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    required
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>
                <div>
                  <label htmlFor="device_type" className="block text-sm font-medium text-gray-700">
                    Device Type
                  </label>
                  <select
                    id="device_type"
                    name="device_type"
                    required
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    value={formData.device_type}
                    onChange={(e) => setFormData({ ...formData, device_type: e.target.value })}
                  >
                    <option value="">Select type</option>
                    <option value="refrigerator">Refrigerator</option>
                    <option value="air_conditioner">Air Conditioner</option>
                    <option value="television">Television</option>
                    <option value="appliance">Appliance</option>
                    <option value="lighting">Lighting</option>
                    <option value="heating">Heating</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              <div className="flex space-x-4">
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Add Device
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-md text-sm font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Devices List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Your Devices ({devices.length})</h3>
          </div>
          <div className="p-6">
            {devices.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">🏠</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No devices yet</h3>
                <p className="text-gray-500 mb-4">Add your first smart home device to start monitoring energy usage</p>
                <button
                  onClick={() => setShowAddForm(true)}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Add Your First Device
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {devices.map((device) => (
                  <div key={device.id} className="border border-gray-200 rounded-lg p-4">
                    {editingDevice?.id === device.id ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <input
                            type="text"
                            value={editingDevice.name}
                            onChange={(e) => setEditingDevice({ ...editingDevice, name: e.target.value })}
                            className="border border-gray-300 rounded-md px-3 py-2"
                          />
                          <select
                            value={editingDevice.device_type}
                            onChange={(e) => setEditingDevice({ ...editingDevice, device_type: e.target.value })}
                            className="border border-gray-300 rounded-md px-3 py-2"
                          >
                            <option value="refrigerator">Refrigerator</option>
                            <option value="air_conditioner">Air Conditioner</option>
                            <option value="television">Television</option>
                            <option value="appliance">Appliance</option>
                            <option value="lighting">Lighting</option>
                            <option value="heating">Heating</option>
                            <option value="other">Other</option>
                          </select>
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              checked={editingDevice.is_active}
                              onChange={(e) => setEditingDevice({ ...editingDevice, is_active: e.target.checked })}
                              className="mr-2"
                            />
                            Active
                          </label>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleUpdate(device.device_id)}
                            className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingDevice(null)}
                            className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-3 py-1 rounded text-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="flex-shrink-0">
                            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                              <span className="text-indigo-600 text-lg">
                                {device.device_type === 'refrigerator' ? '❄️' :
                                 device.device_type === 'air_conditioner' ? '❄️' :
                                 device.device_type === 'television' ? '📺' :
                                 device.device_type === 'appliance' ? '🔌' :
                                 device.device_type === 'lighting' ? '💡' :
                                 device.device_type === 'heating' ? '🔥' : '🏠'}
                              </span>
                            </div>
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900">{device.name}</h4>
                            <p className="text-sm text-gray-500 capitalize">{device.device_type.replace('_', ' ')}</p>
                            <p className="text-xs text-gray-400">ID: {device.device_id}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            device.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {device.is_active ? 'Active' : 'Inactive'}
                          </span>
                          <button
                            onClick={() => setEditingDevice(device)}
                            className="text-indigo-600 hover:text-indigo-500 text-sm"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(device.device_id)}
                            className="text-red-600 hover:text-red-500 text-sm"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
} 