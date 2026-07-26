import io.CsvMenuLoader;
import io.ReceiptWriter;
import model.MenuItem;
import model.Order;
import model.OrderItem;
import model.Size;
import service.MenuCatalog;
import service.OrderService;
import service.ReceiptService;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

/**
 * Functional test harness for FoodFlow.
 *
 * The harness checks behavior, not the internal design. After students refactor
 * the code, these tests should still pass.
 */
public class TestHarness {
    public static void main(String[] args) {
        System.out.println("=== FoodFlow Test Harness ===\n");

        try {
            testMenuLoading();
            testOrderItemPricing();
            testDeliveryOrderPricing();
            testScheduledGiftOrderPricing();
            testSampleOrderAndReceipt();
            testValidation();

            System.out.println("\n=== All Tests Passed ===");
        } catch (Exception e) {
            System.err.println("[FAIL] " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static void testMenuLoading() throws Exception {
        System.out.println("Test 1: Loading menu...");
        MenuCatalog catalog = loadCatalog();
        check(catalog.count() == 8, "Expected 8 menu items");
        check(catalog.findByCode("B01") != null, "Expected B01 in menu");
        check(catalog.findByCode("p01") != null, "Menu lookup should be case-insensitive");
        System.out.println("[PASS] Menu loaded correctly");
    }

    private static void testOrderItemPricing() throws Exception {
        System.out.println("Test 2: Pricing customized order item...");
        MenuCatalog catalog = loadCatalog();
        OrderService service = new OrderService();
        OrderItem item = service.createOrderItem(catalog.findByCode("B01"), 2, Size.LARGE, true, true, "");
        assertMoney(876.0, item.getSubtotal(), "Two large classic burgers with cheese");
        System.out.println("[PASS] Order item pricing is correct");
    }

    private static void testDeliveryOrderPricing() throws Exception {
        System.out.println("Test 3: Pricing delivery order...");
        MenuCatalog catalog = loadCatalog();
        OrderService service = new OrderService();
        List<OrderItem> items = Arrays.asList(
                service.createOrderItem(catalog.findByCode("B01"), 2, Size.LARGE, true, true, ""),
                service.createOrderItem(catalog.findByCode("D01"), 2, Size.MEDIUM, false, false, "")
        );

        Order order = service.createDeliveryOrder("Alice", "01700000000",
                "House 12, Road 7", items, "WELCOME10", false, "Ring bell");

        assertMoney(1116.0, order.getSubtotal(), "Delivery subtotal");
        assertMoney(111.6, order.getDiscount(), "WELCOME10 discount");
        assertMoney(80.0, order.getServiceCharges(), "Delivery charge");
        assertMoney(1084.4, order.getTotal(), "Delivery total");
        check(order.getDeliveryAddress().equals("House 12, Road 7"), "Address should be preserved");
        System.out.println("[PASS] Delivery order pricing is correct");
    }

    private static void testScheduledGiftOrderPricing() throws Exception {
        System.out.println("Test 4: Pricing scheduled gift order...");
        MenuCatalog catalog = loadCatalog();
        OrderService service = new OrderService();
        List<OrderItem> items = Arrays.asList(
                service.createOrderItem(catalog.findByCode("P02"), 1, Size.MEDIUM, true, false, ""),
                service.createOrderItem(catalog.findByCode("S01"), 2, Size.SMALL, false, false, "")
        );

        Order order = service.createScheduledGiftOrder("Bob", "01800000000",
                "Banani", items, LocalDateTime.of(2026, 7, 1, 18, 30));

        assertMoney(886.0, order.getSubtotal(), "Gift subtotal");
        assertMoney(113.6, order.getDiscount(), "Gift discount");
        assertMoney(130.0, order.getServiceCharges(), "Gift delivery and wrapping charges");
        assertMoney(902.4, order.getTotal(), "Gift total");
        check(order.getScheduledTime() != null, "Scheduled time should be set");
        check(order.isGiftWrap(), "Gift wrapping should be enabled");
        System.out.println("[PASS] Scheduled gift order pricing is correct");
    }

    private static void testSampleOrderAndReceipt() throws Exception {
        System.out.println("Test 5: Creating sample order and writing receipt...");
        MenuCatalog catalog = loadCatalog();
        OrderService service = new OrderService();
        ReceiptService receiptService = new ReceiptService();

        Order order = service.createSampleFamilyOrder(catalog);
        assertMoney(4282.0, order.getSubtotal(), "Sample subtotal");
        assertMoney(692.3, order.getDiscount(), "Sample discount");
        assertMoney(200.0, order.getServiceCharges(), "Sample service charges");
        assertMoney(3789.7, order.getTotal(), "Sample total");

        String receipt = receiptService.formatReceipt(order);
        check(receipt.contains("FOODFLOW RECEIPT"), "Receipt should contain heading");
        check(receipt.contains("Sample Family"), "Receipt should contain customer name");

        Path output = Paths.get("out", "foodflow-test-receipt.txt");
        Files.createDirectories(output.getParent());
        new ReceiptWriter(receiptService).writeReceipt(output.toString(), order);
        check(Files.exists(output), "Receipt file should be created");
        System.out.println("[PASS] Sample order and receipt are correct");
    }

    private static void testValidation() throws Exception {
        System.out.println("Test 6: Checking validation...");
        MenuCatalog catalog = loadCatalog();
        OrderService service = new OrderService();
        List<OrderItem> items = Arrays.asList(
                service.createOrderItem(catalog.findByCode("D01"), 1, Size.MEDIUM, false, false, "")
        );

        boolean rejected = false;
        try {
            service.createDeliveryOrder("Carol", "01900000000", "", items, "", false, "");
        } catch (IllegalArgumentException e) {
            rejected = true;
        }
        check(rejected, "Delivery order without address should be rejected");
        System.out.println("[PASS] Validation behavior is correct");
    }

    private static MenuCatalog loadCatalog() throws Exception {
        CsvMenuLoader loader = new CsvMenuLoader();
        List<MenuItem> items = loader.loadFromFile("data/menu.csv");
        MenuCatalog catalog = new MenuCatalog();
        catalog.addAll(items);
        return catalog;
    }

    private static void assertMoney(double expected, double actual, String label) {
        if (Math.abs(expected - actual) > 0.001) {
            throw new AssertionError(label + ": expected " + expected + " but found " + actual);
        }
    }

    private static void check(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
