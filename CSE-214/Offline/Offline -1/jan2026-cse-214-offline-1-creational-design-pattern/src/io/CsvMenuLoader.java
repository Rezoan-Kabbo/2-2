package io;

import model.MenuItem;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Loads menu items from a CSV file.
 */
public class CsvMenuLoader {
    public List<MenuItem> loadFromFile(String filePath) throws IOException {
        List<MenuItem> items = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            int lineNumber = 0;
            boolean firstLine = true;

            while ((line = reader.readLine()) != null) {
                lineNumber++;
                line = line.trim();
                if (line.isEmpty()) {
                    continue;
                }
                if (firstLine && line.toLowerCase().startsWith("code")) {
                    firstLine = false;
                    continue;
                }
                firstLine = false;
                items.add(parseLine(line, lineNumber));
            }
        }

        System.out.println("Loaded " + items.size() + " menu items from " + filePath);
        return items;
    }

    private MenuItem parseLine(String line, int lineNumber) {
        String[] parts = line.split(",", -1);
        if (parts.length < 4) {
            throw new IllegalArgumentException("Line " + lineNumber + " must contain code,name,category,price");
        }

        try {
            return new MenuItem(parts[0], parts[1], parts[2], Double.parseDouble(parts[3].trim()));
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Invalid price at line " + lineNumber + ": " + parts[3], e);
        }
    }
}

