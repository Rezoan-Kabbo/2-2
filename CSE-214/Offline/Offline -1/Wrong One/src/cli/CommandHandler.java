package cli;

import io.CsvMenuLoader;
import io.ReceiptWriter;
import model.MenuItem;
import model.Order;
import model.OrderItem;
import model.Size;
import service.MenuCatalog;
import service.OrderService;
import service.ReceiptService;
import util.MoneyUtils;
import util.TextUtils;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Processes CLI commands and coordinates services.
 */
public class CommandHandler {
    private final MenuCatalog catalog;
    private final OrderService orderService;
    private final ReceiptService receiptService;
    private final List<OrderItem> cart = new ArrayList<>();
    private Order lastOrder;

    public CommandHandler(MenuCatalog catalog, OrderService orderService, ReceiptService receiptService) {
        this.catalog = catalog;
        this.orderService = orderService;
        this.receiptService = receiptService;
    }

    public void handleLoad(String filePath) {
        try {
            catalog.addAll(new CsvMenuLoader().loadFromFile(filePath));
            cart.clear();
            lastOrder = null;
        } catch (IOException e) {
            System.err.println("Could not load menu: " + e.getMessage());
        }
    }

    public void handleMenu() {
        System.out.println("\nMenu");
        System.out.println(TextUtils.separator(60));
        for (MenuItem item : catalog.findAll()) {
            System.out.println(item);
        }
    }

    public void handleAdd(String[] parts) {
        if (parts.length < 4) {
            System.err.println("Usage: add <code> <qty> <SMALL|MEDIUM|LARGE> [cheese] [spicy]");
            return;
        }

        MenuItem menuItem = catalog.findByCode(parts[1]);
        if (menuItem == null) {
            System.err.println("Unknown menu code: " + parts[1]);
            return;
        }

        int quantity = Integer.parseInt(parts[2]);
        Size size = Size.valueOf(parts[3].toUpperCase());
        boolean cheese = false;
        boolean spicy = false;

        for (int i = 4; i < parts.length; i++) {
            if ("cheese".equalsIgnoreCase(parts[i])) {
                cheese = true;
            } else if ("spicy".equalsIgnoreCase(parts[i])) {
                spicy = true;
            }
        }

        OrderItem item = orderService.createOrderItem(menuItem, quantity, size, cheese, spicy, "");
        cart.add(item);
        System.out.println("Added: " + item);
    }

    public void handleCart() {
        if (cart.isEmpty()) {
            System.out.println("Cart is empty.");
            return;
        }

        System.out.println("\nCurrent Cart");
        System.out.println(TextUtils.separator(72));
        double total = 0.0;
        for (OrderItem item : cart) {
            System.out.println(item);
            total += item.getSubtotal();
        }
        System.out.println(TextUtils.separator(72));
        System.out.println("Cart subtotal: " + MoneyUtils.format(total));
    }

    public void handleClear() {
        cart.clear();
        System.out.println("Cart cleared.");
    }

    public void handleCheckout(String[] parts) {
        if (cart.isEmpty()) {
            System.err.println("Cannot checkout an empty cart.");
            return;
        }
        if (parts.length < 4) {
            System.err.println("Usage: checkout pickup <name> <phone> OR checkout delivery <name> <phone> <address>");
            return;
        }

        String mode = parts[1].toLowerCase();
        String name = parts[2].replace('_', ' ');
        String phone = parts[3];

        if ("pickup".equals(mode)) {
            lastOrder = orderService.createPickupOrder(name, phone, cart);
        } else if ("delivery".equals(mode)) {
            if (parts.length < 5) {
                System.err.println("Delivery checkout requires an address.");
                return;
            }
            String address = parts[4].replace('_', ' ');
            lastOrder = orderService.createDeliveryOrder(name, phone, address, cart,
                    "WELCOME10", false, "CLI order");
        } else {
            System.err.println("Unknown checkout mode: " + mode);
            return;
        }

        cart.clear();
        System.out.println(receiptService.formatReceipt(lastOrder));
    }

    public void handleSample() {
        lastOrder = orderService.createSampleFamilyOrder(catalog);
        System.out.println(receiptService.formatReceipt(lastOrder));
    }

    public void handleReceipt(String outputPath) {
        if (lastOrder == null) {
            System.err.println("No order has been placed yet.");
            return;
        }

        try {
            new ReceiptWriter(receiptService).writeReceipt(outputPath, lastOrder);
        } catch (IOException e) {
            System.err.println("Could not write receipt: " + e.getMessage());
        }
    }

    public void handleHelp() {
        System.out.println("\nFoodFlow Commands:");
        System.out.println("  load <menu.csv>                              - Load menu data");
        System.out.println("  menu                                         - Show menu");
        System.out.println("  add <code> <qty> <size> [cheese] [spicy]     - Add item to cart");
        System.out.println("  cart                                         - Show cart");
        System.out.println("  clear                                        - Clear cart");
        System.out.println("  checkout pickup <name> <phone>               - Place pickup order");
        System.out.println("  checkout delivery <name> <phone> <address>   - Place delivery order");
        System.out.println("  sample                                       - Create sample family order");
        System.out.println("  receipt <outpath>                            - Write last receipt");
        System.out.println("  help                                         - Show help");
        System.out.println("  exit                                         - Exit");
    }
}

