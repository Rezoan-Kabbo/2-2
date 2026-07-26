package service;

import model.MenuItem;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * In-memory menu catalog.
 */
public class MenuCatalog {
    private final Map<String, MenuItem> itemsByCode = new LinkedHashMap<>();

    public void addAll(List<MenuItem> menuItems) {
        clear();
        for (MenuItem item : menuItems) {
            itemsByCode.put(item.getCode().toUpperCase(), item);
        }
    }

    public MenuItem findByCode(String code) {
        if (code == null) {
            return null;
        }
        return itemsByCode.get(code.trim().toUpperCase());
    }

    public List<MenuItem> findAll() {
        return new ArrayList<>(itemsByCode.values());
    }

    public int count() {
        return itemsByCode.size();
    }

    public void clear() {
        itemsByCode.clear();
    }
}

