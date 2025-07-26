'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    setIsLoading(false);
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    router.push('/');
  };

  const isActive = (path: string) => {
    return pathname === path;
  };

  // Don't show navbar on login/register pages
  if (pathname === '/login' || pathname === '/register') {
    return null;
  }

  // Show loading state
  if (isLoading) {
    return null;
  }

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center">
            <Link href="/" className="text-2xl font-bold text-indigo-600">
              🏠 Smart Home Energy Monitor
            </Link>
          </div>
          
          <div className="flex space-x-8">
            {isAuthenticated ? (
              // Authenticated user navigation
              <>
                <Link 
                  href="/dashboard" 
                  className={`text-sm font-medium ${
                    isActive('/dashboard') 
                      ? 'text-indigo-600' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Dashboard
                </Link>
                <Link 
                  href="/devices" 
                  className={`text-sm font-medium ${
                    isActive('/devices') 
                      ? 'text-indigo-600' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Devices
                </Link>
                <Link 
                  href="/chat" 
                  className={`text-sm font-medium ${
                    isActive('/chat') 
                      ? 'text-indigo-600' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  AI Assistant
                </Link>
                <button
                  onClick={handleLogout}
                  className="text-sm font-medium text-gray-500 hover:text-gray-700"
                >
                  Logout
                </button>
              </>
            ) : (
              // Unauthenticated user navigation (landing page)
              <>
                <Link 
                  href="/login"
                  className="text-indigo-600 hover:text-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Login
                </Link>
                <Link 
                  href="/register"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
