/**
 * Print Invoice Page - Formatted for printing
 * Clean, professional invoice layout
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { invoiceAPI, isAuthenticated } from '../../../services/api';

export default function PrintInvoice() {
  const router = useRouter();
  const { id } = router.query;
  const [invoice, setInvoice] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    
    if (id) {
      loadInvoice();
    }
  }, [id, router]);

  const loadInvoice = async () => {
    try {
      const response = await invoiceAPI.getPrint(id);
      if (response.data.success) {
        setInvoice(response.data.data.invoice);
        setCompany(response.data.data.company);
      }
    } catch (error) {
      console.error('Failed to load invoice:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading invoice...</div>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Invoice not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Print Button - Hidden when printing */}
      <div className="print:hidden bg-secondary-900 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-secondary-700 hover:bg-secondary-600 rounded-lg"
          >
            ← Back to Dashboard
          </button>
          <button
            onClick={handlePrint}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium"
          >
            Print Invoice
          </button>
        </div>
      </div>

      {/* Invoice Content */}
      <div className="container mx-auto p-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-24 h-24 bg-secondary-900 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-4xl font-bold">SD</span>
          </div>
          <h1 className="text-2xl font-bold text-secondary-900 mb-2">
            {company?.name || 'Standard Steels & Hardware'}
          </h1>
          <p className="text-sm text-secondary-600">
            {company?.address || '123 Industrial Area, Steel City'}
          </p>
          <p className="text-sm text-secondary-600">
            Phone: {company?.phone || '+91 12345 67890'} | Email: {company?.email || 'info@standardsteels.com'}
          </p>
        </div>

        {/* Invoice Details */}
        <div className="mb-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-lg font-bold text-secondary-900 mb-2">Bill To:</h2>
              <p className="font-medium">{invoice.customer_name}</p>
              <p className="text-sm text-secondary-600">Phone: {invoice.customer_phone || '12345457890'}</p>
            </div>
            
            <div className="text-right">
              <p className="text-sm text-secondary-600">Invoice No: <span className="font-medium text-secondary-900">{invoice.invoice_number}</span></p>
              <p className="text-sm text-secondary-600">Date: <span className="font-medium text-secondary-900">{invoice.invoice_date}</span></p>
            </div>
          </div>
        </div>

        {/* Items Table */}
        <div className="mb-8">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-secondary-900 text-white">
                <th className="text-left py-3 px-4 font-semibold">Item Name</th>
                <th className="text-center py-3 px-4 font-semibold">Unit</th>
                <th className="text-center py-3 px-4 font-semibold">Quantity</th>
                <th className="text-right py-3 px-4 font-semibold">Rate</th>
                <th className="text-right py-3 px-4 font-semibold">Amount</th>
              </tr>
            </thead>
            <tbody>
              {invoice.items && invoice.items.map((item, index) => (
                <tr key={index} className="border-b border-secondary-200">
                  <td className="py-3 px-4">{item.item_name}</td>
                  <td className="py-3 px-4 text-center capitalize">{item.unit}</td>
                  <td className="py-3 px-4 text-center">{item.quantity}</td>
                  <td className="py-3 px-4 text-right">₹{parseFloat(item.rate).toFixed(2)}</td>
                  <td className="py-3 px-4 text-right font-medium">₹{parseFloat(item.total).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Totals */}
        <div className="flex justify-end mb-8">
          <div className="w-64 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-secondary-600">Subtotal:</span>
              <span className="font-medium">₹{parseFloat(invoice.subtotal).toFixed(2)}</span>
            </div>
            
            {invoice.tax_amount > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-secondary-600">Tax:</span>
                <span className="font-medium">₹{parseFloat(invoice.tax_amount).toFixed(2)}</span>
              </div>
            )}
            
            {invoice.discount_amount > 0 && (
              <div className="flex justify-between text-sm text-red-600">
                <span>Discount:</span>
                <span className="font-medium">-₹{parseFloat(invoice.discount_amount).toFixed(2)}</span>
              </div>
            )}
            
            <div className="flex justify-between pt-2 border-t-2 border-secondary-900">
              <span className="font-bold text-lg">Grand Total:</span>
              <span className="font-bold text-lg">₹{parseFloat(invoice.grand_total).toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 pt-6 border-t border-secondary-200">
          <p className="text-sm text-secondary-600 mb-2">Thank you for your business!</p>
          <p className="text-xs text-secondary-500">
            For any queries, please contact us: {company?.email || 'info@standardsteels.com'}
          </p>
          <p className="text-xs text-secondary-500 mt-4">
            Terms & Conditions Apply | This is a computer generated invoice
          </p>
        </div>
      </div>

      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          body {
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
          }
          
          .print\\:hidden {
            display: none !important;
          }
          
          @page {
            margin: 1cm;
          }
        }
      `}</style>
    </div>
  );
}