package util;

/**
 * Console formatting helpers.
 */
public class TextUtils {
    public static String separator(int width) {
        StringBuilder line = new StringBuilder();
        for (int i = 0; i < width; i++) {
            line.append("-");
        }
        return line.toString();
    }
}
