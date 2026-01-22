"""
Signals for maintaining data consistency across the application
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, Count
import logging

logger = logging.getLogger(__name__)

# Import models
try:
    from invoices.models import Invoice, InvoiceItem
    from customers.models import Customer
except ImportError:
    pass


@receiver(post_save, sender=InvoiceItem)
def update_invoice_totals_on_item_save(sender, instance, created, **kwargs):
    """
    Update invoice subtotal and totals when invoice item is saved or updated.
    Recalculates all monetary fields automatically.
    """
    try:
        invoice = instance.invoice
        # Recalculate invoice totals
        invoice.calculate_totals()
        invoice.save(update_fields=['subtotal', 'tax_amount', 'grand_total'])
        logger.info(f"Updated invoice totals for invoice {invoice.invoice_number}")
    except Exception as e:
        logger.error(f"Error updating invoice totals: {str(e)}", exc_info=True)


@receiver(post_delete, sender=InvoiceItem)
def update_invoice_totals_on_item_delete(sender, instance, **kwargs):
    """
    Update invoice subtotal and totals when invoice item is deleted.
    Ensures invoice totals reflect current items.
    """
    try:
        invoice = instance.invoice
        # Recalculate invoice totals
        invoice.calculate_totals()
        invoice.save(update_fields=['subtotal', 'tax_amount', 'grand_total'])
        logger.info(f"Updated invoice totals after deleting item from invoice {invoice.invoice_number}")
    except Exception as e:
        logger.error(f"Error updating invoice totals on delete: {str(e)}", exc_info=True)


@receiver(post_save, sender=Invoice)
def update_customer_stats_on_invoice_save(sender, instance, created, **kwargs):
    """
    Update customer statistics when invoice is created or updated.
    Maintains total_invoices and total_amount denormalization.
    """
    try:
        if created or instance.status == 'paid':
            customer = instance.customer
            
            # Calculate stats
            stats = Invoice.objects.filter(
                customer=customer,
                status='paid'
            ).aggregate(
                total_count=Count('id'),
                total_amount=Sum('grand_total')
            )
            
            customer.total_invoices = stats['total_count'] or 0
            customer.total_amount = stats['total_amount'] or 0
            customer.save(update_fields=['total_invoices', 'total_amount'])
            
            logger.info(f"Updated customer {customer.customer_name} statistics")
    except Exception as e:
        logger.error(f"Error updating customer stats: {str(e)}", exc_info=True)


@receiver(post_delete, sender=Invoice)
def update_customer_stats_on_invoice_delete(sender, instance, **kwargs):
    """
    Update customer statistics when invoice is deleted.
    Ensures customer totals stay accurate.
    """
    try:
        customer = instance.customer
        
        # Recalculate stats
        stats = Invoice.objects.filter(
            customer=customer,
            status='paid'
        ).aggregate(
            total_count=Count('id'),
            total_amount=Sum('grand_total')
        )
        
        customer.total_invoices = stats['total_count'] or 0
        customer.total_amount = stats['total_amount'] or 0
        customer.save(update_fields=['total_invoices', 'total_amount'])
        
        logger.info(f"Updated customer {customer.customer_name} statistics after invoice deletion")
    except Exception as e:
        logger.error(f"Error updating customer stats on delete: {str(e)}", exc_info=True)
