package model;

import java.util.Objects;

/**
 * Represents one item on the restaurant menu.
 */
public class MenuItem {
    private final String code;
    private final String name;
    private final String category;
    private final double basePrice;

    public MenuItem(String code, String name, String category, double basePrice) {
        this.code = requireNonBlank(code, "Code");
        this.name = requireNonBlank(name, "Name");
        this.category = requireNonBlank(category, "Category");
        if (basePrice < 0) {
            throw new IllegalArgumentException("Base price cannot be negative");
        }
        this.basePrice = basePrice;
    }

    public String getCode() {
        return code;
    }

    public String getName() {
        return name;
    }

    public String getCategory() {
        return category;
    }

    public double getBasePrice() {
        return basePrice;
    }

    private static String requireNonBlank(String value, String fieldName) {
        Objects.requireNonNull(value, fieldName + " cannot be null");
        String trimmed = value.trim();
        if (trimmed.isEmpty()) {
            throw new IllegalArgumentException(fieldName + " cannot be blank");
        }
        return trimmed;
    }

    @Override
    public String toString() {
        return String.format("%-4s %-20s %-10s %8.2f", code, name, category, basePrice);
    }
}

