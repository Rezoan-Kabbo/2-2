package io;

import model.Order;
import model.OrderItem;
import service.ReceiptService;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

/**
 * Writes text receipts to disk.
 */
public class ReceiptWriter {
    private final ReceiptService receiptService;

    public ReceiptWriter(ReceiptService receiptService) {
        this.receiptService = receiptService;
    }

    public void writeReceipt(String filePath, Order order) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePath))) {
            writer.write(receiptService.formatReceipt(order));
            writer.write("\n");
        }
        System.out.println("Receipt written to: " + filePath);
    }
}

