package service;

import model.Order;
import model.OrderItem;
import util.MoneyUtils;
import util.TextUtils;

/**
 * Formats order receipts.
 */
public class ReceiptService {
    public String formatReceipt(Order order) {
        StringBuilder builder = new StringBuilder();
        builder.append("FOODFLOW RECEIPT\n");
        builder.append(TextUtils.separator(72)).append("\n");
        builder.append("Order ID: ").append(order.getOrderId()).append("\n");
        builder.append("Customer: ").append(order.getCustomerName()).append(" (").append(order.getPhone()).append(")\n");
        builder.append("Type: ").append(order.getDeliveryType()).append("\n");
        if (!order.getDeliveryAddress().isEmpty()) {
            builder.append("Address: ").append(order.getDeliveryAddress()).append("\n");
        }
        if (order.getScheduledTime() != null) {
            builder.append("Scheduled: ").append(order.getScheduledTime()).append("\n");
        }
        builder.append("Payment: ").append(order.getPaymentMethod()).append("\n");
        builder.append(TextUtils.separator(72)).append("\n");

        for (OrderItem item : order.getItems()) {
            builder.append(String.format("%-60s %10s\n", item.toString(), MoneyUtils.format(item.getSubtotal())));
        }

        builder.append(TextUtils.separator(72)).append("\n");
        builder.append(String.format("%-25s %10s\n", "Subtotal:", MoneyUtils.format(order.getSubtotal())));
        builder.append(String.format("%-25s %10s\n", "Service charges:", MoneyUtils.format(order.getServiceCharges())));
        builder.append(String.format("%-25s %10s\n", "Discount:", MoneyUtils.format(order.getDiscount())));
        builder.append(String.format("%-25s %10s\n", "Total:", MoneyUtils.format(order.getTotal())));

        if (!order.getSpecialInstructions().isEmpty()) {
            builder.append("Instructions: ").append(order.getSpecialInstructions()).append("\n");
        }
        return builder.toString();
    }
}

