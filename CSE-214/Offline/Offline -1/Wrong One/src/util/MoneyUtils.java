package util;

/**
 * Small formatting helpers for money values.
 */
public class MoneyUtils {
    public static String format(double amount) {
        return String.format("%.2f", amount);
    }
}

