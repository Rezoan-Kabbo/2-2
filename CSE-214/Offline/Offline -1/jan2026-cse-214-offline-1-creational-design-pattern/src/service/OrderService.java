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
        return OrderItem.builder(item, quantity)
                .size(size)
                .extraCheese(extraCheese)
                .spicy(spicy)
                .note(note)
                .build();
    }

    public Order createDeliveryOrder(String customerName,
                                     String phone,
                                     String address,
                                     List<OrderItem> items,
                                     String couponCode,
                                     boolean rushOrder,
                                     String specialInstructions) {
        return Order.builder(nextOrderId(), customerName, phone)
                .deliveryType(DeliveryType.DELIVERY)
                .deliveryAddress(address)
                .paymentMethod(PaymentMethod.CASH)
                .items(items)
                .couponCode(couponCode)
                .rushOrder(rushOrder)
                .specialInstructions(specialInstructions)
                .build();
    }

    public Order createPickupOrder(String customerName, String phone, List<OrderItem> items) {
        return Order.builder(nextOrderId(), customerName, phone)
                .deliveryType(DeliveryType.PICKUP)
                .paymentMethod(PaymentMethod.CASH)
                .items(items)
                .build();
    }

    public Order createScheduledGiftOrder(String customerName,
                                          String phone,
                                          String address,
                                          List<OrderItem> items,
                                          LocalDateTime scheduledTime) {
        return Order.builder(nextOrderId(), customerName, phone)
                .deliveryType(DeliveryType.DELIVERY)
                .deliveryAddress(address)
                .paymentMethod(PaymentMethod.CARD)
                .scheduledTime(scheduledTime)
                .couponCode("WELCOME10")
                .giftWrap(true)
                .cutleryRequired(false)
                .loyaltyPointsToRedeem(25)
                .items(items)
                .specialInstructions("Please call before delivery")
                .build();
    }

    public Order createSampleFamilyOrder(MenuCatalog catalog) {
        List<OrderItem> items = new ArrayList<>();
        
        items.add(OrderItem.builder(catalog.findByCode("P01"), 2)
                .size(Size.LARGE)
                .extraCheese(true)
                .spicy(false)
                .note("half spicy")
                .build());
                
        items.add(OrderItem.builder(catalog.findByCode("B02"), 3)
                .size(Size.MEDIUM)
                .extraCheese(true)
                .spicy(true)
                .build());
                
        items.add(OrderItem.builder(catalog.findByCode("D02"), 4)
                .size(Size.MEDIUM)
                .extraCheese(false)
                .spicy(false)
                .note("less sugar")
                .build());
                
        items.add(OrderItem.builder(catalog.findByCode("S02"), 2)
                .size(Size.LARGE)
                .extraCheese(false)
                .spicy(true)
                .build());

        return Order.builder(nextOrderId(), "Sample Family", "01711111111")
                .deliveryType(DeliveryType.DELIVERY)
                .deliveryAddress("House 25, Road 4, Dhanmondi")
                .paymentMethod(PaymentMethod.MOBILE_BANKING)
                .couponCode("FAMILY15")
                .giftWrap(false)
                .cutleryRequired(true)
                .loyaltyPointsToRedeem(50)
                .rushOrder(true)
                .items(items)
                .specialInstructions("Deliver together")
                .build();
    }

    private String nextOrderId() {
        return "FF-" + nextNumber++;
    }
}