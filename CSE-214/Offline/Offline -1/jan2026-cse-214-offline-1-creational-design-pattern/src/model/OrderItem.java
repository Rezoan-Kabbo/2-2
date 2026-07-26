package model;

import java.util.Objects;

/**
 * Represents a customized menu item inside an order.
 */
public class OrderItem {
    public static final double EXTRA_CHEESE_PRICE = 60.0;

    private final MenuItem menuItem;
    private final int quantity;
    private final Size size;
    private final boolean extraCheese;
    private final boolean spicy;
    private final String note;

    // Private constructor: Instantiated only through the Builder
    private OrderItem(Builder builder) {
        this.menuItem = Objects.requireNonNull(builder.menuItem, "Menu item cannot be null");
        if (builder.quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be positive");
        }
        this.quantity = builder.quantity;
        this.size = builder.size != null ? builder.size : Size.MEDIUM;
        this.extraCheese = builder.extraCheese;
        this.spicy = builder.spicy;
        this.note = builder.note != null ? builder.note.trim() : "";
    }

    // Static entry point factory method enforcing core fields
    public static Builder builder(MenuItem menuItem, int quantity) {
        return new Builder(menuItem, quantity);
    }

    // --- Getters & Business Logic ---

    public MenuItem getMenuItem() { return menuItem; }
    public int getQuantity() { return quantity; }
    public Size getSize() { return size; }
    public boolean hasExtraCheese() { return extraCheese; }
    public boolean isSpicy() { return spicy; }
    public String getNote() { return note; }

    public double getUnitPrice() {
        double price = menuItem.getBasePrice() * size.getMultiplier();
        if (extraCheese) {
            price += EXTRA_CHEESE_PRICE;
        }
        return price;
    }

    public double getSubtotal() {
        return getUnitPrice() * quantity;
    }

    public String describeOptions() {
        StringBuilder options = new StringBuilder(size.name());
        if (extraCheese) {
            options.append(", extra cheese");
        }
        if (spicy) {
            options.append(", spicy");
        }
        if (!note.isEmpty()) {
            options.append(", note: ").append(note);
        }
        return options.toString();
    }

    @Override
    public String toString() {
        return String.format("%dx %-20s %-32s %8.2f",
                quantity,
                menuItem.getName(),
                describeOptions(),
                getSubtotal());
    }

    // --- Inner Builder Implementation ---
    public static class Builder {
        // Required fields
        private final MenuItem menuItem;
        private final int quantity;

        // Optional fields initialized to match default rules
        private Size size = Size.MEDIUM;
        private boolean extraCheese = false;
        private boolean spicy = false;
        private String note = "";

        private Builder(MenuItem menuItem, int quantity) {
            this.menuItem = menuItem;
            this.quantity = quantity;
        }

        public Builder size(Size size) {
            this.size = size;
            return this;
        }

        public Builder extraCheese(boolean extraCheese) {
            this.extraCheese = extraCheese;
            return this;
        }

        public Builder spicy(boolean spicy) {
            this.spicy = spicy;
            return this;
        }

        public Builder note(String note) {
            this.note = note;
            return this;
        }

        public OrderItem build() {
            return new OrderItem(this);
        }
    }
}