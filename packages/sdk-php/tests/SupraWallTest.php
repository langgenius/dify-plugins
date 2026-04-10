<?php

use PHPUnit\Framework\TestCase;
use SupraWall\SupraWall;

class SupraWallTest extends TestCase {
    public function testEvaluateFailsWithoutApiKey() {
        $this->expectException(Exception::class);
        $this->expectExceptionMessage("SUPRAWALL_API_KEY is required");
        SupraWall::setApiKey("");
        SupraWall::evaluate("test-agent", "test-tool");
    }

    public function testTestModeApiKey() {
        SupraWall::setApiKey("ag_test_123");
        $result = SupraWall::evaluate("test-agent", "test-tool");
        $this->assertEquals("ALLOW", $result['decision']);
    }
}
