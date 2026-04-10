package io.suprawall;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class SupraWallTest {
    @Test
    public void testInitFailsWithoutKey() {
        SupraWall.setApiKey(null);
        assertThrows(IllegalArgumentException.class, () -> {
            SupraWall.evaluate("test", "tool", null);
        });
    }

    @Test
    public void testTestModeBypass() throws Exception {
        SupraWall.setApiKey("sw_test_123");
        SupraWall.EvaluateResponse res = SupraWall.evaluate("test", "tool", null);
        assertEquals("ALLOW", res.decision);
    }
}
