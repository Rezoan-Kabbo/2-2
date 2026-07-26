package model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

/**
 * Represents a placed food order.
 *
 * Design note for the assignment:
 * This class works, but its construction API is intentionally awkward.
 * The long constructor mixes required fields, optional fields, defaults,
 * validation, and pricing flags. Students should refactor this design without
 * changing the observable behavior of the program.
 */
public class Order {
    public static final double DELIVERY_FEE = 80.0;
    public static final double RUSH_FEE = 120.0;
    public static final double GIFT_WRAP_FEE = 50.0;

    private final String orderId;
    private final String customerName;
    private final String phone;
    private final DeliveryType deliveryType;
    private final String deliveryAddress;
    private final PaymentMethod paymentMethod;
    private final LocalDateTime scheduledTime;
    private final String couponCode;
    private final boolean giftWrap;
    private final boolean cutleryRequired;
    private final int loyaltyPointsToRedeem;
    private final boolean rushOrder;
    private final List<OrderItem> items;
    private final String specialInstructions;

    // Private constructor: Can only be instantiated via the Builder
    private Order(Builder builder) {
        this.orderId = requireNonBlank(builder.orderId, "Order id");
        this.customerName = requireNonBlank(builder.customerName, "Customer name");
        this.phone = requireNonBlank(builder.phone, "Phone");
        this.deliveryType = builder.deliveryType != null ? builder.deliveryType : DeliveryType.PICKUP;
        this.paymentMethod = builder.paymentMethod != null ? builder.paymentMethod : PaymentMethod.CASH;
        this.scheduledTime = builder.scheduledTime;
        this.couponCode = builder.couponCode != null ? builder.couponCode.trim().toUpperCase() : "";
        this.giftWrap = builder.giftWrap;
        this.cutleryRequired = builder.cutleryRequired;
        this.loyaltyPointsToRedeem = Math.max(0, builder.loyaltyPointsToRedeem);
        this.rushOrder = builder.rushOrder;
        this.specialInstructions = builder.specialInstructions != null ? builder.specialInstructions.trim() : "";

        if (this.deliveryType == DeliveryType.DELIVERY) {
            this.deliveryAddress = requireNonBlank(builder.deliveryAddress, "Delivery address");
        } else {
            this.deliveryAddress = builder.deliveryAddress != null ? builder.deliveryAddress.trim() : "";
        }

        Objects.requireNonNull(builder.items, "Items cannot be null");
        if (builder.items.isEmpty()) {
            throw new IllegalArgumentException("Order must contain at least one item");
        }
        this.items = Collections.unmodifiableList(new ArrayList<>(builder.items));
    }

    // Static factory method to initialize the builder with required fields
    public static Builder builder(String orderId, String customerName, String phone) {
        return new Builder(orderId, customerName, phone);
    }

    // --- Getters and Business Logic ---

    public String getOrderId() { return orderId; }
    public String getCustomerName() { return customerName; }
    public String getPhone() { return phone; }
    public DeliveryType getDeliveryType() { return deliveryType; }
    public String getDeliveryAddress() { return deliveryAddress; }
    public PaymentMethod getPaymentMethod() { return paymentMethod; }
    public LocalDateTime getScheduledTime() { return scheduledTime; }
    public String getCouponCode() { return couponCode; }
    public boolean isGiftWrap() { return giftWrap; }
    public boolean isCutleryRequired() { return cutleryRequired; }
    public int getLoyaltyPointsToRedeem() { return loyaltyPointsToRedeem; }
    public boolean isRushOrder() { return rushOrder; }
    public List<OrderItem> getItems() { return items; }
    public String getSpecialInstructions() { return specialInstructions; }

    public double getSubtotal() {
        return items.stream().mapToDouble(OrderItem::getSubtotal).sum();
    }

    public double getDiscount() {
        double couponDiscount = 0.0;
        if ("WELCOME10".equals(couponCode)) {
            couponDiscount = getSubtotal() * 0.10;
        } else if ("FAMILY15".equals(couponCode) && getSubtotal() >= 1000.0) {
            couponDiscount = getSubtotal() * 0.15;
        }

        double loyaltyDiscount = Math.min(loyaltyPointsToRedeem, 100);
        return couponDiscount + loyaltyDiscount;
    }

    public double getServiceCharges() {
        double charges = 0.0;
        if (deliveryType == DeliveryType.DELIVERY) {
            charges += DELIVERY_FEE;
        }
        if (rushOrder) {
            charges += RUSH_FEE;
        }
        if (giftWrap) {
            charges += GIFT_WRAP_FEE;
        }
        return charges;
    }

    public double getTotal() {
        return Math.max(0.0, getSubtotal() + getServiceCharges() - getDiscount());
    }

    private static String requireNonBlank(String value, String fieldName) {
        Objects.requireNonNull(value, fieldName + " cannot be null");
        String trimmed = value.trim();
        if (trimmed.isEmpty()) {
            throw new IllegalArgumentException(fieldName + " cannot be blank");
        }
        return trimmed;
    }

    // --- The Builder Class ---
    public static class Builder {
        // Required parameters
        private final String orderId;
        private final String customerName;
        private final String phone;

        // Optional parameters initialized to matching class defaults
        private DeliveryType deliveryType = DeliveryType.PICKUP;
        private String deliveryAddress = "";
        private PaymentMethod paymentMethod = PaymentMethod.CASH;
        private LocalDateTime scheduledTime;
        private String couponCode = "";
        private boolean giftWrap = false;
        private boolean cutleryRequired = true;
        private int loyaltyPointsToRedeem = 0;
        private boolean rushOrder = false;
        private List<OrderItem> items = new ArrayList<>();
        private String specialInstructions = "";

        // Constructor enforces minimal required core data
        private Builder(String orderId, String customerName, String phone) {
            this.orderId = orderId;
            this.customerName = customerName;
            this.phone = phone;
        }

        public Builder deliveryType(DeliveryType deliveryType) {
            this.deliveryType = deliveryType;
            return this;
        }

        public Builder deliveryAddress(String deliveryAddress) {
            this.deliveryAddress = deliveryAddress;
            return this;
        }

        public Builder paymentMethod(PaymentMethod paymentMethod) {
            this.paymentMethod = paymentMethod;
            return this;
        }

        public Builder scheduledTime(LocalDateTime scheduledTime) {
            this.scheduledTime = scheduledTime;
            return this;
        }

        public Builder couponCode(String couponCode) {
            this.couponCode = couponCode;
            return this;
        }

        public Builder giftWrap(boolean giftWrap) {
            this.giftWrap = giftWrap;
            return this;
        }

        public Builder cutleryRequired(boolean cutleryRequired) {
            this.cutleryRequired = cutleryRequired;
            return this;
        }

        public Builder loyaltyPointsToRedeem(int loyaltyPointsToRedeem) {
            this.loyaltyPointsToRedeem = loyaltyPointsToRedeem;
            return this;
        }

        public Builder rushOrder(boolean rushOrder) {
            this.rushOrder = rushOrder;
            return this;
        }

        public Builder items(List<OrderItem> items) {
            this.items = items;
            return this;
        }

        public Builder addItem(OrderItem item) {
            if (this.items == null || this.items.getClass().getName().contains("Unmodifiable")) {
                this.items = new ArrayList<>(this.items != null ? this.items : Collections.emptyList());
            }
            if (item != null) {
                this.items.add(item);
            }
            return this;
        }

        public Builder specialInstructions(String specialInstructions) {
            this.specialInstructions = specialInstructions;
            return this;
        }

        public Order build() {
            return new Order(this);
        }
    }
}