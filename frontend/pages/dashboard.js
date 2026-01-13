/**
 * Dashboard Page - Main landing after login
 * Shows action cards and quick access to features
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { isAuthenticated } from '../services/api';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <header className="bg-secondary-900 text-white shadow-lg">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
              <span className="text-secondary-900 text-xl font-bold">SD</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">Standard Steels & Hardware</h1>
              <p className="text-sm text-secondary-300">Billing Management System</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-secondary-700 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium">
                  {user?.email?.charAt(0)?.toUpperCase() || 'A'}
                </span>
              </div>
              <span className="text-sm">Admin</span>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-secondary-700 hover:bg-secondary-600 rounded-lg text-sm font-medium transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-secondary-900 mb-2">Welcome Back!</h2>
          <p className="text-secondary-600">Select an action to get started</p>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Create New Invoice */}
          <div
            onClick={() => router.push('/invoices/create')}
            className="bg-white rounded-lg shadow-md p-8 hover:shadow-xl transition-shadow cursor-pointer border border-secondary-100"
          >
            <div className="w-16 h-16 bg-secondary-900 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-secondary-900 mb-2">Create New Invoice</h3>
            <p className="text-secondary-600 text-sm">
              Generate billing and invoices for customers
            </p>
          </div>

          {/* View Invoices */}
          <div
            onClick={() => router.push('/invoices')}
            className="bg-white rounded-lg shadow-md p-8 hover:shadow-xl transition-shadow cursor-pointer border border-secondary-100"
          >
            <div className="w-16 h-16 bg-primary-600 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-secondary-900 mb-2">View Invoices</h3>
            <p className="text-secondary-600 text-sm">Coming soon...</p>
          </div>

          {/* Reports */}
          <div className="bg-white rounded-lg shadow-md p-8 hover:shadow-xl transition-shadow cursor-pointer border border-secondary-100 opacity-50">
            <div className="w-16 h-16 bg-secondary-400 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-secondary-900 mb-2">Reports</h3>
            <p className="text-secondary-600 text-sm">Coming soon...</p>
          </div>
        </div>
      </main>
    </div>
  );
}