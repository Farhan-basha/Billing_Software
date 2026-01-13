/**
 * Create Invoice Page - Complete implementation matching UI
 * Handles customer details, items, calculations, and invoice generation
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { invoiceAPI, customerAPI, settingsAPI, isAuthenticated } from '../../services/api';
import { toast } from 'react-toastify';

export default function CreateInvoice() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState(null);
  
  // Form state
  const [customerDetails, setCustomerDetails] = useState({
    customer_name: '',
    phone_number: '',
  });
  
  const [invoiceData, setInvoiceData] = useState({
    invoice_date: new Date().toISOString().split('T')[0],
    tax_rate: 0,
    discount_amount: 0,
  });
  
  const [items, setItems] = useState([
    { item_name: 'Metal sheet', unit: 'piece', quantity: 5, rate: 250.00 },
    { item_name: 'Metal pipe', unit: 'piece', quantity: 1, rate: 149.99 },
    { item_name: 'Metal sheet', unit: 'piece', quantity: 5, rate: 250.00 },
    { item_name: 'Metal pipe', unit: 'piece', quantity: 1, rate: 149.99 },
  ]);
  
  const [currentItem, setCurrentItem] = useState({
    item_name: '',
    unit: 'sq meter',
    quantity: 1,
    rate: 0,
  });
  
  const [calculations, setCalculations] = useState({
    subtotal: 0,
    tax_amount: 0,
    grand_total: 0,
  });
  
  const [taxEnabled, setTaxEnabled] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    
    loadSettings();
  }, [router]);

  useEffect(() => {
    calculateTotals();
  }, [items, invoiceData.tax_rate, invoiceData.discount_amount, taxEnabled]);

  const loadSettings = async () => {
    try {
      const response = await settingsAPI.getCompany();
      if (response.data.success) {
        setSettings(response.data.data);
        setInvoiceData(prev => ({
          ...prev,
          tax_rate: response.data.data.default_tax_rate || 0,
        }));
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const calculateTotals = () => {
    const subtotal = items.reduce((sum, item) => {
      return sum + (parseFloat(item.quantity) * parseFloat(item.rate));
    }, 0);
    
    const taxAmount = taxEnabled ? (subtotal * parseFloat(invoiceData.tax_rate || 0)) / 100 : 0;
    const discount = parseFloat(invoiceData.discount_amount || 0);
    const grandTotal = subtotal + taxAmount - discount;
    
    setCalculations({
      subtotal: subtotal.toFixed(2),
      tax_amount: taxAmount.toFixed(2),
      grand_total: grandTotal.toFixed(2),
    });
  };

  const handleCustomerChange = (e) => {
    setCustomerDetails({
      ...customerDetails,
      [e.target.name]: e.target.value,
    });
  };

  const handleItemChange = (e) => {
    setCurrentItem({
      ...currentItem,
      [e.target.name]: e.target.value,
    });
  };

  const handleInvoiceChange = (e) => {
    setInvoiceData({
      ...invoiceData,
      [e.target.name]: e.target.value,
    });
  };

  const addItem = () => {
    if (!currentItem.item_name || currentItem.quantity <= 0 || currentItem.rate < 0) {
      toast.error('Please fill all item details correctly');
      return;
    }
    
    setItems([...items, { ...currentItem }]);
    setCurrentItem({
      item_name: '',
      unit: 'sq meter',
      quantity: 1,
      rate: 0,
    });
  };

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleBack = () => {
    router.push('/dashboard');
  };

  const handleSave = async () => {
    if (!customerDetails.customer_name || !customerDetails.phone_number) {
      toast.error('Please fill customer details');
      return;
    }
    
    if (items.length === 0) {
      toast.error('Please add at least one item');
      return;
    }
    
    setLoading(true);
    
    try {
      // First, check if customer exists or create new
      let customerId;
      
      const searchResponse = await customerAPI.search(customerDetails.phone_number);
      const existingCustomers = searchResponse.data.data;
      
      if (existingCustomers && existingCustomers.length > 0) {
        customerId = existingCustomers[0].id;
      } else {
        const customerResponse = await customerAPI.create(customerDetails);
        customerId = customerResponse.data.data.id;
      }
      
      // Create invoice
      const invoicePayload = {
        customer: customerId,
        invoice_date: invoiceData.invoice_date,
        tax_rate: taxEnabled ? parseFloat(invoiceData.tax_rate) : 0,
        discount_amount: parseFloat(invoiceData.discount_amount) || 0,
        items: items.map((item, index) => ({
          item_name: item.item_name,
          unit: item.unit,
          quantity: parseFloat(item.quantity),
          rate: parseFloat(item.rate),
          order: index,
        })),
      };
      
      const response = await invoiceAPI.create(invoicePayload);
      
      if (response.data.success) {
        toast.success('Invoice created successfully!');
        router.push(`/invoices/print/${response.data.data.id}`);
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error?.message || 
                          error.response?.data?.message ||
                          'Failed to create invoice';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    toast.info('Please save the invoice first to print');
  };

  const handleNewInvoice = () => {
    setCustomerDetails({ customer_name: '', phone_number: '' });
    setItems([]);
    setCurrentItem({ item_name: '', unit: 'sq meter', quantity: 1, rate: 0 });
    setInvoiceData({
      invoice_date: new Date().toISOString().split('T')[0],
      tax_rate: settings?.default_tax_rate || 0,
      discount_amount: 0,
    });
    setTaxEnabled(false);
  };

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <header className="bg-secondary-900 text-white shadow-lg">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={handleBack}
              className="px-4 py-2 bg-secondary-700 hover:bg-secondary-600 rounded-lg text-sm font-medium transition-colors"
            >
              ← Back
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <span className="text-secondary-900 text-lg font-bold">SD</span>
              </div>
              <div>
                <h1 className="text-lg font-bold">Standard Steels & Hardware</h1>
                <p className="text-xs text-secondary-300">Billing System</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm">Admin</span>
            <button
              onClick={() => router.push('/login')}
              className="px-4 py-2 bg-secondary-700 hover:bg-secondary-600 rounded-lg text-sm font-medium transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">Create New Invoice</h2>
        <p className="text-secondary-600 mb-8">Fill in customer details and add items to generate invoice</p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Item Description */}
          <div className="lg:col-span-2 space-y-6">
            {/* Item Input Form */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-secondary-900 mb-4">Description</h3>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Item Name
                  </label>
                  <input
                    type="text"
                    name="item_name"
                    value={currentItem.item_name}
                    onChange={handleItemChange}
                    placeholder="Enter item name"
                    className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Per
                  </label>
                  <select
                    name="unit"
                    value={currentItem.unit}
                    onChange={handleItemChange}
                    className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary-500"
                  >
                    <option value="sq meter">sq meter</option>
                    <option value="piece">piece</option>
                    <option value="meter">meter</option>
                    <option value="kg">kg</option>
                    <option value="ton">ton</option>
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Quantity
                  </label>
                  <input
                    type="number"
                    name="quantity"
                    value={currentItem.quantity}
                    onChange={handleItemChange}
                    min="1"
                    step="0.01"
                    className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Rate / Price
                  </label>
                  <input
                    type="number"
                    name="rate"
                    value={currentItem.rate}
                    onChange={handleItemChange}
                    min="0"
                    step="0.01"
                    className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Amount
                  </label>
                  <div className="px-4 py-2 bg-secondary-50 border border-secondary-300 rounded-lg text-secondary-700">
                    ₹{(currentItem.quantity * currentItem.rate).toFixed(2)}
                  </div>
                </div>
              </div>
              
              <button
                onClick={addItem}
                className="w-full py-2 bg-secondary-900 text-white rounded-lg font-medium hover:bg-secondary-800 transition-colors"
              >
                Add Item
              </button>
            </div>

            {/* Invoice Items Table */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-secondary-900 mb-4">Invoice Items</h3>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-secondary-200">
                      <th className="text-left py-3 px-2 text-sm font-semibold text-secondary-700">Item Name</th>
                      <th className="text-left py-3 px-2 text-sm font-semibold text-secondary-700">Unit</th>
                      <th className="text-center py-3 px-2 text-sm font-semibold text-secondary-700">Quantity</th>
                      <th className="text-right py-3 px-2 text-sm font-semibold text-secondary-700">Rate</th>
                      <th className="text-right py-3 px-2 text-sm font-semibold text-secondary-700">Total</th>
                      <th className="text-center py-3 px-2 text-sm font-semibold text-secondary-700">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="text-center py-8 text-secondary-500">
                          No items added yet. Add items using the form above.
                        </td>
                      </tr>
                    ) : (
                      items.map((item, index) => (
                        <tr key={index} className="border-b border-secondary-100">
                          <td className="py-3 px-2 text-sm">{item.item_name}</td>
                          <td className="py-3 px-2 text-sm capitalize">{item.unit}</td>
                          <td className="py-3 px-2 text-sm text-center">{item.quantity}</td>
                          <td className="py-3 px-2 text-sm text-right">₹{parseFloat(item.rate).toFixed(2)}</td>
                          <td className="py-3 px-2 text-sm text-right font-medium">
                            ₹{(item.quantity * item.rate).toFixed(2)}
                          </td>
                          <td className="py-3 px-2 text-center">
                            <button
                              onClick={() => removeItem(index)}
                              className="text-red-600 hover:text-red-800 font-medium text-sm"
                            >
                              🗑
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Right Column - Customer Details & Summary */}
          <div className="space-y-6">
            {/* Customer Details */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-secondary-900 mb-4">Customer Details</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Customer Name
                  </label>
                  <input
                    type="text"
                    name="customer_name"
                    value={customerDetails.customer_name}
                    onChange={handleCustomerChange}
                    placeholder="Enter customer name"
                    className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    name="phone_number"
                    value={customerDetails.phone_number}
                    onChange={handleCustomerChange}
                    placeholder="Enter phone number"
                    className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Invoice Number
                  </label>
                  <input
                    type="text"
                    value="INV-508850"
                    readOnly
                    className="w-full px-4 py-2 bg-secondary-50 border border-secondary-300 rounded-lg text-secondary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Date
                  </label>
                  <input
                    type="date"
                    name="invoice_date"
                    value={invoiceData.invoice_date}
                    onChange={handleInvoiceChange}
                    className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary-500"
                  />
                </div>
              </div>
            </div>

            {/* Billing Summary */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-secondary-900 mb-4">Billing Summary</h3>
              
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-600">Subtotal</span>
                  <span className="font-medium">₹{calculations.subtotal}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="taxEnabled"
                      checked={taxEnabled}
                      onChange={(e) => setTaxEnabled(e.target.checked)}
                      className="w-4 h-4"
                    />
                    <label htmlFor="taxEnabled" className="text-sm text-secondary-600">
                      Tax ({invoiceData.tax_rate}%)
                    </label>
                  </div>
                  <span className="font-medium text-sm">₹{calculations.tax_amount}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-secondary-600">Discount</span>
                  <input
                    type="number"
                    name="discount_amount"
                    value={invoiceData.discount_amount}
                    onChange={handleInvoiceChange}
                    min="0"
                    step="0.01"
                    className="w-24 px-2 py-1 border border-secondary-300 rounded text-right text-sm"
                    placeholder="0.00"
                  />
                </div>
                
                <div className="pt-3 border-t border-secondary-200">
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-bold text-secondary-900">Grand Total</span>
                    <span className="text-xl font-bold text-secondary-900">
                      ₹{calculations.grand_total}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 space-y-3">
                <button
                  onClick={handleSave}
                  disabled={loading}
                  className="w-full py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Saving...' : 'Save Invoice'}
                </button>
                
                <button
                  onClick={handlePrint}
                  className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Print Invoice
                </button>
                
                <button
                  onClick={handleNewInvoice}
                  className="w-full py-3 bg-secondary-600 text-white rounded-lg font-medium hover:bg-secondary-700 transition-colors"
                >
                  New Invoice
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}