package service;

import model.DeliveryType;
import model.MenuItem;
import model.Order;
import model.OrderItem;
import model.PaymentMethod;
import model.Size;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Coordinates order creation.
 *
 * Several methods below repeat long Order constructor calls with many optional
 * parameters. That is intentional assignment material for refactoring.
 */
public class OrderService {
    private int nextNumber = 1001;

    public OrderItem createOrderItem(MenuItem item, int quantity, Size size, boolean extraCheese, boolean spicy, String note) {
        return new OrderItem(item, quantity, size, extraCheese, spicy, note);
    }

    public Order createDeliveryOrder(String customerName,
                                     String phone,
                                     String address,
                                     List<OrderItem> items,
                                     String couponCode,
                                     boolean rushOrder,
                                     String specialInstructions) {
        return new Order(nextOrderId(), customerName, phone,
                DeliveryType.DELIVERY,
                address,
                PaymentMethod.CASH,
                null,
                couponCode,
                false,
                true,
                0,
                rushOrder,
                items,
                specialInstructions);
    }

    public Order createPickupOrder(String customerName, String phone, List<OrderItem> items) {
        return new Order(nextOrderId(), customerName, phone,
                DeliveryType.PICKUP,
                "",
                PaymentMethod.CASH,
                null,
                "",
                false,
                true,
                0,
                false,
                items,
                "");
    }

    public Order createScheduledGiftOrder(String customerName,
                                          String phone,
                                          String address,
                                          List<OrderItem> items,
                                          LocalDateTime scheduledTime) {
        return new Order(nextOrderId(), customerName, phone,
                DeliveryType.DELIVERY,
                address,
                PaymentMethod.CARD,
                scheduledTime,
                "WELCOME10",
                true,
                false,
                25,
                false,
                items,
                "Please call before delivery");
    }

    public Order createSampleFamilyOrder(MenuCatalog catalog) {
        List<OrderItem> items = new ArrayList<>();
        items.add(new OrderItem(catalog.findByCode("P01"), 2, Size.LARGE, true, false, "half spicy"));
        items.add(new OrderItem(catalog.findByCode("B02"), 3, Size.MEDIUM, true, true, ""));
        items.add(new OrderItem(catalog.findByCode("D02"), 4, Size.MEDIUM, false, false, "less sugar"));
        items.add(new OrderItem(catalog.findByCode("S02"), 2, Size.LARGE, false, true, ""));

        return new Order(nextOrderId(),
                "Sample Family",
                "01711111111",
                DeliveryType.DELIVERY,
                "House 25, Road 4, Dhanmondi",
                PaymentMethod.MOBILE_BANKING,
                null,
                "FAMILY15",
                false,
                true,
                50,
                true,
                items,
                "Deliver together");
    }

    private String nextOrderId() {
        return "FF-" + nextNumber++;
    }
}

