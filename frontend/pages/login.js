/**
 * Login Page Component
 * Handles both admin and user authentication
 */

import { useState } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import { authAPI, setAuthTokens } from '../services/api';
import { toast } from 'react-toastify';

export default function Login() {
  const router = useRouter();
  const [loginType, setLoginType] = useState('admin');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    console.log('🔐 Login attempt:', { email: formData.email, role: loginType });

    try {
      console.log('📡 Sending request to:', `${process.env.API_BASE_URL || 'http://localhost:8000/api'}/auth/login/`);
      
      const response = await authAPI.login({
        ...formData,
        role: loginType,
      });

      console.log('✅ Login response:', response.data);

      if (response.data.success) {
        const { tokens, user } = response.data.data;
        
        console.log('💾 Storing tokens...');
        // Store tokens
        setAuthTokens(tokens.access, tokens.refresh);
        
        // Store user info
        localStorage.setItem('user', JSON.stringify(user));
        
        console.log('✅ Login successful, redirecting to dashboard...');
        toast.success('Login successful!');
        router.push('/dashboard');
      } else {
        console.error('❌ Login failed: response not successful');
        toast.error('Login failed');
      }
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('Error response:', error.response);
      
      const errorMessage = error.response?.data?.error?.detail || 
                          error.response?.data?.detail ||
                          error.response?.data?.message ||
                          error.message ||
                          'Invalid email or password';
      
      console.error('Error message:', errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-secondary-900 via-secondary-800 to-secondary-900">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md p-8">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-20 h-20 bg-secondary-900 rounded-full flex items-center justify-center mb-4">
            <span className="text-white text-3xl font-bold">SD</span>
          </div>
          <h1 className="text-2xl font-bold text-secondary-900 text-center">
            Standard Steels & Hardware
          </h1>
          <p className="text-secondary-500 text-sm mt-1">
            Quotation Management System
          </p>
        </div>

        {/* Login Type Toggle */}
        <div className="flex mb-6">
          <button
            type="button"
            onClick={() => setLoginType('admin')}
            className={`flex-1 py-2 text-sm font-medium rounded-l-lg transition-colors ${
              loginType === 'admin'
                ? 'bg-secondary-900 text-white'
                : 'bg-secondary-100 text-secondary-600 hover:bg-secondary-200'
            }`}
          >
            Admin Login
          </button>
          <button
            type="button"
            onClick={() => setLoginType('user')}
            className={`flex-1 py-2 text-sm font-medium rounded-r-lg transition-colors ${
              loginType === 'user'
                ? 'bg-secondary-900 text-white'
                : 'bg-secondary-100 text-secondary-600 hover:bg-secondary-200'
            }`}
          >
            User Login
          </button>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Username / Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
              className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
              className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-secondary-900 text-white py-3 rounded-lg font-medium hover:bg-secondary-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Logging in...' : 'Login as Admin'}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-6 text-center">
          <p className="text-xs text-secondary-500">
            © 2025 Standard Steels & Hardware. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
}