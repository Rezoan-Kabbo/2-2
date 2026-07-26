package model;

/**
 * Portion sizes used for customizable food items.
 */
public enum Size {
    SMALL(0.85),
    MEDIUM(1.00),
    LARGE(1.35);

    private final double multiplier;

    Size(double multiplier) {
        this.multiplier = multiplier;
    }

    public double getMultiplier() {
        return multiplier;
    }
}

